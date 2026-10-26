"""
Implement derivation formula for quadratic superbrackets and verify against basis.
"""
from collections import defaultdict
from fractions import Fraction
import sympy as sp
from src.C_generators import build_c_basis, normal_order_word

def osc_parity(osc):
    return 1 if osc.startswith("a_") else 0

def bracket_osc(u, v, gb_dict):
    # [u, v} = [u, v}_0 + kappa * [u, v]_1
    # Returns (c_0, c_kappa_dict)
    # Both u, v in {a_1_p, a_1_m, b_k_p, b_k_m}
    pu, pv = osc_parity(u), osc_parity(v)
    
    c_0 = Fraction(0)
    c_k = defaultdict(Fraction)
    
    if pu == 0 and pv == 0:
        # Both bosons: [b_j^-, b_k^+] = delta_{jk}
        # [u, v] = - [v, u]
        ux, vx = u.split("_"), v.split("_")
        if ux[1] == vx[1]:
            if ux[2] == "m" and vx[2] == "p":
                c_0 = Fraction(1)
            elif ux[2] == "p" and vx[2] == "m":
                c_0 = Fraction(-1)
    elif pu == 1 and pv == 1:
        # Both fermions: {a_1^-, a_1^+} = 1
        # {a_1^+, a_1^-} = 1
        # {a_1^p, a_1^p} = 0, {a_1^m, a_1^m} = 0
        ux, vx = u.split("_"), v.split("_")
        if ux[2] != vx[2]:
            c_0 = Fraction(1)
    else:
        # One boson, one fermion:
        # C_inhomogeneous_definition.md:
        # [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
        # and [a_1^sigma, b_j^s] = - (-1)^{1 * 0} [b_j^s, a_1^sigma] = gb_{sigma, j, s} * kappa
        if pu == 0 and pv == 1:
            # u is boson b_j_s, v is fermion a_1_sigma
            bx, ax = u.split("_"), v.split("_")
            sig = ax[2]
            j = bx[1]
            s = bx[2]
            gb_name = f"gb_a1{sig}_b{j}{s}"
            c_k[gb_name] += Fraction(-1)
        else:
            # u is fermion a_1_sigma, v is boson b_j_s
            ax, bx = u.split("_"), v.split("_")
            sig = ax[2]
            j = bx[1]
            s = bx[2]
            gb_name = f"gb_a1{sig}_b{j}{s}"
            c_k[gb_name] += Fraction(1)
            
    return c_0, c_k

# For two quadratic monomials m1 = (u, v) and m2 = (x, y):
# In superalgebra:
# [u v, x y} = u [v, x y} + (-1)^{p(v) p(x y)} [u, x y} v
# [v, x y} = [v, x} y + (-1)^{p(v) p(x)} x [v, y}
# Since [v, x} is central (scalar or kappa),
# [v, x y} = [v, x} y + (-1)^{p(v) p(x)} [v, y} x.
# Similarly:
# [u, x y} = [u, x} y + (-1)^{p(u) p(x)} [u, y} x.
# Therefore:
# [u v, x y} =
#   [v, x} u y
# + (-1)^{p(v) p(x)} [v, y} u x
# + (-1)^{p(v) (p(x)+p(y))} [u, x} y v
# + (-1)^{p(v) (p(x)+p(y)) + p(u) p(x)} [u, y} x v.

def superbracket_monomials(u, v, x, y):
    pu, pv = osc_parity(u), osc_parity(v)
    px, py = osc_parity(x), osc_parity(y)
    pxy = (px + py) % 2
    
    terms = []
    
    # Term 1: [v, x} u y
    c0, ck = bracket_osc(v, x, None)
    sign = Fraction(1)
    terms.append((sign, c0, ck, (u, y)))
    
    # Term 2: (-1)^{pv px} [v, y} u x
    c0, ck = bracket_osc(v, y, None)
    s2 = -1 if (pv * px) % 2 == 1 else 1
    terms.append((Fraction(s2), c0, ck, (u, x)))
    
    # Term 3: (-1)^{pv pxy} [u, x} y v
    c0, ck = bracket_osc(u, x, None)
    s3 = -1 if (pv * pxy) % 2 == 1 else 1
    terms.append((Fraction(s3), c0, ck, (y, v)))
    
    # Term 4: (-1)^{pv pxy + pu px} [u, y} x v
    c0, ck = bracket_osc(u, y, None)
    s4 = -1 if ((pv * pxy + pu * px) % 2 == 1) else 1
    terms.append((Fraction(s4), c0, ck, (x, v)))
    
    # Now for each term, normal-order the remaining 2-oscillator word:
    res_0 = defaultdict(Fraction)
    res_k = defaultdict(lambda: defaultdict(Fraction)) # gb_name -> word -> coeff
    
    for sign, c0, ck, w in terms:
        # Standard part
        if c0 != 0:
            no = normal_order_word(list(w), sign * c0)
            for nw, nc in no.items():
                res_0[nw] += nc
        # Kappa part
        for gb_name, c_gb in ck.items():
            if c_gb != 0:
                no = normal_order_word(list(w), sign * c_gb)
                for nw, nc in no.items():
                    res_k[gb_name][nw] += nc
                    
    return res_0, res_k

def superbracket_polys(poly1, poly2):
    tot_0 = defaultdict(Fraction)
    tot_k = defaultdict(lambda: defaultdict(Fraction))
    for w1, c1 in poly1.items():
        if len(w1) == 0: continue # scalar commutes
        for w2, c2 in poly2.items():
            if len(w2) == 0: continue
            u, v = w1
            x, y = w2
            r0, rk = superbracket_monomials(u, v, x, y)
            for w, c in r0.items():
                tot_0[w] += c1 * c2 * c
            for gb_name, wdict in rk.items():
                for w, c in wdict.items():
                    tot_k[gb_name][w] += c1 * c2 * c
    return {w: c for w, c in tot_0.items() if c != 0}, {gb: {w: c for w, c in wd.items() if c != 0} for gb, wd in tot_k.items()}

# Let's test on n=1:
print("Testing derivation superbracket for n=1:")
even, odd, gens = build_c_basis(1)
full = even + odd

all_words = set()
for g in gens.values():
    all_words.update(g["poly"].keys())
word_list = sorted(list(all_words))
M_sp = sp.Matrix(
    [[gens[name]["poly"].get(w, Fraction(0)) for name in full] for w in word_list]
)

all_closed_0 = True
all_closed_k = True
gamma_count = 0

for i, X in enumerate(full):
    for j, Y in enumerate(full):
        r0, rk = superbracket_polys(gens[X]["poly"], gens[Y]["poly"])
        # Check r0 matches basis
        v0 = sp.Matrix([r0.get(w, Fraction(0)) for w in word_list])
        sol0, _ = M_sp.gauss_jordan_solve(v0)
        
        # Check rk
        for gb, wdict in rk.items():
            vk = sp.Matrix([wdict.get(w, Fraction(0)) for w in word_list])
            try:
                solk, _ = M_sp.gauss_jordan_solve(vk)
                for k, Z in enumerate(full):
                    if solk[k] != 0:
                        gamma_count += 1
            except Exception as e:
                print(f"FAILED TO DECOMPOSE rk for [{X}, {Y}] gb={gb}: {wdict}")
                all_closed_k = False

print(f"Standard closure: {all_closed_0}")
print(f"Gamma closure: {all_closed_k}")
print(f"Total non-zero gamma coefficients: {gamma_count}")
