import sympy as sp
from solve_triviality_n1 import sol, phi, all_phi_vars, even_gens, odd_gens, gen_list

# Set free parameters to 0
free_vars = [v for v in all_phi_vars if v not in sol]
print("Free variables in f:", free_vars)

subs_zero = {v: 0 for v in free_vars}
particular_sol = {k: sp.simplify(v.subs(subs_zero)) for k, v in sol.items()}

print("\nParticular solution for f (mapping even to odd, and odd to even):")
for (src, tgt), var in phi.items():
    val = particular_sol.get(var, 0)
    if val != 0:
        print(f"f({src}) -> {tgt}: {val}")
