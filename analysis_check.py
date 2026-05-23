import json

# Definition of C(n+1) generator space basis index labels
# Fermionic: 'a_1+', 'a_1-'
# Bosonic: 'b_1+', 'b_1-', ..., 'b_n+', 'b_n-'

def generate_deformation_data(n):
    # gb parameters indexed by (sigma, j, s) where sigma in {+, -}, j in {1..n}, s in {+, -}
    gb_params = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_params.append(f"gb_{sigma}_{j}_{s}")
    
    # Structure of the inhomogeneous deformation cocycle
    # gamma(X, Y) = [X, Y]_gb - [X, Y]_0
    # The problem asks to check if gamma_gb = delta f for some odd map f.
    
    data = {
        "n": n,
        "gb_parameters": gb_params,
        "triviality_condition": "gamma_gb == delta_f",
        "analysis_notes": "We are testing if for a given set of gb parameters, there exists an odd map f such that the deformation is coboundary."
    }
    return data

if __name__ == "__main__":
    for n in range(1, 4):
        print(f"Data for n={n}:")
        print(json.dumps(generate_deformation_data(n), indent=2))
