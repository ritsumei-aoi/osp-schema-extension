import sympy as sp
from itertools import product
import json

def get_osc_parity(osc):
    # osc is ('a', '+/-') or ('b', j, '+/-')
    return 1 if osc[0] == 'a' else 0

def osc_to_str(osc):
    if osc[0] == 'a':
        return f"a^{osc[1]}"
    else:
        return f"b_{osc[1]}^{osc[2]}"

def standard_bracket_osc(u, v):
    # Returns scalar c such that [u, v]_0 = c
    # [u, v]_0 = u v - (-1)^{p(u)p(v)} v u
    pu = get_osc_parity(u)
    pv = get_osc_parity(v)
    
    if pu == 1 and pv == 1:
        # {a^-, a^+} = 1
        if (u[1] == '-' and v[1] == '+') or (u[1] == '+' and v[1] == '-'):
            return 1
        return 0
    elif pu == 0 and pv == 0:
        # [b_j^-, b_k^+] = \delta_{jk}
        # [b_k^+, b_j^-] = -\delta_{jk}
        if u[1] == v[1]:
            if u[2] == '-' and v[2] == '+':
                return 1
            elif u[2] == '+' and v[2] == '-':
                return -1
        return 0
    else:
        return 0

def deformed_bracket_osc(u, v, gb_dict):
    # Returns (c_0, c_kappa) such that [u, v] = c_0 + c_kappa * \kappa
    c0 = standard_bracket_osc(u, v)
    
    pu = get_osc_parity(u)
    pv = get_osc_parity(v)
    
    c_kappa = 0
    if pu == 0 and pv == 1:
        # u is b_j^s, v is a^\sigma
        # [b_j^s, a^\sigma] = - gb_{\sigma, j, s} * \kappa
        j = u[1]
        s = u[2]
        sigma = v[1]
        c_kappa = - gb_dict[(sigma, j, s)]
    elif pu == 1 and pv == 0:
        # u is a^\sigma, v is b_j^s
        # [a^\sigma, b_j^s] = - (-1)^{1*0} [b_j^s, a^\sigma] = - (- gb_{\sigma, j, s} \kappa) = gb_{\sigma, j, s} \kappa
        sigma = u[1]
        j = v[1]
        s = v[2]
        c_kappa = gb_dict[(sigma, j, s)]
        
    return c0, c_kappa

def reduce_pair_to_basis(u, v, n, basis_map):
    # Reduces a quadratic oscillator pair u*v (modulo central scalars) into a vector in basis
    # basis_map: name -> index
    dim = len(basis_map)
    vec = [0] * dim
    
    pu = get_osc_parity(u)
    pv = get_osc_parity(v)
    
    if pu == 1 and pv == 1:
        # Fermionic pair:
        if u[1] == '+' and v[1] == '-':
            # a^+ a^- = H_0
            vec[basis_map['H_0']] += 1
        elif u[1] == '-' and v[1] == '+':
            # a^- a^+ = 1 - a^+ a^- = - H_0 (mod scalars)
            vec[basis_map['H_0']] -= 1
        else:
            # (a^+)^2 = 0, (a^-)^2 = 0
            pass
    elif pu == 1 and pv == 0:
        # a^\sigma b_j^s -> directly odd basis generator
        sigma = u[1]
        j = v[1]
        s = v[2]
        name = f"E_{sigma}e{s}d{j}"
        vec[basis_map[name]] += 1
    elif pu == 0 and pv == 1:
        # b_j^s a^\sigma = a^\sigma b_j^s (mod kappa, but here we reduce the oscillator monomial)
        sigma = v[1]
        j = u[1]
        s = u[2]
        name = f"E_{sigma}e{s}d{j}"
        vec[basis_map[name]] += 1
    else:
        # Bosonic pair: u = ('b', j, s1), v = ('b', k, s2)
        j, s1 = u[1], u[2]
        k, s2 = v[1], v[2]
        
        if s1 == '+' and s2 == '+':
            if j == k:
                # (b_j^+)^2 = 2 * E_+2d_j
                vec[basis_map[f"E_+2d_{j}"]] += 2
            else:
                j_min, k_max = min(j, k), max(j, k)
                vec[basis_map[f"E_+d{j_min}+d{k_max}"]] += 1
        elif s1 == '-' and s2 == '-':
            if j == k:
                # (b_j^-)^2 = 2 * E_-2d_j
                vec[basis_map[f"E_-2d_{j}"]] += 2
            else:
                j_min, k_max = min(j, k), max(j, k)
                vec[basis_map[f"E_-d{j_min}-d{k_max}"]] += 1
        elif s1 == '+' and s2 == '-':
            if j == k:
                # b_j^+ b_j^- = N_j
                vec[basis_map[f"N_{j}"]] += 1
            else:
                # b_j^+ b_k^- with j < k or j > k
                if j < k:
                    vec[basis_map[f"E_+d{j}-d{k}"]] += 1
                else:
                    vec[basis_map[f"E_-d{k}+d{j}"]] += 1
        elif s1 == '-' and s2 == '+':
            if j == k:
                # b_j^- b_j^+ = b_j^+ b_j^- + 1 = N_j (mod scalars)
                vec[basis_map[f"N_{j}"]] += 1
            else:
                # b_j^- b_k^+ = b_k^+ b_j^-
                if k < j:
                    vec[basis_map[f"E_+d{k}-d{j}"]] += 1
                else:
                    vec[basis_map[f"E_-d{j}+d{k}"]] += 1
                    
    return vec

print("Reduction helper defined.")
