"""
Verify minimal obstructions for general j in n=2.
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def verify_mode_j(n=2, j=2):
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    
    even_gens = [g for g in gen_names if parities[g] == 0]
    odd_gens = [g for g in gen_names if parities[g] == 1]
    
    phi = {}
    for o in odd_gens:
        for e in even_gens:
            phi[(o, e)] = sp.Symbol(f"phi_{o}_{e}")
            phi[(e, o)] = sp.Symbol(f"phi_{e}_{o}")
            
    c0 = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    gamma = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    
    for g1 in gen_names:
        for g2 in gen_names:
            br = superbracket(g1, g2, gens, parities, reduce_word)
            t0 = {k: v[0] for k, v in br.items() if v[0] != 0}
            tk = {k: v[1] for k, v in br.items() if v[1] != 0}
            dec0, _ = decompose_into_basis(t0, gens, n)
            deck, _ = decompose_into_basis(tk, gens, n)
            for k_gen, val in dec0.items():
                c0[(g1, g2)][k_gen] = val
            for k_gen, val in deck.items():
                gamma[(g1, g2)][k_gen] = val

    def compute_delta_f(g1, g2, r):
        p1, p2 = parities[g1], parities[g2]
        res = sp.Integer(0)
        s1 = (-1)**p1
        for k in gen_names:
            if parities[k] == 1 - p2:
                res += s1 * phi[(k, g2)] * c0[(g1, k)][r]
        s2 = - (-1)**((p1 + 1) * p2)
        for k in gen_names:
            if parities[k] == 1 - p1:
                res += s2 * phi[(k, g1)] * c0[(g2, k)][r]
        for m, c_val in c0[(g1, g2)].items():
            if parities[r] == 1 - parities[m]:
                res -= c_val * phi[(r, m)]
        return sp.simplify(res)

    print(f"--- Verifying mode j={j} in n={n} ---")
    # For j=2:
    # E_2d_j = E_2d_2
    # E_-2d_j = E_-2d_2
    # F_p_j_p = F_p_2_p
    # F_p_j_m = F_p_2_m
    # F_m_j_p = F_m_2_p
    # F_m_j_m = F_m_2_m
    # Cartan element: H_3 = - b2+ b2- - 1/2
    
    # 1. gb_+_2_-
    df1 = compute_delta_f("F_p_2_m", "H_1", "H_3")
    g1 = gamma[("F_p_2_m", "H_1")]["H_3"]
    print("Obstruction 1 for j=2:")
    print("  delta_f =", df1)
    print("  gamma =", g1)
    
    # 2. gb_+_2_+
    df2a = compute_delta_f("F_p_2_p", "F_p_2_m", "F_p_2_m")
    g2a = gamma[("F_p_2_p", "F_p_2_m")]["F_p_2_m"]
    df2b = compute_delta_f("F_p_2_m", "E_2d_2", "H_3")
    g2b = gamma[("F_p_2_m", "E_2d_2")]["H_3"]
    print("Obstruction 2 for j=2:")
    print("  delta_f comb =", sp.simplify(df2a + df2b))
    print("  gamma comb =", sp.simplify(g2a + g2b))

    # 3. gb_-_2_-
    df3a = compute_delta_f("F_m_2_p", "F_m_2_m", "F_m_2_p")
    g3a = gamma[("F_m_2_p", "F_m_2_m")]["F_m_2_p"]
    df3b = compute_delta_f("F_m_2_p", "E_-2d_2", "H_3")
    g3b = gamma[("F_m_2_p", "E_-2d_2")]["H_3"]
    print("Obstruction 3 for j=2:")
    print("  delta_f comb =", sp.simplify(df3a + df3b))
    print("  gamma comb =", sp.simplify(g3a + g3b))

    # 4. gb_-_2_+
    df4a = compute_delta_f("F_m_2_p", "F_m_2_p", "F_m_2_p")
    g4a = gamma[("F_m_2_p", "F_m_2_p")]["F_m_2_p"]
    df4b = compute_delta_f("F_m_2_p", "H_3", "H_3")
    g4b = gamma[("F_m_2_p", "H_3")]["H_3"]
    print("Obstruction 4 for j=2:")
    print("  delta_f comb =", sp.simplify(sp.Rational(-1, 2) * df4a + df4b))
    print("  gamma comb =", sp.simplify(sp.Rational(-1, 2) * g4a + g4b))

if __name__ == '__main__':
    verify_mode_j(2, 2)
