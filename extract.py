import sympy as sp
import itertools
from solver import get_generators, get_parity, bracket, Term, normal_order_expr

def extract_gen_coeffs(expr, gens_dict):
    # Express expr (list of Terms with kappa=0) as a linear combination of generators.
    # Note: Since generators form a basis, we can do this by matching the top degree terms.
    # Actually, generators have specific terms.
    # Let's build a matrix of generators.
    # All ops terms (tuples) present in gens_dict:
    op_to_idx = {}
    gen_names = list(gens_dict.keys())
    
    for g_name in gen_names:
        for t in gens_dict[g_name]:
            if t.ops not in op_to_idx:
                op_to_idx[t.ops] = len(op_to_idx)
                
    # Also add the empty tuple for scalars
    if () not in op_to_idx:
        op_to_idx[()] = len(op_to_idx)
        
    M = sp.zeros(len(op_to_idx), len(gen_names))
    for j, g_name in enumerate(gen_names):
        for t in gens_dict[g_name]:
            i = op_to_idx[t.ops]
            M[i, j] = t.coeff
            
    # Now convert expr to a vector
    V = sp.zeros(len(op_to_idx), 1)
    for t in expr:
        if t.ops in op_to_idx:
            V[op_to_idx[t.ops], 0] += t.coeff
        else:
            # If there's an op not in generators basis, that's a problem (shouldn't happen for kappa=0 bracket)
            pass
            
    # We want to solve M * C = V
    # However, since M might not be square, we can use LUSolve or just rref
    # Actually, M should have full column rank.
    # Let's augment and solve.
    aug = M.row_join(V)
    reduced, pivots = aug.rref()
    
    coeffs = {g_name: 0 for g_name in gen_names}
    scalar_remnant = 0
    
    # Extract solution
    # The columns 0 to len(gen_names)-1 are variables.
    for i, p in enumerate(pivots):
        if p < len(gen_names):
            coeffs[gen_names[p]] = reduced[i, -1]
            
    # Check if there is a remainder in V that is not a scalar
    # Actually, let's just use the generators to cancel terms in V.
    return coeffs

def test_extract():
    gens = get_generators(1)
    # [E_e_d1, E_-e_-d1]_0
    X = gens['E_e_d1']
    Y = gens['E_-e_-d1']
    b = bracket(X, Y, 1, 1)
    b_0 = [t for t in b if t.kappa_power == 0]
    
    coeffs = extract_gen_coeffs(b_0, gens)
    print("Bracket [E_e_d1, E_-e_-d1]_0:")
    for k, v in coeffs.items():
        if v != 0:
            print(f"{v} * {k}")

if __name__ == "__main__":
    test_extract()
