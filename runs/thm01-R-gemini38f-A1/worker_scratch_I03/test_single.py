import sys
sys.path.append('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-A1/.gemini/antigravity-cli/brain/654dfce4-b8df-497b-869d-784f1053ddd2/scratch')
from verify_generators import build_generators, graded_bracket
import sympy as sp

gens, parities = build_generators(1)
h1 = gens['H_1']
e2p = gens['E_2del1_p']
br = graded_bracket(h1, e2p, 0, 0)
print("H_1:", dict(h1.terms))
print("E_2del1_p:", dict(e2p.terms))
print("[H_1, E_2del1_p]:", dict(br.terms))
