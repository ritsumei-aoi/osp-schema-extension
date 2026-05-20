from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

import C_gamma as cgamma
import C_generators as cg

SparseVector = dict[int, Fraction]

_COBOUNDARY_SCHEMA_CACHE: dict[tuple[int, str], dict[str, Any]] = {}
_COLUMN_DATA_CACHE: dict[int, dict[str, Any]] = {}


def coboundary_path(n: int, profile_name: str, data_dir: Path | None = None) -> Path:
    base = data_dir or Path("data")
    return base / f"C_{n}_coboundary_{profile_name}.json"


def build_profile_assignments(n: int, profile_name: str) -> dict[str, Any]:
    if profile_name != "gb_one":
        raise ValueError(f"Unsupported coboundary verification profile: {profile_name}")

    gb_values = {label: Fraction(1) for label in cgamma.gb_labels_in_order(n)}
    return {
        "name": profile_name,
        "assignment_type": "explicit",
        "description": "All gb deformation parameters are set to 1.",
        "gb_values": gb_values,
    }


def serialize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": profile["name"],
        "assignment_type": profile["assignment_type"],
        "description": profile["description"],
        "gb_values": {
            label: cg.fraction_to_str(value) for label, value in profile["gb_values"].items()
        },
    }


def basis_order(n: int) -> list[str]:
    return cg.build_basis_order(n)


def target_order(n: int) -> list[str]:
    return basis_order(n) + ["K"]


def row_index(
    left_index: int,
    right_index: int,
    target_index: int,
    basis_count: int,
    target_count: int,
) -> int:
    return (left_index * basis_count + right_index) * target_count + target_index


def add_scaled_sparse_vector(target: SparseVector, source: SparseVector, scale: Fraction) -> None:
    for index, coeff in source.items():
        new_coeff = target.get(index, Fraction(0)) + coeff * scale
        if new_coeff:
            target[index] = new_coeff
        elif index in target:
            del target[index]


def scale_sparse_vector(vector: SparseVector, scale: Fraction) -> SparseVector:
    if not scale:
        return {}
    return {index: coeff * scale for index, coeff in vector.items() if coeff * scale}


def reduce_sparse_vector(vector: SparseVector, basis_vectors: dict[int, SparseVector]) -> SparseVector:
    reduced = dict(vector)
    while reduced:
        pivot = min(reduced)
        if pivot not in basis_vectors:
            break
        factor = reduced[pivot]
        add_scaled_sparse_vector(reduced, basis_vectors[pivot], -factor)
    return reduced


def add_vector_to_basis(vector: SparseVector, basis_vectors: dict[int, SparseVector]) -> bool:
    reduced = reduce_sparse_vector(vector, basis_vectors)
    if not reduced:
        return False

    pivot = min(reduced)
    pivot_coeff = reduced[pivot]
    normalized = {index: coeff / pivot_coeff for index, coeff in reduced.items()}
    basis_vectors[pivot] = normalized
    return True


def build_column_data(n: int) -> dict[str, Any]:
    if n in _COLUMN_DATA_CACHE:
        return _COLUMN_DATA_CACHE[n]

    ordered_basis = basis_order(n)
    parity = cg.build_parity_map(n)
    basis_index = {name: index for index, name in enumerate(ordered_basis)}
    target_names = target_order(n)
    target_index_map = {name: index for index, name in enumerate(target_names)}

    brackets_to_target = {
        target: {name: cg.bracket_in_basis(n, name, target) for name in ordered_basis}
        for target in ordered_basis
    }
    bracket_occurrences: dict[str, list[tuple[int, int, Fraction]]] = {
        source: [] for source in ordered_basis
    }
    for left_index, left in enumerate(ordered_basis):
        for right_index, right in enumerate(ordered_basis):
            bracket = cg.bracket_in_basis(n, left, right)
            for source, coeff in bracket.items():
                bracket_occurrences[source].append((left_index, right_index, coeff))

    parameters: list[dict[str, str]] = []
    even_basis = list(cg.build_basis(n)["even"])
    odd_basis = list(cg.build_basis(n)["odd"])
    for source in even_basis:
        for target in odd_basis:
            parameters.append(
                {
                    "parameter": f"phi_{target}_from_{source}",
                    "source": source,
                    "target": target,
                }
            )
    for source in odd_basis:
        for target in even_basis:
            parameters.append(
                {
                    "parameter": f"phi_{target}_from_{source}",
                    "source": source,
                    "target": target,
                }
            )

    data = {
        "basis_order": ordered_basis,
        "basis_index": basis_index,
        "target_order": target_names,
        "target_index": target_index_map,
        "parity": parity,
        "brackets_to_target": brackets_to_target,
        "bracket_occurrences": bracket_occurrences,
        "parameters": parameters,
    }
    _COLUMN_DATA_CACHE[n] = data
    return data


def build_basis_map_column(n: int, source: str, target: str) -> SparseVector:
    data = build_column_data(n)
    ordered_basis = data["basis_order"]
    parity = data["parity"]
    basis_count = len(ordered_basis)
    target_count = len(data["target_order"])
    source_index = data["basis_index"][source]
    target_basis_index = data["target_index"][target]

    vector: SparseVector = {}

    # First term: (-1)^{p(X)} [X, f(Y)] when Y = source.
    for left_index, left in enumerate(ordered_basis):
        sign = Fraction(-1 if parity[left] else 1)
        for result, coeff in data["brackets_to_target"][target][left].items():
            index = row_index(
                left_index,
                source_index,
                data["target_index"][result],
                basis_count,
                target_count,
            )
            vector[index] = vector.get(index, Fraction(0)) + sign * coeff
            if not vector[index]:
                del vector[index]

    # Second term: -(-1)^{(p(source)+1)p(Y)} [Y, f(X)] when X = source.
    for right_index, right in enumerate(ordered_basis):
        exponent = (parity[source] + 1) * parity[right]
        sign = Fraction(1 if exponent % 2 else -1)
        for result, coeff in data["brackets_to_target"][target][right].items():
            index = row_index(
                source_index,
                right_index,
                data["target_index"][result],
                basis_count,
                target_count,
            )
            vector[index] = vector.get(index, Fraction(0)) + sign * coeff
            if not vector[index]:
                del vector[index]

    # Third term: -f([X, Y]).
    for left_index, right_index, coeff in data["bracket_occurrences"][source]:
        index = row_index(left_index, right_index, target_basis_index, basis_count, target_count)
        vector[index] = vector.get(index, Fraction(0)) - coeff
        if not vector[index]:
            del vector[index]

    return vector


def build_coboundary_columns(n: int) -> list[dict[str, Any]]:
    data = build_column_data(n)
    columns: list[dict[str, Any]] = []
    for parameter in data["parameters"]:
        vector = build_basis_map_column(n, parameter["source"], parameter["target"])
        columns.append(
            {
                "parameter": parameter["parameter"],
                "source": parameter["source"],
                "target": parameter["target"],
                "vector": vector,
            }
        )
    return columns


def evaluate_linear_coefficient(coefficients: dict[str, str], gb_values: dict[str, Fraction]) -> Fraction:
    total = Fraction(0)
    for label, coeff in coefficients.items():
        total += Fraction(coeff) * gb_values[label]
    return total


def evaluate_gamma_profile(n: int, profile_name: str, data_dir: Path | None = None) -> list[dict[str, Any]]:
    gamma_schema = json.loads(cgamma.gamma_path(n, data_dir).read_text(encoding="utf-8"))
    profile = build_profile_assignments(n, profile_name)
    entries: list[dict[str, Any]] = []
    for entry in gamma_schema["inhomogeneous_deformation"]["gamma_matrix"]:
        value = evaluate_linear_coefficient(entry["coeff"], profile["gb_values"])
        if not value:
            continue
        entries.append(
            {
                "X": entry["X"],
                "Y": entry["Y"],
                "Z": entry["Z"],
                "coeff": cg.fraction_to_str(value),
                "sign_rule": entry["sign_rule"],
            }
        )
    return entries


def gamma_entries_to_vector(n: int, entries: list[dict[str, Any]]) -> SparseVector:
    data = build_column_data(n)
    basis_count = len(data["basis_order"])
    target_count = len(data["target_order"])
    vector: SparseVector = {}
    for entry in entries:
        index = row_index(
            data["basis_index"][entry["X"]],
            data["basis_index"][entry["Y"]],
            data["target_index"][entry["Z"]],
            basis_count,
            target_count,
        )
        value = Fraction(entry["coeff"])
        vector[index] = vector.get(index, Fraction(0)) + value
        if not vector[index]:
            del vector[index]
    return vector


def project_vector_to_basis_rows(n: int, vector: SparseVector) -> SparseVector:
    data = build_column_data(n)
    basis_target_limit = len(data["basis_order"])
    target_count = len(data["target_order"])
    projected: SparseVector = {}
    for index, coeff in vector.items():
        target_slot = index % target_count
        if target_slot < basis_target_limit:
            projected[index] = coeff
    return projected


def partition_gamma_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    basis_entries = [entry for entry in entries if entry["Z"] != "K"]
    k_entries = [entry for entry in entries if entry["Z"] == "K"]
    return {
        "basis_entries": basis_entries,
        "k_entries": k_entries,
    }


def vector_to_coboundary_entries(n: int, vector: SparseVector, parameter: str, source: str, target: str) -> list[dict[str, Any]]:
    data = build_column_data(n)
    basis_count = len(data["basis_order"])
    target_names = data["target_order"]
    entries: list[dict[str, Any]] = []
    for index in sorted(vector):
        left_slot, remainder = divmod(index, basis_count * len(target_names))
        right_slot, target_slot = divmod(remainder, len(target_names))
        result_name = target_names[target_slot]
        if result_name == "K":
            continue
        entries.append(
            {
                "parameter": parameter,
                "source": source,
                "target": target,
                "X": data["basis_order"][left_slot],
                "Y": data["basis_order"][right_slot],
                "Z": result_name,
                "coeff": cg.fraction_to_str(vector[index]),
                "sign_rule": "graded",
            }
        )
    return entries


def verify_rank_condition(n: int, profile_name: str, data_dir: Path | None = None) -> dict[str, Any]:
    columns = build_coboundary_columns(n)
    basis_vectors: dict[int, SparseVector] = {}
    for column in columns:
        add_vector_to_basis(column["vector"], basis_vectors)

    gamma_entries = evaluate_gamma_profile(n, profile_name, data_dir)
    gamma_vector = gamma_entries_to_vector(n, gamma_entries)
    gamma_basis_vector = project_vector_to_basis_rows(n, gamma_vector)
    residual_basis = reduce_sparse_vector(gamma_basis_vector, basis_vectors)
    residual_full = reduce_sparse_vector(gamma_vector, basis_vectors)

    gamma_partition = partition_gamma_entries(gamma_entries)
    operator_rank = len(basis_vectors)
    augmented_rank = operator_rank + (1 if residual_full else 0)
    basis_augmented_rank = operator_rank + (1 if residual_basis else 0)
    k_component_nonzero = bool(gamma_partition["k_entries"])
    basis_component_in_image = not residual_basis

    if k_component_nonzero and basis_component_in_image:
        obstruction_source = "K-only"
    elif k_component_nonzero and not basis_component_in_image:
        obstruction_source = "K-and-basis"
    elif basis_component_in_image:
        obstruction_source = "none"
    else:
        obstruction_source = "basis-only"

    is_trivial = augmented_rank == operator_rank
    classification = "Trivial" if is_trivial else "Non-trivial"
    if is_trivial:
        statement = (
            f"For n={n} and profile {profile_name}, the evaluated deformation lies in the coboundary image."
        )
        witness = "A coboundary witness exists within the computed parity-reversing ansatz."
    else:
        statement = (
            f"For n={n} and profile {profile_name}, the evaluated deformation does not lie in the coboundary image."
        )
        if obstruction_source == "K-only":
            witness = "Non-trivial because the evaluated cocycle has nonzero K-components while every coboundary is g-valued."
        elif obstruction_source == "K-and-basis":
            witness = "Non-trivial because both K-components and basis components remain outside the coboundary image."
        else:
            witness = "Non-trivial because the basis-valued part of the cocycle remains outside the coboundary image."

    return {
        "columns": columns,
        "gamma_entries": gamma_entries,
        "operator_rank": operator_rank,
        "augmented_rank": augmented_rank,
        "basis_augmented_rank": basis_augmented_rank,
        "gamma_nonzero_count": len(gamma_entries),
        "gamma_basis_nonzero_count": len(gamma_partition["basis_entries"]),
        "gamma_k_nonzero_count": len(gamma_partition["k_entries"]),
        "k_component_nonzero": k_component_nonzero,
        "basis_component_in_image": basis_component_in_image,
        "is_trivial": is_trivial,
        "classification": classification,
        "statement": statement,
        "witness": witness,
        "obstruction_source": obstruction_source,
    }


def build_coboundary_map_summary(n: int, verification: dict[str, Any]) -> dict[str, Any]:
    data = build_column_data(n)
    return {
        "type": "odd parity-reversing linear map",
        "configuration": "full_basis_linear",
        "parameter_count": len(data["parameters"]),
        "parameters": [
            {
                "parameter": parameter["parameter"],
                "source": parameter["source"],
                "target": parameter["target"],
            }
            for parameter in data["parameters"]
        ],
        "coboundary_coefficients": [
            entry
            for column in verification["columns"]
            for entry in vector_to_coboundary_entries(
                n,
                column["vector"],
                column["parameter"],
                column["source"],
                column["target"],
            )
        ],
    }


def build_rank_verification_summary(verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "operator_rank": verification["operator_rank"],
        "augmented_rank": verification["augmented_rank"],
        "basis_augmented_rank": verification["basis_augmented_rank"],
        "target_nonzero_count": verification["gamma_nonzero_count"],
        "target_basis_nonzero_count": verification["gamma_basis_nonzero_count"],
        "target_k_nonzero_count": verification["gamma_k_nonzero_count"],
        "k_component_nonzero": verification["k_component_nonzero"],
        "basis_component_in_image": verification["basis_component_in_image"],
        "is_trivial": verification["is_trivial"],
        "obstruction_source": verification["obstruction_source"],
    }


def build_conclusion_summary(verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": verification["classification"],
        "statement": verification["statement"],
        "witness": verification["witness"],
        "obstruction_source": verification["obstruction_source"],
    }


def build_metadata(n: int, profile_name: str) -> dict[str, Any]:
    return {
        "generated_by": "src/C_coboundary.py",
        "generation_date": date.today().isoformat(),
        "references": [
            "docs/math/C_coboundary_definition.md",
            "docs/math/C_inhomogeneous_definition.md",
            f"data/C_{n}_structure.json",
            f"data/C_{n}_gamma.json",
        ],
        "profile_name": profile_name,
        "structure_file": f"C_{n}_structure.json",
        "gamma_file": f"C_{n}_gamma.json",
    }


def build_coboundary_schema(
    n: int,
    profile_name: str = "gb_one",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    cache_key = (n, profile_name)
    if data_dir is None and cache_key in _COBOUNDARY_SCHEMA_CACHE:
        return deepcopy(_COBOUNDARY_SCHEMA_CACHE[cache_key])

    structure_schema = cgamma.load_structure_schema(n, data_dir)
    profile = build_profile_assignments(n, profile_name)
    verification = verify_rank_condition(n, profile_name, data_dir)
    schema = {
        "schema_version": "5.0",
        "algebra": structure_schema["algebra"],
        "basis": structure_schema["basis"],
        "parity": structure_schema["parity"],
        "central_elements": structure_schema["central_elements"],
        "evaluation_profile": serialize_profile(profile),
        "coboundary_map": build_coboundary_map_summary(n, verification),
        "target_cocycle": verification["gamma_entries"],
        "rank_verification": build_rank_verification_summary(verification),
        "conclusion": build_conclusion_summary(verification),
        "metadata": build_metadata(n, profile_name),
    }

    if data_dir is None:
        _COBOUNDARY_SCHEMA_CACHE[cache_key] = deepcopy(schema)
    return deepcopy(schema)


def write_coboundary_json(
    n: int,
    profile_name: str,
    out_path: Path,
    data_dir: Path | None = None,
) -> Path:
    schema = build_coboundary_schema(n, profile_name, data_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate C(n+1) Schema 4 coboundary JSON files.")
    parser.add_argument("--profile", choices=("gb_one",), required=True, help="Approved gb verification profile")
    parser.add_argument("--n", type=int, choices=(1, 2, 3), help="Bosonic rank n to generate")
    parser.add_argument("--all", action="store_true", help="Generate n=1,2,3")
    parser.add_argument("--out", type=Path, help="Output file path for a single n run")
    parser.add_argument("--outdir", type=Path, default=Path("data"), help="Output directory for --all")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.all == bool(args.n):
        raise SystemExit("Specify exactly one of --n or --all")

    if args.all:
        for n in (1, 2, 3):
            path = write_coboundary_json(n, args.profile, coboundary_path(n, args.profile, args.outdir))
            print(f"Wrote {path}")
        return

    out_path = args.out or coboundary_path(args.n, args.profile, args.outdir)
    path = write_coboundary_json(args.n, args.profile, out_path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
