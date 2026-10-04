#!/usr/bin/env python3
"""Check whether a supplied rational-valued 2-cochain is delta f for odd f."""

import argparse
import json
import sys
from fractions import Fraction
from itertools import product


def coefficient(value):
    if isinstance(value, bool):
        raise ValueError("Boolean values are not rational coefficients")
    return Fraction(str(value))


def read_cochain(entries, basis, label):
    names = {item["name"] for item in basis}
    result = {}
    for entry in entries:
        x, y = entry["x"], entry["y"]
        if x not in names or y not in names:
            raise ValueError(f"{label} entry references an unknown basis name")
        key = (x, y)
        if key in result:
            raise ValueError(f"duplicate {label} entry for {x}, {y}")
        terms = {}
        for name, value in entry.get("terms", {}).items():
            if name not in names:
                raise ValueError(f"{label} entry references unknown output {name}")
            parsed = coefficient(value)
            if parsed:
                terms[name] = parsed
        result[key] = terms
    return result


def verify(data, check_documented_dimension=True):
    basis = data["basis"]
    if not basis:
        raise ValueError("basis must not be empty")
    names = [item["name"] for item in basis]
    if len(names) != len(set(names)):
        raise ValueError("basis names must be unique")
    for item in basis:
        if item.get("parity") not in (0, 1):
            raise ValueError(f"invalid parity for {item['name']}; expected 0 or 1")

    if check_documented_dimension:
        n = data.get("n")
        if n not in (1, 2, 3):
            raise ValueError("n must be 1, 2, or 3")
        expected = (2 * n * n + n + 1, 4 * n)
        actual = (
            sum(item["parity"] == 0 for item in basis),
            sum(item["parity"] == 1 for item in basis),
        )
        if actual != expected:
            raise ValueError(
                f"basis parity dimensions {actual} do not match n={n}: {expected}"
            )

    bracket = read_cochain(data["bracket"], basis, "bracket")
    gamma = read_cochain(data["gamma"], basis, "gamma")
    parity = {item["name"]: item["parity"] for item in basis}
    for (a, b), terms in bracket.items():
        for output in terms:
            if parity[output] != (parity[a] + parity[b]) % 2:
                raise ValueError(
                    f"bracket[{a},{b}] has output {output} of inconsistent parity"
                )
    odd_map_entries = [
        (output, argument)
        for output, argument in product(names, repeat=2)
        if parity[output] != parity[argument]
    ]

    def bracket_of(left, right):
        return bracket.get((left, right), {})

    rows = [
        (a, b, output)
        for a, b in product(names, repeat=2)
        for output in names
        if parity[output] == (parity[a] + parity[b] + 1) % 2
    ]
    matrix = [[Fraction(0) for _ in odd_map_entries] for _ in rows]
    rhs = [Fraction(0) for _ in rows]
    row_index = {row: index for index, row in enumerate(rows)}

    for column, (f_output, f_argument) in enumerate(odd_map_entries):
        for a, b in product(names, repeat=2):
            pa, pb = parity[a], parity[b]
            sign1 = -1 if pa else 1
            sign2 = -1 if (pa + 1) * pb % 2 else 1
            if b == f_argument:
                for output, value in bracket_of(a, f_output).items():
                    row = (a, b, output)
                    if row in row_index:
                        matrix[row_index[row]][column] += sign1 * value
            if a == f_argument:
                for output, value in bracket_of(b, f_output).items():
                    row = (a, b, output)
                    if row in row_index:
                        matrix[row_index[row]][column] -= sign2 * value
            for middle, structure_constant in bracket_of(a, b).items():
                if middle == f_argument and output_parity_matches(
                    parity, middle, f_output, a, b
                ):
                    row = (a, b, f_output)
                    if row in row_index:
                        matrix[row_index[row]][column] -= structure_constant

    for (a, b), terms in gamma.items():
        for output, value in terms.items():
            if parity[output] != (parity[a] + parity[b] + 1) % 2:
                raise ValueError(
                    f"gamma[{a},{b}] has output {output} of inconsistent parity"
                )
            rhs[row_index[(a, b, output)]] = value

    solution, consistent, rank = solve(matrix, rhs)
    witness = {}
    if consistent:
        witness = {
            f"{output}<-{argument}": str(value)
            for (output, argument), value in zip(odd_map_entries, solution)
            if value
        }
    return {
        "trivial": consistent,
        "rank_coboundary_map": rank,
        "odd_map_witness": witness if consistent else None,
        "field": "Q",
    }


def output_parity_matches(parity, middle, f_output, a, b):
    return parity[f_output] == (parity[a] + parity[b] + 1) % 2


def solve(matrix, rhs):
    if not matrix:
        return [], all(value == 0 for value in rhs), 0
    row_count, column_count = len(matrix), len(matrix[0])
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    pivot_columns = []
    pivot_row = 0

    for column in range(column_count):
        selected = next(
            (row for row in range(pivot_row, row_count) if augmented[row][column]),
            None,
        )
        if selected is None:
            continue
        augmented[pivot_row], augmented[selected] = (
            augmented[selected],
            augmented[pivot_row],
        )
        pivot = augmented[pivot_row][column]
        augmented[pivot_row] = [value / pivot for value in augmented[pivot_row]]
        for row in range(row_count):
            if row != pivot_row and augmented[row][column]:
                factor = augmented[row][column]
                augmented[row] = [
                    left - factor * right
                    for left, right in zip(augmented[row], augmented[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break

    for row in augmented:
        if all(value == 0 for value in row[:column_count]) and row[-1] != 0:
            return None, False, len(pivot_columns)
    solution = [Fraction(0) for _ in range(column_count)]
    for row, column in enumerate(pivot_columns):
        solution[column] = augmented[row][-1]
    return solution, True, len(pivot_columns)


def self_test():
    abelian = {
        "basis": [{"name": "e", "parity": 0}, {"name": "o", "parity": 1}],
        "bracket": [],
        "gamma": [],
    }
    assert verify(abelian, check_documented_dimension=False)["trivial"]

    # For the abelian 1|1 algebra every coboundary is zero.
    abelian["gamma"] = [{"x": "e", "y": "e", "terms": {"e": "1"}}]
    try:
        verify(abelian, check_documented_dimension=False)
    except ValueError:
        # The test cochain intentionally violates odd-coboundary parity.
        pass
    else:
        raise AssertionError("expected inconsistent gamma parity to be rejected")

    abelian["gamma"] = [{"x": "e", "y": "o", "terms": {"e": "1"}}]
    assert not verify(abelian, check_documented_dimension=False)["trivial"]

    solvable = {
        "basis": [{"name": "h", "parity": 0}, {"name": "q", "parity": 1}],
        "bracket": [
            {"x": "h", "y": "q", "terms": {"q": "1"}},
            {"x": "q", "y": "h", "terms": {"q": "-1"}},
        ],
        "gamma": [
            {"x": "h", "y": "q", "terms": {"h": "-1"}},
            {"x": "q", "y": "h", "terms": {"h": "1"}},
            {"x": "q", "y": "q", "terms": {"q": "2"}},
        ],
    }
    result = verify(solvable, check_documented_dimension=False)
    assert result["trivial"] and result["odd_map_witness"] == {"h<-q": "1"}
    print("self-test passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON input file; reads stdin if omitted")
    parser.add_argument("--self-test", action="store_true", help="run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    try:
        with open(args.input, encoding="utf-8") if args.input else sys.stdin as stream:
            result = verify(json.load(stream))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
