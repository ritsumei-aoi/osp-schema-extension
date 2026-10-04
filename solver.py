import sympy as sp
import sys

def solve_for_n(n):
    # gb parameters
    gb = {}
    for sigma in ['+', '-']:
        for j in range(1, n+1):
            for s in ['+', '-']:
                gb[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")

    # oscillators
    # a1+, a1-
    # bk+, bk- for k=1..n
    
    # We will compute the gamma(X, Y) directly using the formula derived:
    # gamma(X, Y) is the kappa coefficient in [X, Y].
    # Let X and Y be expressed as quadratic forms in oscillators.
    # Actually, the quickest way to compute gamma is:
    # For A, B in {a_1^+, a_1^-, b_j^+, b_j^-}:
    # [A, B] = c * kappa + ...
    # We know [b_j^s, a_1^sigma] = -gb_{sigma, j, s} kappa
    # So [a_1^sigma, b_j^s] = gb_{sigma, j, s} kappa.
    # For quadratic terms X = A B, Y = C D:
    # We just need to apply the Leibniz rule, keeping only the kappa part.
    # [A B, C D] = A [B, C] D \pm ... (accounting for parities).
    
    # Let's represent basis elements as tuples of length 2 (A, B) where A,B are oscillator names.
    # Actually, all generators in C(n+1) are symmetric or antisymmetric combinations, or just AB.
    # Let's list the basis of g = C(n+1).
    
    # Parity of oscillators:
    def p(osc):
        return 1 if osc[0] == 'a' else 0
        
    def comm_kappa(osc1, osc2):
        # returns the coefficient of kappa in [osc1, osc2]
        if p(osc1) == 0 and p(osc2) == 1:
            s = osc1[-1]
            j = int(osc1[1:-1])
            sigma = osc2[-1]
            return -gb[(sigma, j, s)]
        elif p(osc1) == 1 and p(osc2) == 0:
            s = osc2[-1]
            j = int(osc2[1:-1])
            sigma = osc1[-1]
            return gb[(sigma, j, s)]
        else:
            return 0
            
    def comm_std(osc1, osc2):
        # standard supercommutator (no kappa)
        if osc1[0] == 'a' and osc2[0] == 'a':
            if osc1 != osc2:
                return 1 # {a+, a-} = 1. Wait, {a-, a+} = 1
            return 0
        if osc1[0] == 'b' and osc2[0] == 'b':
            if osc1[:-1] == osc2[:-1] and osc1 != osc2:
                # [b_j^-, b_j^+] = 1 => b- b+ - b+ b- = 1 => [b-, b+] = 1
                return 1 if osc1[-1] == '-' else -1
            return 0
        return 0

    # ... I will write a better script.
    print("Done")

if __name__ == "__main__":
    solve_for_n(1)
