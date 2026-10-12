"""
Symbolic verification of the 4 minimal obstructions.
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def verify_minimal_obstructions(n=1):
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
        # Term 1: (-1)^p1 [g1, f(g2)]
        s1 = (-1)**p1
        for k in gen_names:
            if parities[k] == 1 - p2:
                res += s1 * phi[(k, g2)] * c0[(g1, k)][r]
        # Term 2: - (-1)^{(p1+1)p2} [g2, f(g1)]
        s2 = - (-1)**((p1 + 1) * p2)
        for k in gen_names:
            if parities[k] == 1 - p1:
                res += s2 * phi[(k, g1)] * c0[(g2, k)][r]
        # Term 3: - f([g1, g2])
        for m, c_val in c0[(g1, g2)].items():
            if parities[r] == 1 - parities[m]:
                res -= c_val * phi[(r, m)]
        return sp.simplify(res)

    print(f"==================================================")
    print(f"Verifying Minimal Obstructions for n={n} (C({n+1}))")
    print(f"==================================================")

    # For general n, each mode j in {1, ..., n} defines an osp(2|2)_j sub-superalgebra.
    # The canonical Cartan generator H_{n+1} = -b_n^+ b_n^- - 1/2.
    # The element H_1^(j) = a_1^+ a_1^- + b_j^+ b_j^- is represented in the canonical basis as:
    # H_1^(j) = H_1 - sum_{k=2}^j H_k.
    #
    # Obstruction 1 directly evaluates the bracket [F_{+, j, -}, H_1^(j)] along canonical basis element H_{n+1}:
    for j in range(1, n + 1):
        print(f"\n--- Mode j={j} ---")
        print(f"  [Obstruction 1: gb_+_{j}_-]")
        df1 = compute_delta_f(f"F_p_{j}_m", "H_1", f"H_{n+1}")
        g1 = gamma[(f"F_p_{j}_m", "H_1")][f"H_{n+1}"]
        for k in range(2, j + 1):
            df1 -= compute_delta_f(f"F_p_{j}_m", f"H_{k}", f"H_{n+1}")
            g1 -= gamma[(f"F_p_{j}_m", f"H_{k}")][f"H_{n+1}"]
        print(f"    delta_f(F_p_{j}_m, H_1^({j}))_{{H_{n+1}}} =", df1)
        print(f"    gamma(F_p_{j}_m, H_1^({j}))_{{H_{n+1}}} =", g1)
        print(f"    => {g1} = 0  ==>  gb_+_{j}_- = 0")
        assert df1 == 0 and g1 == -2 * gb[('+', j, '-')]

    # Canonical Obstructions for n=1 and n=2:
    if n == 1:
        print("\n--- Canonical Obstructions for n=1 (C(2)) ---")
        print("  [Obstruction 2: gb_+_1_+]")
        df2a = compute_delta_f("F_p_1_p", "F_p_1_m", "F_p_1_m")
        g2a = gamma[("F_p_1_p", "F_p_1_m")]["F_p_1_m"]
        df2b = compute_delta_f("F_p_1_m", "E_2d_1", "H_2")
        g2b = gamma[("F_p_1_m", "E_2d_1")]["H_2"]
        comb_df2 = sp.simplify(df2a + df2b)
        comb_g2 = sp.simplify(g2a + g2b)
        print("    delta_f comb =", comb_df2)
        print("    gamma comb =", comb_g2)
        print("    =>", comb_g2, "= 0  ==>  gb_+_1_+ = 0")
        assert comb_df2 == 0 and comb_g2 == -2 * gb[('+', 1, '+')]

        print("  [Obstruction 3: gb_-_1_-]")
        df3a = compute_delta_f("F_m_1_p", "F_m_1_m", "F_m_1_p")
        g3a = gamma[("F_m_1_p", "F_m_1_m")]["F_m_1_p"]
        df3b = compute_delta_f("F_m_1_p", "E_-2d_1", "H_2")
        g3b = gamma[("F_m_1_p", "E_-2d_1")]["H_2"]
        comb_df3 = sp.simplify(df3a + df3b)
        comb_g3 = sp.simplify(g3a + g3b)
        print("    delta_f comb =", comb_df3)
        print("    gamma comb =", comb_g3)
        print("    =>", comb_g3, "= 0  ==>  gb_-_1_- = 0")
        assert comb_df3 == 0 and comb_g3 == -2 * gb[('-', 1, '-')]

        print("  [Obstruction 4: gb_-_1_+]")
        df4a = compute_delta_f("F_m_1_p", "F_m_1_p", "F_m_1_p")
        g4a = gamma[("F_m_1_p", "F_m_1_p")]["F_m_1_p"]
        df4b = compute_delta_f("F_m_1_p", "H_2", "H_2")
        g4b = gamma[("F_m_1_p", "H_2")]["H_2"]
        comb_df4 = sp.simplify(sp.Rational(-1, 2) * df4a + df4b)
        comb_g4 = sp.simplify(sp.Rational(-1, 2) * g4a + g4b)
        print("    delta_f comb =", comb_df4)
        print("    gamma comb =", comb_g4)
        print("    =>", comb_g4, "= 0  ==>  gb_-_1_+ = 0")
        assert comb_df4 == 0 and comb_g4 == 2 * gb[('-', 1, '+')]

    elif n == 2:
        print("\n--- Canonical Obstructions for n=2 (C(3)) ---")
        # Mode 1:
        print("  [Obstruction 2 (j=1): gb_+_1_+]")
        df2a_1 = compute_delta_f("F_p_1_p", "F_p_1_m", "F_p_1_m")
        g2a_1 = gamma[("F_p_1_p", "F_p_1_m")]["F_p_1_m"]
        df2b_1 = compute_delta_f("F_p_1_m", "E_2d_1", "H_2")
        g2b_1 = gamma[("F_p_1_m", "E_2d_1")]["H_2"]
        c_df2_1 = sp.simplify(df2a_1 - df2b_1)
        c_g2_1 = sp.simplify(g2a_1 - g2b_1)
        print("    delta_f comb =", c_df2_1)
        print("    gamma comb =", c_g2_1)
        print("    =>", c_g2_1, "= 0  ==>  gb_+_1_+ = 0")
        assert c_df2_1 == 0 and c_g2_1 == -2 * gb[('+', 1, '+')]

        print("  [Obstruction 3 (j=1): gb_-_1_-]")
        df3a_1 = compute_delta_f("F_m_1_p", "F_m_1_m", "F_m_1_p")
        g3a_1 = gamma[("F_m_1_p", "F_m_1_m")]["F_m_1_p"]
        df3b_1 = compute_delta_f("F_m_1_p", "E_-2d_1", "H_2")
        g3b_1 = gamma[("F_m_1_p", "E_-2d_1")]["H_2"]
        c_df3_1 = sp.simplify(df3a_1 - df3b_1)
        c_g3_1 = sp.simplify(g3a_1 - g3b_1)
        print("    delta_f comb =", c_df3_1)
        print("    gamma comb =", c_g3_1)
        print("    =>", c_g3_1, "= 0  ==>  gb_-_1_- = 0")
        assert c_df3_1 == 0 and c_g3_1 == -2 * gb[('-', 1, '-')]

        print("  [Obstruction 4 (j=1): gb_-_1_+]")
        df4a_1 = compute_delta_f("F_m_1_p", "F_m_1_p", "F_m_1_p")
        g4a_1 = gamma[("F_m_1_p", "F_m_1_p")]["F_m_1_p"]
        df4b_1 = compute_delta_f("F_m_1_p", "H_2", "H_2")
        g4b_1 = gamma[("F_m_1_p", "H_2")]["H_2"]
        c_df4_1 = sp.simplify(sp.Rational(-1, 2) * df4a_1 + df4b_1)
        c_g4_1 = sp.simplify(sp.Rational(-1, 2) * g4a_1 + g4b_1)
        print("    delta_f comb =", c_df4_1)
        print("    gamma comb =", c_g4_1)
        print("    =>", c_g4_1, "= 0  ==>  gb_-_1_+ = 0")
        assert c_df4_1 == 0 and c_g4_1 == 2 * gb[('-', 1, '+')]

        # Mode 2:
        print("  [Obstruction 2 (j=2): gb_+_2_+]")
        df2a_2 = compute_delta_f("F_p_2_p", "F_p_2_m", "F_p_2_m")
        g2a_2 = gamma[("F_p_2_p", "F_p_2_m")]["F_p_2_m"]
        df2b_2_sum = sum(compute_delta_f("F_p_2_m", "E_2d_2", f"H_{k}") for k in range(1, 4))
        g2b_2_sum = sum(gamma[("F_p_2_m", "E_2d_2")][f"H_{k}"] for k in range(1, 4))
        c_df2_2 = sp.simplify(df2a_2 + df2b_2_sum)
        c_g2_2 = sp.simplify(g2a_2 + g2b_2_sum)
        print("    delta_f comb =", c_df2_2)
        print("    gamma comb =", c_g2_2)
        print("    =>", c_g2_2, "= 0  ==>  gb_+_2_+ = 0")
        assert c_df2_2 == 0 and c_g2_2 == -2 * gb[('+', 2, '+')]

        print("  [Obstruction 3 (j=2): gb_-_2_-]")
        df3a_2 = compute_delta_f("F_m_2_p", "F_m_2_m", "F_m_2_p")
        g3a_2 = gamma[("F_m_2_p", "F_m_2_m")]["F_m_2_p"]
        df3b_2_sum = sum(compute_delta_f("F_m_2_p", "E_-2d_2", f"H_{k}") for k in range(1, 4))
        g3b_2_sum = sum(gamma[("F_m_2_p", "E_-2d_2")][f"H_{k}"] for k in range(1, 4))
        c_df3_2 = sp.simplify(df3a_2 + df3b_2_sum)
        c_g3_2 = sp.simplify(g3a_2 + g3b_2_sum)
        print("    delta_f comb =", c_df3_2)
        print("    gamma comb =", c_g3_2)
        print("    =>", c_g3_2, "= 0  ==>  gb_-_2_- = 0")
        assert c_df3_2 == 0 and c_g3_2 == -2 * gb[('-', 2, '-')]

        print("  [Obstruction 4 (j=2): gb_-_2_+]")
        df_A = compute_delta_f("F_m_1_p", "F_p_2_p", "F_p_1_p")
        g_A = gamma[("F_m_1_p", "F_p_2_p")]["F_p_1_p"]
        df_B = compute_delta_f("F_m_1_p", "E_dp_d_1_2", "E_2d_1")
        g_B = gamma[("F_m_1_p", "E_dp_d_1_2")]["E_2d_1"]
        c_df4_2 = sp.simplify(-2 * df_A + df_B)
        c_g4_2 = sp.simplify(-2 * g_A + g_B)
        print("    delta_f comb =", c_df4_2)
        print("    gamma comb =", c_g4_2)
        print("    =>", c_g4_2, "= 0  ==>  gb_-_2_+ = 0")
        assert c_df4_2 == 0 and c_g4_2 == 4 * gb[('-', 2, '+')]

if __name__ == '__main__':
    verify_minimal_obstructions(1)
    verify_minimal_obstructions(2)
