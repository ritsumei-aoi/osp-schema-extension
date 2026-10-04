import sympy as sp

def run_test(n):
    print(f"Running for n={n}")
    
    # We will build a linear system for the coefficients of f
    # f: g -> g is an odd linear map
    # We will represent generators abstractly.
    
    # Let's write a simple associative algebra evaluator for the oscillators
    # Generators of U(A): a1_p, a1_m, b_j_p, b_j_m (j=1..n), kappa
    # We want to represent elements as linear combinations of words in normal form.
    # Normal form order: kappa, a1_p, a1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m.
    # Commutation relations:
    # {a1_m, a1_p} = 1 -> a1_m a1_p = 1 - a1_p a1_m
    # [b_j_m, b_j_p] = 1 -> b_j_m b_j_p = 1 + b_j_p b_j_m
    # [b_j_s, a1_sigma] = -gb_{sigma, j, s} kappa
    # -> b_j_s a1_sigma = a1_sigma b_j_s - gb_{sigma, j, s} kappa
    
    pass

run_test(1)
