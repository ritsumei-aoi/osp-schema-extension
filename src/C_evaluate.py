"""Layer 3: evaluated gamma structure for C(n+1) (I06).

Substitutes a concrete value for each gb parameter into the Schema 2 gamma
coefficients, giving numerically evaluated structure constants of the
inhomogeneous deformation.

Representative assignment (decided in I06): every gb parameter is +1. This is
the simplest nonzero profile, so every term of gamma survives the substitution.
Other profiles can be passed in; see `evaluate`.
"""

import json
from pathlib import Path

import sympy

import C_gamma as G


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

DEFAULT_PROFILE = "all_plus_one"


def gb_all(n, value):
    rows, cols = G.gb_labels(n)
    return {str(G.gb_symbol(r, c)): sympy.Integer(value) for r in rows for c in cols}


PROFILES = {
    "all_plus_one": lambda n: gb_all(n, 1),
}


def evaluate_terms(terms, assignment):
    """Substitute gb values into a list of {X,Y,Z,coeff} entries; drop zeros."""
    out = []
    for t in terms:
        val = sympy.sympify(t["coeff"]).subs(assignment)
        if val != 0:
            out.append({"X": t["X"], "Y": t["Y"], "Z": t["Z"], "coeff": str(val)})
    return out


def evaluate(n, profile=DEFAULT_PROFILE):
    assignment = PROFILES[profile](n)
    gamma_doc = json.loads((DATA / f"C_{n}_gamma.json").read_text())
    entries = gamma_doc["inhomogeneous_deformation"]["gamma"]
    evaluated = evaluate_terms(entries, assignment)
    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "layer": "evaluated_gamma",
        "gb_assignment_profile": profile,
        "gb_assignment": {k: str(v) for k, v in sorted(assignment.items())},
        "evaluated_structure_constants": evaluated,
        "source": f"data/C_{n}_gamma.json",
    }


def check_consistency(n, profile=DEFAULT_PROFILE):
    """Recompute from the symbolic gamma (not the file) and compare with the evaluated data."""
    assignment = PROFILES[profile](n)
    labels, parity, undeformed, gamma = G.split_kappa(n)
    pbw = {l: i for i, l in enumerate(labels)}
    # The file stores each unordered pair once, in PBW order: compare that orientation.
    fresh = {}
    for (X, Y), terms in gamma.items():
        if pbw[X] > pbw[Y]:
            continue
        for Z, c in terms.items():
            val = sympy.sympify(c).subs(assignment)
            if val != 0:
                fresh[(X, Y, Z)] = val
    doc = evaluate(n, profile)
    from_file = {
        (e["X"], e["Y"], e["Z"]): sympy.Rational(e["coeff"])
        for e in doc["evaluated_structure_constants"]
    }
    return fresh == from_file, len(from_file)


def main():
    for n in (1, 2, 3):
        doc = evaluate(n)
        path = DATA / f"C_{n}_evaluated.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        ok, count = check_consistency(n)
        print(f"wrote {path.name}: evaluated entries={count}, consistent with Schema 2: {ok}")
    return 0


if __name__ == "__main__":
    main()
