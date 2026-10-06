"""
C(n+1) Schema-3: evaluated structure.  Issue I06.

Substitute concrete numerical values for the 4n gb deformation parameters into the symbolic
gamma structure (Schema 2) to obtain the evaluated inhomogeneous deformation.

Representative gb profiles (parity-1 parameters given concrete signs):
  * "all_plus"      : every gb = +1
  * "fermion_sign"  : gb_{sigma,j,s} = +1 if sigma=+ else -1

For each profile we emit the numerically evaluated gamma coefficients and cross-check them against
an independent recomputation of the deformed bracket with a *numeric* gb hook (consistency with
Schema 2).

Run:  python3 src/C_evaluate.py      # writes data/C_{1,2,3}_evaluated.json
"""

from __future__ import annotations
import json
import os
import sys
from datetime import date
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osc_algebra as oa
import C_generators as cg
import C_gamma as cgm

DATA_DIR = cg.DATA_DIR


def profiles(n):
    """Return {profile_name: {gb_name: value}}."""
    out = {}
    allp = {}
    fsg = {}
    for sigma in (+1, -1):
        for j in range(1, n + 1):
            for s in (+1, -1):
                name = cgm.gb_name(sigma, j, s)
                allp[name] = 1
                fsg[name] = 1 if sigma == +1 else -1
    out["all_plus"] = allp
    out["fermion_sign"] = fsg
    return out


def numeric_gb_hook(prof):
    def hook(sigma, j, s):
        return sp.Integer(prof[cgm.gb_name(sigma, j, s)])
    return hook


def evaluate_profile(n, prof):
    """Evaluated gamma records + a consistency flag vs an independent numeric recompute."""
    R = cg.realizations(n)
    P = cg.parity_map(n)
    order = cg.pbw_order(n)
    pos = {lab: i for i, lab in enumerate(order)}
    subs = {sp.Symbol(k): sp.Integer(v) for k, v in prof.items()}
    hook = numeric_gb_hook(prof)

    records = []
    mismatches = []
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            # symbolic gamma -> substitute
            _, gam_sym = cgm.split_kappa(cgm.deformed_bracket(X, Y, R, P))
            comps_sym = {Z: sp.nsimplify(sp.expand(c).subs(subs))
                         for Z, c in cg.decompose(gam_sym, n).items()}
            comps_sym = {Z: c for Z, c in comps_sym.items() if c != 0}
            # independent numeric recompute
            defbr = oa.graded_commutator(R[X], P[X], R[Y], P[Y], gb=hook)
            _, gam_num = cgm.split_kappa(defbr)
            comps_num = {Z: c for Z, c in cg.decompose(gam_num, n).items() if c != 0}
            keys = set(comps_sym) | set(comps_num)
            if any(sp.simplify(comps_sym.get(k, 0) - comps_num.get(k, 0)) != 0 for k in keys):
                mismatches.append((X, Y))
            for Z, c in sorted(comps_sym.items(), key=lambda kv: pos.get(kv[0], 10 ** 9)):
                records.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "carrier": "kappa"})
    return records, mismatches


def build_schema3(n):
    profs = profiles(n)
    evaluations = {}
    all_ok = True
    for name, prof in profs.items():
        recs, mism = evaluate_profile(n, prof)
        all_ok = all_ok and not mism
        evaluations[name] = {
            "gb_values": prof,
            "evaluated_gamma": recs,
            "num_nonzero": len(recs),
            "consistency_with_schema2": (len(mism) == 0),
            "mismatches": mism,
        }
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "description": "Evaluated inhomogeneous deformation: gamma with concrete gb values.",
        "representative_profile": "all_plus",
        "evaluations": evaluations,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": date.today().isoformat(),
            "depends_on": [f"C_{n}_gamma.json", f"C_{n}_structure.json"],
        },
    }, all_ok


def generate_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        data, ok = build_schema3(n)
        path = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        nz = data["evaluations"]["all_plus"]["num_nonzero"]
        print(f"wrote {path}  (all_plus #nonzero={nz}, consistency_with_schema2={ok})")


if __name__ == "__main__":
    generate_all()
