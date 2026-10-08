"""Generate symbolic coboundary data for C(n+1) odd linear maps."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

from src.C_generators import ROOT, _coefficient


def build_coboundary_schema(n: int) -> dict:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    source_path = ROOT / "data" / f"C_{n}_structure.json"
    try:
        structure = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read Schema 1 source {source_path}: {exc}") from exc
    if structure.get("algebra", {}).get("n") != n:
        raise ValueError(f"Schema 1 source {source_path} has the wrong bosonic rank")

    even = structure["basis"]["even"]
    odd = structure["basis"]["odd"]
    labels = odd + even
    parity = structure["parity"]
    order = {label: index for index, label in enumerate(labels)}
    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        pair = (entry["X"], entry["Y"])
        brackets.setdefault(pair, {})[entry["Z"]] = Fraction(entry["coeff"])

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if (x, y) in brackets:
            return brackets[x, y]
        if (y, x) not in brackets:
            return {}
        sign = -1 if parity[x] * parity[y] == 0 else 1
        return {z: sign * coefficient for z, coefficient in brackets[y, x].items()}

    f_map: dict[str, list[tuple[str, str]]] = {}
    f_coefficients = []
    for source in labels:
        allowed_targets = even if parity[source] else odd
        for target in allowed_targets:
            symbol = f"phi_{order[target] + 1}_{order[source] + 1}"
            f_map.setdefault(source, []).append((target, symbol))
            f_coefficients.append({
                "input": source,
                "output": target,
                "symbol": symbol,
            })

    def delta_pair(x: str, y: str) -> dict[tuple[str, str], Fraction]:
        result: dict[tuple[str, str], Fraction] = {}
        first_sign = -1 if parity[x] else 1
        for target, symbol in f_map[y]:
            for output, coefficient in bracket(x, target).items():
                result[output, symbol] = (
                    result.get((output, symbol), Fraction(0))
                    + first_sign * coefficient
                )

        exponent = (parity[x] + 1) * parity[y]
        second_sign = 1 if exponent % 2 else -1
        for target, symbol in f_map[x]:
            for output, coefficient in bracket(y, target).items():
                result[output, symbol] = (
                    result.get((output, symbol), Fraction(0))
                    + second_sign * coefficient
                )

        for intermediate, coefficient in bracket(x, y).items():
            for output, symbol in f_map[intermediate]:
                result[output, symbol] = (
                    result.get((output, symbol), Fraction(0))
                    - coefficient
                )
        return {key: coefficient for key, coefficient in result.items() if coefficient}

    for x in labels:
        for y in labels:
            xy = delta_pair(x, y)
            yx = delta_pair(y, x)
            sign = -1 if parity[x] * parity[y] == 0 else 1
            expected = {(output, symbol): sign * value for (output, symbol), value in xy.items()}
            if yx != expected:
                raise ValueError(f"coboundary fails graded skew-symmetry for ({x}, {y})")

    coboundary_coefficients = []
    for x_index, x in enumerate(labels):
        for y in labels[x_index:]:
            for (output, symbol), coefficient in sorted(delta_pair(x, y).items()):
                coboundary_coefficients.append({
                    "X": x,
                    "Y": y,
                    "Z": output,
                    "phi": symbol,
                    "coeff": _coefficient(coefficient),
                })

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_structure_schema": source_path.name,
        "coboundary_operator": {
            "map_parity": 1,
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "basis_order": labels,
            "f_coefficients": f_coefficients,
        },
        "coboundary_coefficients": coboundary_coefficients,
        "metadata": {
            "generated_by": "src/C_coboundary_generator.py",
            "generation_date": date.today().isoformat(),
            "references": [
                source_path.name,
                "docs/math/C_coboundary_definition.md",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.ranks:
        schema = build_coboundary_schema(n)
        path = args.output_dir / f"C_{n}_coboundary.json"
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


if __name__ == "__main__":
    main()
