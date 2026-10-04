"""
Implementation of C(n+1) Lie superalgebra, inhomogeneous deformation,
and coboundary deformation.
"""

import sympy as sp
from sympy import symbols, Matrix, zeros, Rational, simplify

def solve_for_n(n=1):
    print(f"==================================================")
    print(f"Solving for C({n+1}) = osp(2|{2*n})")
    print(f"==================================================")
    
    # 1. Define oscillators
    # Fermions: a1+, a1-
    # Bosons: b_j+, b_j- for j=1..n
    # Each oscillator has an ID and a parity:
    # 0: a1+ (p=1), 1: a1- (p=1)
    # 2*j: bj+ (p=0), 2*j+1: bj- (p=0) for j=1..n
    
    # Let's list oscillators:
    # a+ = ('a', 1, +1)
    # a- = ('a', 1, -1)
    # b+j = ('b', j, +1)
    # b-j = ('b', j, -1)
    
    oscillators = []
    oscillators.append(('a', 1, +1))
    oscillators.append(('a', 1, -1))
    for j in range(1, n+1):
        oscillators.append(('b', j, +1))
        oscillators.append(('b', j, -1))
        
    def osc_parity(osc):
        return 1 if osc[0] == 'a' else 0
        
    def osc_name(osc):
        sign = '+' if osc[2] == +1 else '-'
        return f"{osc[0]}_{osc[1]}^{sign}"

    print("Oscillators:", [osc_name(o) for o in oscillators])
    
    # Define gb parameters:
    # gb_{sigma, j, s}
    # indexed by sigma in {+1, -1}, j in 1..n, s in {+1, -1}
    gb_vars = {}
    for sigma in [+1, -1]:
        sig_str = '+' if sigma == +1 else '-'
        for j in range(1, n+1):
            for s in [+1, -1]:
                s_str = '+' if s == +1 else '-'
                var_name = f"gb_{sig_str}_{j}_{s_str}"
                gb_vars[(sigma, j, s)] = symbols(var_name)
                
    print(f"Number of gb parameters: {len(gb_vars)} (expected {4*n})")
    
    # Commutation relations in A:
    # [u, v] = C0(u, v) * K + C1(u, v) * kappa
    # [b_j^-, b_k^+] = delta_jk * K  => [b-, b+] = 1, [b+, b-] = -1
    # {a1^-, a1^+} = K               => [a-, a+] = 1, [a+, a-] = 1 (supercommutator)
    # [b_j^s, a1^sigma] = - gb_{sigma, j, s} * kappa
    # [a1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa
    
    def comm_0(u, v):
        # returns scalar for K
        # u, v are oscillators
        if u[0] == 'a' and v[0] == 'a':
            # {a-, a+} = 1
            if u[2] == -1 and v[2] == +1:
                return Rational(1)
            elif u[2] == +1 and v[2] == -1:
                return Rational(1) # because [a+, a-] = a+ a- - (-1) a- a+ = a+ a- + a- a+ = 1
            else:
                return Rational(0)
        elif u[0] == 'b' and v[0] == 'b':
            if u[1] == v[1]:
                # [b-, b+] = 1, [b+, b-] = -1
                if u[2] == -1 and v[2] == +1:
                    return Rational(1)
                elif u[2] == +1 and v[2] == -1:
                    return Rational(-1)
                else:
                    return Rational(0)
            else:
                return Rational(0)
        else:
            return Rational(0)
            
    def comm_1(u, v):
        # returns symbol for kappa
        # [b_j^s, a1^sigma] = - gb_{sigma, j, s} * kappa
        # [a1^sigma, b_j^s] = - (-1)^{1*0} [b_j^s, a1^sigma] = gb_{sigma, j, s} * kappa
        if u[0] == 'b' and v[0] == 'a':
            j = u[1]
            s = u[2]
            sigma = v[2]
            return -gb_vars[(sigma, j, s)]
        elif u[0] == 'a' and v[0] == 'b':
            sigma = u[2]
            j = v[1]
            s = v[2]
            return gb_vars[(sigma, j, s)]
        else:
            return Rational(0)

    # Basis elements of g = C(n+1)
    # Each basis element is represented as a linear combination of pairs of oscillators:
    # list of (coeff, u, v) where u, v in oscillators, and parity p
    basis = []
    basis_names = []
    basis_parities = []
    
    # Even generators:
    # 1. Cartan generators:
    # H_1 = a1+ a1- + b1+ b1-
    h1_terms = [(Rational(1), ('a', 1, +1), ('a', 1, -1)),
                (Rational(1), ('b', 1, +1), ('b', 1, -1))]
    basis.append(h1_terms)
    basis_names.append("H_1")
    basis_parities.append(0)
    
    # H_k = b_{k-1}+ b_{k-1}- - b_k+ b_k- (2 <= k <= n)
    for k in range(2, n+1):
        hk_terms = [(Rational(1), ('b', k-1, +1), ('b', k-1, -1)),
                    (Rational(-1), ('b', k, +1), ('b', k, -1))]
        basis.append(hk_terms)
        basis_names.append(f"H_{k}")
        basis_parities.append(0)
        
    # H_{n+1} = - b_n+ b_n- - 1/2
    # Note: the scalar -1/2 is central, we can track it or represent the oscillator part:
    # Let's keep the oscillator part: - b_n+ b_n- (and track scalar if needed)
    # Wait, in the bracket, scalar does not affect anything, but let's check!
    hn1_terms = [(Rational(-1), ('b', n, +1), ('b', n, -1))]
    basis.append(hn1_terms)
    basis_names.append(f"H_{n+1}")
    basis_parities.append(0)
    
    # 2. Bosonic root generators:
    # E_{2 delta_k} = 1/2 (b_k+)^2
    for k in range(1, n+1):
        basis.append([(Rational(1, 2), ('b', k, +1), ('b', k, +1))])
        basis_names.append(f"E_2delta_{k}")
        basis_parities.append(0)
        
    # E_{-2 delta_k} = 1/2 (b_k-)^2
    for k in range(1, n+1):
        basis.append([(Rational(1, 2), ('b', k, -1), ('b', k, -1))])
        basis_names.append(f"E_-2delta_{k}")
        basis_parities.append(0)
        
    # E_{delta_k - delta_l} = b_k+ b_l- (k != l)
    for k in range(1, n+1):
        for l in range(1, n+1):
            if k != l:
                basis.append([(Rational(1), ('b', k, +1), ('b', l, -1))])
                basis_names.append(f"E_delta_{k}-delta_{l}")
                basis_parities.append(0)
                
    # E_{delta_k + delta_l} = b_k+ b_l+ (k < l)
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            basis.append([(Rational(1), ('b', k, +1), ('b', l, +1))])
            basis_names.append(f"E_delta_{k}+delta_{l}")
            basis_parities.append(0)
            
    # E_{-delta_k - delta_l} = b_k- b_l- (k < l)
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            basis.append([(Rational(1), ('b', k, -1), ('b', l, -1))])
            basis_names.append(f"E_-delta_{k}-delta_{l}")
            basis_parities.append(0)

    dim_even = len(basis)
    print(f"Dimension of even subalgebra: {dim_even} (expected {2*n**2 + n + 1})")
    
    # Odd generators:
    # E_{varepsilon + delta_l} = a1+ b_l+
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, +1), ('b', l, +1))])
        basis_names.append(f"E_eps+delta_{l}")
        basis_parities.append(1)
        
    # E_{varepsilon - delta_l} = a1+ b_l-
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, +1), ('b', l, -1))])
        basis_names.append(f"E_eps-delta_{l}")
        basis_parities.append(1)
        
    # E_{-varepsilon + delta_l} = a1- b_l+
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, -1), ('b', l, +1))])
        basis_names.append(f"E_-eps+delta_{l}")
        basis_parities.append(1)
        
    # E_{-varepsilon - delta_l} = a1- b_l-
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, -1), ('b', l, -1))])
        basis_names.append(f"E_-eps-delta_{l}")
        basis_parities.append(1)
        
    dim_odd = len(basis) - dim_even
    dim_total = len(basis)
    print(f"Dimension of odd space: {dim_odd} (expected {4*n})")
    print(f"Total dimension: {dim_total} (expected {2*n**2 + 5*n + 1})")
    
    return oscillators, gb_vars, basis, basis_names, basis_parities

solve_for_n(1)
solve_for_n(2)
