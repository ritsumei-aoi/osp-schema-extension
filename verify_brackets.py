"""
Test quadratic representation mapping and compute brackets
"""
import sympy as sp
from verify_cn1 import get_algebra

def build_representation_map(alg):
    """
    Map any ordered pair (i, j) of oscillators to a vector in g (coefficients over basis generators).
    """
    n = alg['n']
    num_osc = alg['num_osc']
    dim_g = alg['dim_g']
    generators = alg['generators']
    gen_index = {g['name']: idx for idx, g in enumerate(generators)}
    
    # pair_to_g[(i, j)] = list of (gen_idx, coeff)
    pair_to_g = {}
    
    for i in range(num_osc):
        for j in range(num_osc):
            pi = alg['osc_parities'][i]
            pj = alg['osc_parities'][j]
            name_i = alg['osc_names'][i]
            name_j = alg['osc_names'][j]
            
            vec = [0] * dim_g
            
            # Fermion-fermion
            if i in (0, 1) and j in (0, 1):
                if i == 0 and j == 0:
                    pass # (a1+)^2 = 0
                elif i == 1 and j == 1:
                    pass # (a1-)^2 = 0
                elif i == 0 and j == 1: # a1+ a1- = H_0
                    vec[gen_index['H_0']] = 1
                elif i == 1 and j == 0: # a1- a1+ = 1 - a1+ a1- = - H_0 (mod scalars)
                    vec[gen_index['H_0']] = -1
                    
            # Fermion-boson
            elif i in (0, 1) and j >= 2:
                # a1^sigma b_k^s
                sigma = '+' if i == 0 else '-'
                k = j // 2
                s = '+' if j % 2 == 0 else '-'
                gen_name = f'F_{sigma}eps_{s}d{k}'
                vec[gen_index[gen_name]] = 1
                
            # Boson-fermion
            elif i >= 2 and j in (0, 1):
                # b_k^s a1^sigma = a1^sigma b_k^s (since parity product is 0)
                sigma = '+' if j == 0 else '-'
                k = i // 2
                s = '+' if i % 2 == 0 else '-'
                gen_name = f'F_{sigma}eps_{s}d{k}'
                vec[gen_index[gen_name]] = 1 # (-1)^(0*1) = 1
                
            # Boson-boson
            else:
                k = i // 2
                si = '+' if i % 2 == 0 else '-'
                l = j // 2
                sj = '+' if j % 2 == 0 else '-'
                
                if k == l:
                    if si == '+' and sj == '+':
                        vec[gen_index[f'E_+2d{k}']] = 1
                    elif si == '-' and sj == '-':
                        vec[gen_index[f'E_-2d{k}']] = 1
                    elif si == '+' and sj == '-':
                        vec[gen_index[f'H_{k}']] = 1
                    elif si == '-' and sj == '+':
                        # b- b+ = b+ b- + 1 = H_k (mod scalars)
                        vec[gen_index[f'H_{k}']] = 1
                else:
                    # k != l
                    k_min, l_max = min(k, l), max(k, l)
                    s_kmin = si if k < l else sj
                    s_lmax = sj if k < l else si
                    gen_name = f'E_{s_kmin}d{k_min}{s_lmax}d{l_max}'
                    vec[gen_index[gen_name]] = 1
                    
            pair_to_g[(i, j)] = vec
            
    return pair_to_g

def compute_brackets(alg):
    """
    Compute structure constants C_{ij}^k and deformation constants gamma_{ij}^k(gb).
    """
    dim_g = alg['dim_g']
    generators = alg['generators']
    pair_to_g = build_representation_map(alg)
    p = [g['parity'] for g in generators]
    osc_p = alg['osc_parities']
    omega0 = alg['omega0']
    Omega_def = alg['Omega_def']
    
    # bracket_0[i][j] = vector in g
    # gamma_def[i][j] = vector in g (with gb symbols)
    bracket_0 = [[sp.zeros(dim_g, 1) for _ in range(dim_g)] for _ in range(dim_g)]
    gamma_def = [[sp.zeros(dim_g, 1) for _ in range(dim_g)] for _ in range(dim_g)]
    
    for idx_X, gen_X in enumerate(generators):
        for idx_Y, gen_Y in enumerate(generators):
            # X = sum c_X * u_A u_B
            # Y = sum c_Y * u_C u_D
            for c_X, A, B in gen_X['terms']:
                for c_Y, C, D in gen_Y['terms']:
                    pA, pB, pC, pD = osc_p[A], osc_p[B], osc_p[C], osc_p[D]
                    pY = gen_Y['parity']
                    
                    # 4 terms in supercommutator [uA uB, uC uD]:
                    # Term 1: [uB, uC] uA uD
                    # Term 2: (-1)^(pB pC) [uB, uD] uA uC
                    # Term 3: (-1)^(pB pC) [uA, uC] uB uD
                    # Term 4: (-1)^(pB pD + pA pC) [uA, uD] uB uC
                    
                    terms = [
                        (omega0[B, C], Omega_def[B, C], 1, A, D),
                        (omega0[B, D], Omega_def[B, D], (-1)**(pB * pC), A, C),
                        (omega0[A, C], Omega_def[A, C], (-1)**(pB * pC), B, D),
                        (omega0[A, D], Omega_def[A, D], (-1)**(pB * pD + pA * pC), B, C),
                    ]
                    
                    for w0, w_def, sign, u1, u2 in terms:
                        vec = pair_to_g[(u1, u2)]
                        # Add to bracket_0
                        if w0 != 0:
                            for k in range(dim_g):
                                if vec[k] != 0:
                                    bracket_0[idx_X][idx_Y][k] += c_X * c_Y * sign * w0 * vec[k]
                        # Add to gamma_def
                        if w_def != 0:
                            for k in range(dim_g):
                                if vec[k] != 0:
                                    gamma_def[idx_X][idx_Y][k] += c_X * c_Y * sign * w_def * vec[k]
                                    
    return bracket_0, gamma_def

alg1 = get_algebra(1)
b0, gdef = compute_brackets(alg1)
print("n=1 computed successfully!")
