from verify_generators import build_generators, graded_bracket
gens, parities = build_generators(1)
h1 = gens['H_1']
e2p = gens['E_2del1_p']
br = graded_bracket(h1, e2p, 0, 0)
print("H_1:", h1.terms)
print("E_2del1_p:", e2p.terms)
print("[H_1, E_2del1_p]:", br.terms)
