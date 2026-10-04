from oscillator_algebra import OscillatorAlgebra
import sympy as sp

alg = OscillatorAlgebra(1)
for i in range(alg.dim):
    b1, p1 = alg.basis[i]
    for j in range(alg.dim):
        b2, p2 = alg.basis[j]
        bracket_dict = alg.superbracket(b1, p1, b2, p2)
        target_k1 = {k[1]: v for k, v in bracket_dict.items() if k[0]}
        if target_k1:
            print(f"[{alg.basis[i][0]}, {alg.basis[j][0]}]_kappa = {target_k1}")
