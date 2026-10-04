"""
General solver and verifier for C(n+1) = osp(2|2n) inhomogeneous deformation triviality.
Supports n = 1, 2, 3.
"""
import sympy as sp
from itertools import product

def setup_algebra(n):
    # Oscillators:
    # 0: a_p (a_1^+), 1: a_m (a_1^-) [fermionic, parity 1]
    # For k = 1..n:
    # 2*k: b_k^+, 2*k+1: b_k^- [bosonic, parity 0]
    
    num_osc = 2 + 2 * n
    parities = [1, 1] + [0] * (2 * n)
    osc_names = ['a_p', 'a_m']
    for k in range(1, n + 1):
        osc_names.extend([f'b_{k}p', f'b_{k}m'])
        
    # Undeformed brackets c0[(i, j)]
    c0 = { (i, j): sp.Rational(0) for i in range(num_osc) for j in range(num_osc) }
    # {a_m, a_p} = 1
    c0[(1, 0)] = sp.Rational(1)
    c0[(0, 1)] = sp.Rational(1)
    # [b_k^-, b_k^+] = 1, [b_k^+, b_k^-] = -1
    for k in range(1, n + 1):
        bp = 2 * k
        bm = 2 * k + 1
        c0[(bm, bp)] = sp.Rational(1)
        c0[(bp, bm)] = sp.Rational(-1)
        
    # Deformed parameters:
    # 4n parameters: gb_{sigma, k, s} for sigma in {p, m}, k in 1..n, s in {p, m}
    gb_list = []
    gb_map = {}
    for k in range(1, n + 1):
        for sigma in ['p', 'm']:
            for s in ['p', 'm']:
                param_name = f'gb_{sigma}_{k}_{s}'
                gb_list.append(param_name)
                gb_map[(sigma, k, s)] = param_name
                
    # Define basis generators of g = osp(2|2n)
    # Each generator: list of (u1, u2, coeff), const_term, parity
    generators = {}
    
    # 1. so(2) generator: J = a_p a_m - 1/2
    generators['J'] = ([(0, 1, sp.Rational(1))], sp.Rational(-1, 2), 0)
    
    # 2. sp(2n) generators:
    # For each k in 1..n:
    # H_k = b_kp b_km + 1/2
    # E_2k = 1/2 (b_kp)^2
    # F_2k = 1/2 (b_km)^2
    for k in range(1, n + 1):
        bp = 2 * k
        bm = 2 * k + 1
        generators[f'H_{k}'] = ([(bp, bm, sp.Rational(1))], sp.Rational(1, 2), 0)
        generators[f'E_2d_{k}'] = ([(bp, bp, sp.Rational(1, 2))], sp.Rational(0), 0)
        generators[f'F_2d_{k}'] = ([(bm, bm, sp.Rational(1, 2))], sp.Rational(0), 0)
        
    # Cross terms for sp(2n) (when n >= 2):
    # For 1 <= j < k <= n:
    # b_jp b_kp, b_jp b_km, b_jm b_kp, b_jm b_km
    for j in range(1, n + 1):
        for k in range(j + 1, n + 1):
            jp, jm = 2 * j, 2 * j + 1
            kp, km = 2 * k, 2 * k + 1
            generators[f'E_pp_{j}_{k}'] = ([(jp, kp, sp.Rational(1))], sp.Rational(0), 0)
            generators[f'E_pm_{j}_{k}'] = ([(jp, km, sp.Rational(1))], sp.Rational(0), 0)
            generators[f'E_mp_{j}_{k}'] = ([(jm, kp, sp.Rational(1))], sp.Rational(0), 0)
            generators[f'E_mm_{j}_{k}'] = ([(jm, km, sp.Rational(1))], sp.Rational(0), 0)
            
    # 3. Odd generators (4n total):
    # For k in 1..n:
    # a_p b_kp, a_p b_km, a_m b_kp, a_m b_km
    for k in range(1, n + 1):
        bp, bm = 2 * k, 2 * k + 1
        generators[f'F_pp_{k}'] = ([(0, bp, sp.Rational(1))], sp.Rational(0), 1)
        generators[f'F_pm_{k}'] = ([(0, bm, sp.Rational(1))], sp.Rational(0), 1)
        generators[f'F_mp_{k}'] = ([(1, bp, sp.Rational(1))], sp.Rational(0), 1)
        generators[f'F_mm_{k}'] = ([(1, bm, sp.Rational(1))], sp.Rational(0), 1)
        
    even_gens = [g for g, v in generators.items() if v[2] == 0]
    odd_gens = [g for g, v in generators.items() if v[2] == 1]
    gen_list = even_gens + odd_gens
    
    print(f"\n--- Setup for n={n} ---")
    print(f"dim(even) = {len(even_gens)}, dim(odd) = {len(odd_gens)}, total = {len(gen_list)}")
    print(f"Number of gb parameters = {len(gb_list)}")
    
    # Normal order reduction:
    # maps any pair (i, j) of oscillators to a linear combination of generators + constant
    def normal_order(pair_dict):
        res = {g: sp.Rational(0) for g in gen_list}
        const = sp.Rational(0)
        for (i, j), coeff in pair_dict.items():
            if coeff == 0: continue
            # Fermionic:
            if (i, j) == (0, 1): # a_p a_m = J + 1/2
                res['J'] += coeff
                const += coeff * sp.Rational(1, 2)
            elif (i, j) == (1, 0): # a_m a_p = 1 - a_p a_m = -J + 1/2
                res['J'] -= coeff
                const += coeff * sp.Rational(1, 2)
            elif i in [0, 1] and j in [0, 1]:
                # a_p^2 = 0, a_m^2 = 0
                pass
            # Boson-Boson same index k:
            elif i >= 2 and j >= 2:
                ki, si = i // 2, i % 2 # si: 0 is p, 1 is m
                kj, sj = j // 2, j % 2
                if ki == kj:
                    if si == 0 and sj == 0: # b_kp^2 = 2 * E_2d_k
                        res[f'E_2d_{ki}'] += coeff * 2
                    elif si == 1 and sj == 1: # b_km^2 = 2 * F_2d_k
                        res[f'F_2d_{ki}'] += coeff * 2
                    elif si == 0 and sj == 1: # b_kp b_km = H_k - 1/2
                        res[f'H_{ki}'] += coeff
                        const -= coeff * sp.Rational(1, 2)
                    elif si == 1 and sj == 0: # b_km b_kp = b_kp b_km + 1 = H_k + 1/2
                        res[f'H_{ki}'] += coeff
                        const += coeff * sp.Rational(1, 2)
                else:
                    # ki != kj
                    j_min, k_max = min(ki, kj), max(ki, kj)
                    s_min = si if ki < kj else sj
                    s_max = sj if ki < kj else si
                    s_str = ('p' if s_min == 0 else 'm') + ('p' if s_max == 0 else 'm')
                    res[f'E_{s_str}_{j_min}_{k_max}'] += coeff
            # Fermion-Boson:
            else:
                # one is in {0, 1}, one >= 2
                if i in [0, 1]:
                    fi, bi = i, j
                else:
                    fi, bi = j, i
                sig = 'p' if fi == 0 else 'm'
                kb, sb = bi // 2, bi % 2
                s_b = 'p' if sb == 0 else 'm'
                res[f'F_{sig}{s_b}_{kb}'] += coeff
        return res, const

    return {
        'n': n,
        'parities': parities,
        'c0': c0,
        'gb_list': gb_list,
        'gb_map': gb_map,
        'generators': generators,
        'even_gens': even_gens,
        'odd_gens': odd_gens,
        'gen_list': gen_list,
        'normal_order': normal_order
    }

print("Algebra setup function defined.")
