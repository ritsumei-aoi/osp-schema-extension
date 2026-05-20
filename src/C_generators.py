from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date
from fractions import Fraction
from pathlib import Path

Word = tuple[str, ...]
Expression = dict[Word, Fraction]

ORDERING_CONVENTION = "PBW: κ < [odd] < [even]  (K = 1 is excluded; see central_elements)"
SCHEMA_TOP_LEVEL_KEYS = (
    "schema_version",
    "algebra",
    "oscillator_generators",
    "oscillator_relations",
    "central_elements",
    "basis",
    "parity",
    "generator_realization",
    "structure_constants",
    "metadata",
)

_SCHEMA_CACHE: dict[int, dict] = {}
_STRUCTURE_CONSTANTS_CACHE: dict[int, list[dict[str, str]]] = {}
_BRACKET_CACHE: dict[tuple[int, str, str], dict[str, Fraction]] = {}


def fraction_to_str(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def clone_expression(expr: Expression) -> Expression:
    return dict(expr)


def clean_expression(expr: Expression) -> Expression:
    return {word: coeff for word, coeff in expr.items() if coeff}


def add_scaled_expression(target: Expression, expr: Expression, scale: Fraction) -> None:
    for word, coeff in expr.items():
        new_coeff = target.get(word, Fraction(0)) + coeff * scale
        if new_coeff:
            target[word] = new_coeff
        elif word in target:
            del target[word]


def is_fermion(label: str) -> bool:
    return label in {"a_1_p", "a_1_m"}


def is_boson(label: str) -> bool:
    return label.startswith("b_")


def parse_boson(label: str) -> tuple[int, str]:
    _, index, sign = label.split("_")
    return int(index), sign


def oscillator_sort_key(label: str) -> tuple[int, int, int]:
    if label == "a_1_p":
        return (0, 1, 0)
    if label == "a_1_m":
        return (0, 2, 0)
    index, sign = parse_boson(label)
    return (1, index, 0 if sign == "p" else 1)


def normalize_word(word: Word) -> Expression:
    if len(word) < 2:
        return {word: Fraction(1)}

    for index in range(len(word) - 1):
        left = word[index]
        right = word[index + 1]
        prefix = word[:index]
        suffix = word[index + 2 :]

        if left == right and is_fermion(left):
            return {}

        if left == "a_1_m" and right == "a_1_p":
            result: Expression = {}
            add_scaled_expression(result, normalize_word(prefix + suffix), Fraction(1))
            add_scaled_expression(
                result,
                normalize_word(prefix + ("a_1_p", "a_1_m") + suffix),
                Fraction(-1),
            )
            return clean_expression(result)

        if is_boson(left) and is_boson(right):
            left_index, left_sign = parse_boson(left)
            right_index, right_sign = parse_boson(right)
            if left_sign == "m" and right_sign == "p" and left_index == right_index:
                result = {}
                add_scaled_expression(result, normalize_word(prefix + suffix), Fraction(1))
                add_scaled_expression(
                    result,
                    normalize_word(prefix + (right, left) + suffix),
                    Fraction(1),
                )
                return clean_expression(result)

        if oscillator_sort_key(left) > oscillator_sort_key(right):
            return normalize_word(prefix + (right, left) + suffix)

    return {word: Fraction(1)}


def multiply_words(left: Word, right: Word) -> Expression:
    return normalize_word(left + right)


def multiply_expressions(left: Expression, right: Expression) -> Expression:
    result: Expression = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            add_scaled_expression(
                result,
                multiply_words(left_word, right_word),
                left_coeff * right_coeff,
            )
    return clean_expression(result)


def graded_bracket(left: Expression, right: Expression, parity_left: int, parity_right: int) -> Expression:
    result = multiply_expressions(left, right)
    reverse = multiply_expressions(right, left)
    sign = Fraction(-1 if (parity_left * parity_right) % 2 else 1)
    add_scaled_expression(result, reverse, -sign)
    return clean_expression(result)


def build_even_basis(n: int) -> list[str]:
    basis = [f"H_{index}" for index in range(1, n + 2)]
    basis.extend(f"E_2del{index}_p" for index in range(1, n + 1))
    basis.extend(
        f"E_del{i}_del{j}_pp"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    )
    basis.extend(
        f"E_del{i}_del{j}_pm"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    )
    basis.extend(f"E_2del{index}_m" for index in range(1, n + 1))
    basis.extend(
        f"E_del{i}_del{j}_mm"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    )
    basis.extend(
        f"E_del{i}_del{j}_mp"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    )
    return basis


def build_odd_basis(n: int) -> list[str]:
    basis: list[str] = []
    for suffix in ("pp", "pm", "mp", "mm"):
        basis.extend(f"E_eps1_del{index}_{suffix}" for index in range(1, n + 1))
    return basis


def build_basis(n: int) -> dict[str, object]:
    return {
        "even": build_even_basis(n),
        "odd": build_odd_basis(n),
        "ordering_convention": ORDERING_CONVENTION,
    }


def build_basis_order(n: int) -> list[str]:
    basis = build_basis(n)
    return list(basis["odd"]) + list(basis["even"])


def build_parity_map(n: int) -> dict[str, int]:
    parity = {name: 0 for name in build_even_basis(n)}
    parity.update({name: 1 for name in build_odd_basis(n)})
    return parity


def build_algebra_metadata(n: int) -> dict[str, object]:
    return {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n + 1})",
        "alternative_notation": {
            "osp": f"osp(2|{2 * n})",
            "dimension_formula": "osp(2m|2n) with m=1",
        },
        "dimension": {
            "total": 2 * n * n + 5 * n + 1,
            "even": 2 * n * n + n + 1,
            "odd": 4 * n,
        },
    }


def build_oscillator_generators(n: int) -> dict[str, object]:
    labels = []
    for index in range(1, n + 1):
        labels.extend([f"b_{index}_p", f"b_{index}_m"])
    return {
        "standard_fermion": {
            "count": 2,
            "labels": ["a_1_p", "a_1_m"],
            "parity": 1,
            "relation": "{a_1_m, a_1_p} = 1",
            "description": "Standard fermionic pair a_1^± with canonical anticommutation relations.",
        },
        "bosons": {
            "count": 2 * n,
            "n": n,
            "labels": labels,
            "description": "Bosonic oscillators b_i^± with i=1,...,n",
        },
    }


def build_oscillator_relations() -> dict[str, object]:
    return {
        "standard_fermion_anticommutators": {
            "description": "Canonical anticommutation relations for the standard fermionic pair",
            "relations": {
                "same_type": "{a_1^+, a_1^+} = 0 and {a_1^-, a_1^-} = 0",
                "conjugate_pair": "{a_1^-, a_1^+} = 1",
            },
        },
        "bosonic_commutators": {
            "description": "Canonical commutation relations for bosonic oscillators",
            "relations": {
                "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
            },
        },
        "mixed_commutators": {
            "boson_fermion": "[b_i^s, a_1^t] = 0 for all i and s,t in {+,-}",
        },
    }


def build_central_elements() -> dict[str, object]:
    return {
        "kappa": {
            "parity": 0,
            "relation": "kappa^2 = 0",
            "description": "Formal central symbol for the nilpotent extension; recorded explicitly in the schema and excluded from basis lists.",
        },
        "K": {
            "parity": 0,
            "relation": "K = 1",
            "description": "Central identity element; recorded for completeness and excluded from basis lists.",
        },
    }


def number_word(label: str) -> Word:
    return (label.replace("_m", "_p"), label)


def build_generator_expressions(n: int) -> dict[str, Expression]:
    expressions: dict[str, Expression] = {
        "H_1": {
            ("a_1_p", "a_1_m"): Fraction(1),
            ("b_1_p", "b_1_m"): Fraction(1),
        }
    }

    for index in range(2, n + 1):
        expressions[f"H_{index}"] = {
            (f"b_{index - 1}_p", f"b_{index - 1}_m"): Fraction(1),
            (f"b_{index}_p", f"b_{index}_m"): Fraction(-1),
        }

    expressions[f"H_{n + 1}"] = {
        (f"b_{n}_p", f"b_{n}_m"): Fraction(-1),
        (): Fraction(-1, 2),
    }

    for index in range(1, n + 1):
        expressions[f"E_2del{index}_p"] = {(f"b_{index}_p", f"b_{index}_p"): Fraction(1)}
        expressions[f"E_2del{index}_m"] = {(f"b_{index}_m", f"b_{index}_m"): Fraction(1)}
        expressions[f"E_eps1_del{index}_pp"] = {("a_1_p", f"b_{index}_p"): Fraction(1)}
        expressions[f"E_eps1_del{index}_pm"] = {("a_1_p", f"b_{index}_m"): Fraction(1)}
        expressions[f"E_eps1_del{index}_mp"] = {("a_1_m", f"b_{index}_p"): Fraction(1)}
        expressions[f"E_eps1_del{index}_mm"] = {("a_1_m", f"b_{index}_m"): Fraction(1)}

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            expressions[f"E_del{i}_del{j}_pp"] = {(f"b_{i}_p", f"b_{j}_p"): Fraction(1)}
            expressions[f"E_del{i}_del{j}_pm"] = {(f"b_{i}_p", f"b_{j}_m"): Fraction(1)}
            expressions[f"E_del{i}_del{j}_mm"] = {(f"b_{i}_m", f"b_{j}_m"): Fraction(1)}
            expressions[f"E_del{i}_del{j}_mp"] = {(f"b_{i}_m", f"b_{j}_p"): Fraction(1)}

    return {name: clean_expression(expr) for name, expr in expressions.items()}


def generator_to_frappat_form(name: str, n: int) -> str:
    if name == "H_1":
        return "a_1^+ a_1^- + b_1^+ b_1^-"

    if name.startswith("H_"):
        index = int(name.split("_")[1])
        if index == n + 1:
            return f"-b_{n}^+ b_{n}^- - 1/2"
        return f"b_{index - 1}^+ b_{index - 1}^- - b_{index}^+ b_{index}^-"

    if name.startswith("E_2del"):
        body = name[len("E_2del") :]
        index, sign = body.split("_")
        return f"(b_{index}^{'+' if sign == 'p' else '-'})^2"

    if name.startswith("E_eps1_del"):
        body = name[len("E_eps1_del") :]
        index, suffix = body.split("_")
        fermion = "+" if suffix[0] == "p" else "-"
        boson = "+" if suffix[1] == "p" else "-"
        return f"a_1^{fermion} b_{index}^{boson}"

    if name.startswith("E_del"):
        body = name[len("E_del") :]
        left, right, suffix = body.split("_")
        left_sign = "+" if suffix[0] == "p" else "-"
        right_sign = "+" if suffix[1] == "p" else "-"
        return f"b_{left}^{left_sign} b_{right}^{right_sign}"

    raise ValueError(f"Unknown generator name: {name}")


def expression_to_standard_form(expr: Expression) -> list[dict[str, object]]:
    items = sorted(expr.items(), key=lambda item: (len(item[0]), item[0]))
    return [{"words": list(word), "coeff": fraction_to_str(coeff)} for word, coeff in items]


def build_generator_realizations(n: int, expressions: dict[str, Expression], parity_map: dict[str, int]) -> dict[str, object]:
    realizations = {}
    for name in build_basis_order(n):
        payload = {
            "standard_form": expression_to_standard_form(expressions[name]),
            "frappat_form": generator_to_frappat_form(name, n),
            "parity": parity_map[name],
        }
        if name == f"H_{n + 1}":
            payload["note"] = "Terminal Cartan; includes the constant term -1/2."
        realizations[name] = payload

    return {
        "description": "Standard form with PBW ordering",
        "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
        "realizations": realizations,
    }


def gaussian_solve(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    size = len(vector)
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]

    for column in range(size):
        pivot = None
        for row in range(column, size):
            if augmented[row][column]:
                pivot = row
                break
        if pivot is None:
            raise ValueError("Singular linear system in Cartan decomposition")
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]

        pivot_value = augmented[column][column]
        for index in range(column, size + 1):
            augmented[column][index] /= pivot_value

        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            factor = augmented[row][column]
            for index in range(column, size + 1):
                augmented[row][index] -= factor * augmented[column][index]

    return [augmented[row][size] for row in range(size)]


def build_direct_word_map(expressions: dict[str, Expression]) -> dict[Word, str]:
    mapping: dict[Word, str] = {}
    for name, expr in expressions.items():
        if name.startswith("H_"):
            continue
        if len(expr) == 1:
            word = next(iter(expr))
            mapping[word] = name
    return mapping


def cartan_number_words(n: int) -> list[Word]:
    return [("a_1_p", "a_1_m")] + [(f"b_{index}_p", f"b_{index}_m") for index in range(1, n + 1)]


def decompose_cartan_expression(n: int, expr: Expression, cartan_expressions: list[Expression]) -> dict[str, Fraction]:
    rows = cartan_number_words(n)
    matrix: list[list[Fraction]] = []
    vector: list[Fraction] = []
    for row_word in rows:
        matrix.append([cartan_expr.get(row_word, Fraction(0)) for cartan_expr in cartan_expressions])
        vector.append(expr.get(row_word, Fraction(0)))

    coefficients = gaussian_solve(matrix, vector)
    names = [f"H_{index}" for index in range(1, n + 2)]
    result = {name: coeff for name, coeff in zip(names, coefficients) if coeff}

    reconstructed: Expression = {}
    for name, coeff in result.items():
        add_scaled_expression(reconstructed, build_generator_expressions(n)[name], coeff)

    if clean_expression(reconstructed) != clean_expression(expr):
        raise ValueError(
            f"Cartan decomposition mismatch for n={n}: expected {expr}, reconstructed {reconstructed}"
        )

    return result


def decompose_expression_to_basis(n: int, expr: Expression) -> dict[str, Fraction]:
    expressions = build_generator_expressions(n)
    direct_word_map = build_direct_word_map(expressions)
    cartan_names = [f"H_{index}" for index in range(1, n + 2)]
    cartan_expressions = [expressions[name] for name in cartan_names]

    direct_coefficients: dict[str, Fraction] = {}
    cartan_expr: Expression = {}

    for word, coeff in clean_expression(expr).items():
        if word in direct_word_map:
            name = direct_word_map[word]
            direct_coefficients[name] = direct_coefficients.get(name, Fraction(0)) + coeff
            continue

        if word == () or word in cartan_number_words(n):
            cartan_expr[word] = cartan_expr.get(word, Fraction(0)) + coeff
            continue

        raise ValueError(f"Expression term {word} is outside the approved basis span for n={n}")

    result = {name: coeff for name, coeff in direct_coefficients.items() if coeff}
    if clean_expression(cartan_expr):
        result.update(decompose_cartan_expression(n, cartan_expr, cartan_expressions))

    return {name: coeff for name, coeff in result.items() if coeff}


def bracket_in_basis(n: int, left_name: str, right_name: str) -> dict[str, Fraction]:
    cache_key = (n, left_name, right_name)
    if cache_key in _BRACKET_CACHE:
        return dict(_BRACKET_CACHE[cache_key])

    expressions = build_generator_expressions(n)
    parity_map = build_parity_map(n)
    bracket_expr = graded_bracket(
        expressions[left_name],
        expressions[right_name],
        parity_map[left_name],
        parity_map[right_name],
    )
    coefficients = decompose_expression_to_basis(n, bracket_expr)
    _BRACKET_CACHE[cache_key] = dict(coefficients)
    return dict(coefficients)


def build_structure_constants(n: int) -> list[dict[str, str]]:
    if n in _STRUCTURE_CONSTANTS_CACHE:
        return deepcopy(_STRUCTURE_CONSTANTS_CACHE[n])

    structure_constants: list[dict[str, str]] = []
    basis_order = build_basis_order(n)
    for left_name in basis_order:
        for right_name in basis_order:
            coefficients = bracket_in_basis(n, left_name, right_name)
            for result_name in basis_order:
                coeff = coefficients.get(result_name)
                if not coeff:
                    continue
                structure_constants.append(
                    {
                        "X": left_name,
                        "Y": right_name,
                        "Z": result_name,
                        "coeff": fraction_to_str(coeff),
                        "sign_rule": "graded",
                    }
                )

    _STRUCTURE_CONSTANTS_CACHE[n] = deepcopy(structure_constants)
    return structure_constants


def build_metadata() -> dict[str, object]:
    return {
        "generated_by": "src/C_generators.py",
        "generation_date": date.today().isoformat(),
        "references": [
            "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
            "Bakalov and Sullivan (2017)",
        ],
    }


def build_structure_schema(n: int) -> dict[str, object]:
    if n in _SCHEMA_CACHE:
        return deepcopy(_SCHEMA_CACHE[n])

    expressions = build_generator_expressions(n)
    parity_map = build_parity_map(n)
    schema = {
        "schema_version": "5.0",
        "algebra": build_algebra_metadata(n),
        "oscillator_generators": build_oscillator_generators(n),
        "oscillator_relations": build_oscillator_relations(),
        "central_elements": build_central_elements(),
        "basis": build_basis(n),
        "parity": parity_map,
        "generator_realization": build_generator_realizations(n, expressions, parity_map),
        "structure_constants": build_structure_constants(n),
        "metadata": build_metadata(),
    }
    _SCHEMA_CACHE[n] = deepcopy(schema)
    return schema


def write_structure_json(n: int, out_path: Path) -> Path:
    schema = build_structure_schema(n)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def default_output_path(n: int, outdir: Path) -> Path:
    return outdir / f"C_{n}_structure.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate C(n+1) Schema 1 JSON files.")
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
            path = write_structure_json(n, default_output_path(n, args.outdir))
            print(f"Wrote {path}")
        return

    out_path = args.out or default_output_path(args.n, args.outdir)
    path = write_structure_json(args.n, out_path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
