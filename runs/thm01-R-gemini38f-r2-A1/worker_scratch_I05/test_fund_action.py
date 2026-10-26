"""
Check what monomials appear in C(n+1).
Can C(n+1) act on V as the fundamental representation?
Let's compute the action of X in C(n+1) on the oscillators in V:
For each generator X in C(n+1) and oscillator w in V:
rho(X)(w) = [X, w] in U(A).
"""
from collections import defaultdict
from fractions import Fraction
import sympy as sp
from src.C_generators import build_c_basis
from test_quadratic_bracket import osc_parity, bracket_osc, normal_order_word

def action_generator_on_osc(poly_X, pX, w):
    # [X, w} in U(A)
    # X = sum c u v.
    # [u v, w} = u [v, w} + (-1)^{pv pw} [u, w} v
    pw = osc_parity(w)
    res_0 = defaultdict(Fraction) # osc -> coeff
    res_k = defaultdict(lambda: defaultdict(Fraction)) # gb -> osc -> coeff
    
    for w_pair, c in poly_X.items():
        if len(w_pair) == 0:
            continue
        u, v = w_pair
        pu, pv = osc_parity(u), osc_parity(v)
        
        # Term 1: u [v, w}
        c0_vw, ck_vw = bracket_osc(v, w, None)
        if c0_vw != 0:
            res_0[u] += c * c0_vw
        for gb, c_gb in ck_vw.items():
            res_k[gb][u] += c * c_gb
            
        # Term 2: (-1)^{pv pw} [u, w} v
        c0_uw, ck_uw = bracket_osc(u, w, None)
        s = -1 if (pv * pw) % 2 == 1 else 1
        if c0_uw != 0:
            res_0[v] += c * s * c0_uw
        for gb, c_gb in ck_uw.items():
            res_k[gb][v] += c * s * c_gb
            
    return res_0, res_k

# For n=1:
even, odd, gens = build_c_basis(1)
V = ["a_1_p", "a_1_m", "b_1_p", "b_1_m"]

print("Action of generators on V:")
for name in gens:
    print(f"\nGenerator {name} (parity {gens[name]['parity']}):")
    for w in V:
        r0, rk = action_generator_on_osc(gens[name]["poly"], gens[name]["parity"], w)
        r0_str = " + ".join([f"{c}*{k}" for k, c in r0.items()]) or "0"
        print(f"  [X, {w}]_0 = {r0_str}")
        if rk:
            rk_str = ", ".join([f"{gb}: {'+'.join([f'{c}*{k}' for k,c in wd.items()])}" for gb, wd in rk.items()])
            print(f"      deformed: {rk_str}")
