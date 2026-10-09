"""Schema 3 (evaluated deformation) for C(n+1)  (Issue I06).

Substitutes concrete values of the 4n gb parameters into the Schema 2 linear forms and
writes  data/C_{n}_evaluated.json  (default profile "ones")  and
        data/C_{n}_evaluated_<profile>.json  for the other sign profiles.

Consistency check: the evaluated gamma is recomputed *directly* in the deformed oscillator
algebra with the numeric gb values (independent of the Schema 2 linear forms) and compared.

Usage: python3 src/C_evaluate.py [--datadir data] [--profiles ones,alternating,...] [n ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import Decomposer, OscillatorAlgebra, algebra_block, build_basis, fr, metadata_block  # noqa: E402
from C_gamma import gb_labels  # noqa: E402


# ---------------------------------------------------------------------- profiles

def profile_values(name: str, n: int) -> dict:
    """Return {gb_label: Fraction} for a named sign profile."""
    vals = {}
    for lab, (sigma, k, s) in gb_labels(n):
        if name == "ones":
            v = 1
        elif name == "alternating":          # +1 when the two signs agree, -1 otherwise
            v = 1 if sigma == s else -1
        elif name == "plus_only":            # only the a_1^+ row is switched on
            v = 1 if sigma == "p" else 0
        elif name == "minus_only":           # only the a_1^- row is switched on
            v = 1 if sigma == "m" else 0
        elif name == "single":               # a single parameter gb_{a_1^+, b_1^+}
            v = 1 if (sigma, k, s) == ("p", 1, "p") else 0
        elif name == "conjugate":            # gb_{a^-, b_k^s} = gb_{a^+, b_k^{-s}}, graded by k
            v = (k if s == "p" else -k) if sigma == "p" else (-k if s == "p" else k)
        elif name == "mixed":                # fixed pseudo-random ±1 / rational pattern
            v = [1, -1, Fraction(1, 2), -2][(2 * (sigma == "m") + (s == "m") + k) % 4]
        else:
            raise ValueError(f"unknown profile {name}")
        vals[lab] = Fraction(v)
    return vals


PROFILES = ["ones", "alternating", "plus_only", "minus_only", "single", "conjugate", "mixed"]


# ---------------------------------------------------------------------- evaluation

def evaluate_gamma(schema2: dict, values: dict):
    """Evaluate the Schema 2 linear forms; returns list of {X,Y,Z,coeff} with non-zero coeff."""
    out = []
    for e in schema2["inhomogeneous_deformation"]["gamma"]:
        c = sum(Fraction(v) * values[l] for l, v in e["coeff"].items())
        if c != 0:
            out.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": fr(c)})
    return out


def direct_gamma(n: int, values: dict):
    """Independent recomputation: deformed brackets with numeric gb in the oscillator algebra."""
    odd, even, real, roots = build_basis(n)
    order = odd + even
    gb = {key: values[lab] for lab, key in gb_labels(n)}
    alg = OscillatorAlgebra(n, gb)
    elements = {lab: alg.element(terms) for lab, terms in real.items()}
    dec = Decomposer(OscillatorAlgebra(n), order, {lab: OscillatorAlgebra(n).element(t) for lab, t in real.items()}, include_K=True)
    out = []
    zorder = order + ["K"]
    for X in order:
        for Y in order:
            A0, A1 = alg.split_kappa(alg.bracket(elements[X], elements[Y]))
            comps = dec.decompose(A1)
            for Z in zorder:
                if Z in comps:
                    out.append({"X": X, "Y": Y, "Z": Z, "coeff": fr(comps[Z])})
    return out


def build_schema3(n: int, profile: str, schema1: dict, schema2: dict, check=True):
    values = profile_values(profile, n)
    ev = evaluate_gamma(schema2, values)
    if check:
        direct = direct_gamma(n, values)
        if direct != ev:
            raise RuntimeError(f"evaluated gamma differs from direct computation for n={n}, profile={profile}")
    deformed = [dict(e, kappa_order=0) for e in
                ({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": e["coeff"]} for e in schema1["structure_constants"])]
    deformed += [dict(e, kappa_order=1) for e in ev]
    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": algebra_block(n),
        "source_structure": f"C_{n}_structure.json",
        "source_gamma": f"C_{n}_gamma.json",
        "profile": profile,
        "profile_description": PROFILE_DESCRIPTIONS[profile],
        "gb_assignment": {lab: fr(values[lab]) for lab, _ in gb_labels(n)},
        "evaluated_gamma": ev,
        "deformed_structure_constants": deformed,
        "consistency": {
            "direct_recomputation_matches": bool(check),
            "description": "evaluated_gamma equals the kappa-part of the brackets recomputed in the deformed oscillator algebra with the numeric gb values",
        },
        "metadata": metadata_block("src/C_evaluate.py"),
    }


PROFILE_DESCRIPTIONS = {
    "ones": "all 4n parameters equal to +1 (representative assignment)",
    "alternating": "gb = +1 when the fermion sign equals the boson sign, -1 otherwise",
    "plus_only": "gb_{a_1^+, .} = 1, gb_{a_1^-, .} = 0",
    "minus_only": "gb_{a_1^-, .} = 1, gb_{a_1^+, .} = 0",
    "single": "only gb_{a_1^+, b_1^+} = 1",
    "conjugate": "gb_{a_1^+, b_k^±} = ±k and gb_{a_1^-, b_k^±} = ∓k (row-2 entries are the sign-flipped row-1 entries)",
    "mixed": "fixed pattern of values in {1, -1, 1/2, -2} depending on (σ, k, s)",
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ns", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--datadir", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    ap.add_argument("--profiles", default=",".join(PROFILES))
    args = ap.parse_args(argv)
    for n in args.ns:
        with open(os.path.join(args.datadir, f"C_{n}_structure.json")) as fh:
            s1 = json.load(fh)
        with open(os.path.join(args.datadir, f"C_{n}_gamma.json")) as fh:
            s2 = json.load(fh)
        for prof in args.profiles.split(","):
            s3 = build_schema3(n, prof, s1, s2)
            name = f"C_{n}_evaluated.json" if prof == "ones" else f"C_{n}_evaluated_{prof}.json"
            path = os.path.join(args.datadir, name)
            with open(path, "w") as fh:
                json.dump(s3, fh, indent=1, ensure_ascii=False)
            ev = s3["evaluated_gamma"]
            print(f"C({n+1}) profile {prof:12s}: {len(ev):5d} non-zero gamma entries "
                  f"({sum(1 for e in ev if e['Z']=='K')} with Z=K); direct recomputation matches -> {os.path.relpath(path)}")


if __name__ == "__main__":
    main()
