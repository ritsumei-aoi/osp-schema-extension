"""
Theoretical analysis and proof verification script.
Explores weight decomposition, cohomology H^2(g, g), and why gamma_gb is non-trivial for any gb != 0.
"""
import sympy as sp
from verify_c_algebra import get_algebra

def analyze_theoretical_proof(n=1):
    basis_elements, names, parities, gb_symbols, struct_consts, gamma_gb = get_algebra(n)
    
    print("=== Analyzing H_0 and sp(2n) brackets ===")
    # Check [H_0, Y] for Y in sp(2n)
    for y in names:
        if y.startswith('h_') or y.startswith('E_+2d') or y.startswith('E_-2d'):
            g = gamma_gb[('H_0', y)]
            print(f"gamma(H_0, {y}) = {g}")
            
    # Check [E_+e+d1, E_-e-d1]
    print("\n=== Analyzing Odd-Odd brackets ===")
    for o1 in names:
        if parities[o1] == 1:
            for o2 in names:
                if parities[o2] == 1:
                    g = gamma_gb[(o1, o2)]
                    if g:
                        print(f"gamma({o1}, {o2}) = {g}")

if __name__ == '__main__':
    analyze_theoretical_proof(1)
