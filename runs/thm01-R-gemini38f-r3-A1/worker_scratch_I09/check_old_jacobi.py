import json, os, sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"

with open(f"{REPO_ROOT}/data/C_1_structure.json") as f: s1 = json.load(f)
with open(f"{REPO_ROOT}/data/C_1_gamma.json") as f: s2 = json.load(f)

basis_even = s1["basis"]["even"]
basis_odd = s1["basis"]["odd"]
all_basis = basis_even + basis_odd
parity = s1["parity"]

c_base = defaultdict(Fraction)
for e in s1["structure_constants"]:
    c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

gb_labels = s2["deformation_parameters"]["labels"]
gb_syms = {p: sp.Symbol(p) for p in gb_labels}

gamma = defaultdict(lambda: sp.Integer(0))
for e in s2["inhomogeneous_deformation"]:
    gamma[(e["X"], e["Y"], e["Z"])] += Fraction(e["coeff"]) * gb_syms[e["param"]]

# Super-Jacobi for deformed bracket [X, Y]~ = [X, Y]_0 + kappa * gamma(X, Y)
# To first order in kappa:
# (-1)^{pX pZ} [X, [Y, Z]~]~ + cyc = 0
# At order 0: Jacobi of [ , ]_0 = 0 (already verified).
# At order 1 (coefficient of kappa):
# (-1)^{pX pZ} ( [X, gamma(Y, Z)]_0 + gamma(X, [Y, Z]_0) ) + cyc = 0 ?
# Wait! Note the parity of kappa and gamma!
# In [X, kappa * gamma(Y, Z)]_0:
# If kappa has parity 1, then [X, kappa * gamma(Y, Z)]_0 = (-1)^{pX} kappa [X, gamma(Y, Z)]_0!
# Let's check both with and without the (-1)^pX factor:

def check_jacobi(with_koszul_on_kappa=False):
    violations = 0
    total_triples = 0
    for idx_X, X in enumerate(all_basis):
        pX = parity[X]
        for idx_Y, Y in enumerate(all_basis):
            if idx_X > idx_Y: continue
            pY = parity[Y]
            for idx_Z, Z in enumerate(all_basis):
                if idx_Y > idx_Z: continue
                pZ = parity[Z]
                total_triples += 1

                # Sum cyclic permutations
                # Term 1: (-1)^{pX pZ} [X, [Y, Z]]
                # Term 2: (-1)^{pY pX} [Y, [Z, X]]
                # Term 3: (-1)^{pZ pY} [Z, [X, Y]]
                triples = [
                    (X, pX, Y, pY, Z, pZ, (-1)**(pX * pZ)),
                    (Y, pY, Z, pZ, X, pX, (-1)**(pY * pX)),
                    (Z, pZ, X, pX, Y, pY, (-1)**(pZ * pY)),
                ]

                # We evaluate the coefficient of each basis element W in the sum
                res_W = defaultdict(lambda: sp.Integer(0))
                for A, pA, B, pB, C, pC, sign_cyc in triples:
                    # [A, gamma(B, C)]_0
                    # gamma(B, C) is sum_W gamma(B, C)^W * W
                    sign_kappa = (-1)**pA if with_koszul_on_kappa else 1
                    for W in all_basis:
                        g_BC_W = gamma.get((B, C, W), sp.Integer(0))
                        if g_BC_W != 0:
                            # [A, W]_0
                            for target in all_basis:
                                c = c_base.get((A, W, target), Fraction(0))
                                if c != 0:
                                    res_W[target] += sign_cyc * sign_kappa * g_BC_W * c

                    # gamma(A, [B, C]_0)
                    for W in all_basis:
                        c_BC_W = c_base.get((B, C, W), Fraction(0))
                        if c_BC_W != 0:
                            for target in all_basis:
                                g_AW_target = gamma.get((A, W, target), sp.Integer(0))
                                if g_AW_target != 0:
                                    res_W[target] += sign_cyc * c_BC_W * g_AW_target

                for target, expr in res_W.items():
                    if sp.simplify(expr) != 0:
                        violations += 1
                        if violations <= 5:
                            print(f"Violation on ({X}, {Y}, {Z}), target {target}: {sp.simplify(expr)}")
                        break

    print(f"with_koszul={with_koszul_on_kappa}: Total triples: {total_triples}, Violations: {violations}")

print("Checking old gamma in C_1_gamma.json:")
check_jacobi(False)
check_jacobi(True)
