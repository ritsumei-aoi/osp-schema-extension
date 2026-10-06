"""Print the evidence used in the I08 report (reads data/C_{n}_triviality.json and Layers 2-4).

Usage: python3 src/C_triviality_report.py
"""
import copy
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR  # noqa: E402
from C_triviality import solve, load_profiles, residual, analytic_f, f_to_values  # noqa: E402
from C_coboundary import load_coboundary, evaluate_linear  # noqa: E402

SHORT = {"E_eps1_del1_pp": "Epp", "E_eps1_del1_pm": "Epm", "E_eps1_del1_mp": "Emp",
         "E_eps1_del1_mm": "Emm"}


def load(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_triviality.json")) as f:
        return json.load(f)


def main():
    print("## 1. Strict reading: where do gamma and delta f disagree?")
    for n in (1, 2, 3):
        s = load(n)["readings"]["strict"]["targets"]
        comps = {tuple(v.get("inconsistent_components", [])) for v in s.values() if not v["trivial"]}
        cnt = {k: v.get("inconsistent_equations") for k, v in s.items()
               if k in ("all_plus", "unit_p_1_p", "unit:gb_m_1_m")}
        print(f"n={n}: inconsistent components {comps}; #inconsistent equations {cnt}")
    d1 = load(1)
    print("n=1 all_plus examples:", d1["readings"]["strict"]["targets"]["all_plus"]["inconsistent_examples"][:6])

    print("\n## 2. Layer 3 vs Layer 4 at the solved f (n=1, profile all_plus, reading mod_K)")
    gb, ev = load_profiles(1)["all_plus"]
    sol = {k: Fraction(v) for k, v in d1["readings"]["mod_K"]["targets"]["all_plus"]["particular_solution"].items()}
    _, sym = load_coboundary(1)
    df = evaluate_linear(sym, sol)
    for pair in [("E_eps1_del1_pp", "E_eps1_del1_pp"), ("H_1", "H_2"), ("E_2del1_p", "E_eps1_del1_pm"),
                 ("E_eps1_del1_pp", "E_eps1_del1_mm")]:
        g = {k: str(v) for k, v in ev.get(pair, {}).items()}
        f = {k: str(v) for k, v in df.get(pair, {}).items()}
        print(f"  {pair}: gamma={g}\n  {' ' * len(str(pair))}  delta f={f}")
    print("  particular solution (nonzero phi):", d1["readings"]["mod_K"]["targets"]["all_plus"]["particular_solution"])

    print("\n## 3. Analytic f from a = a' + kappa*lambda (n=1, symbolic in gb)")
    for j, coords in d1["analytic_f_symbolic"].items():
        print(f"  f({j}) = " + " ; ".join(f"[{i}]: {c}" for i, c in coords.items()))
    for n in (1, 2, 3):
        print(f"  n={n}: residual entries of analytic f (exact reading) per target:",
              set(load(n)["analytic_candidate_residual_entries"].values()))

    print("\n## 4. Solver non-vacuity: perturbed gamma must be detected")
    t = {"all_plus": ev}
    bad = copy.deepcopy(ev)
    bad[("H_1", "H_2")]["E_eps1_del1_pp"] += 1
    bad[("H_2", "H_1")]["E_eps1_del1_pp"] -= 1
    t["perturbed_H1H2"] = bad
    bad2 = copy.deepcopy(ev)
    bad2[("E_eps1_del1_pp", "E_eps1_del1_pp")]["E_eps1_del1_pp"] *= -1
    t["perturbed_EppEpp"] = bad2
    solver, cols, names = solve(1, t, "mod_K")
    for i, nm in enumerate(names):
        print(f"  {nm}: trivial={not solver.inconsistent[i]} inconsistent eqs={solver.inconsistent[i][:3]}")

    print("\n## 5. Kernel of delta (odd maps, mod K) vs inner maps ad_Z, Z odd")
    for n in (1, 2, 3):
        r = load(n)["readings"]["mod_K"]
        print(f"  n={n}: unknowns={r['unknowns']} rank={r['rank']} kernel={r['kernel_dim']} (odd dim 4n={4*n})")


if __name__ == "__main__":
    main()
