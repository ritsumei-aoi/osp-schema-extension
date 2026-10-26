with open('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-A1/.gemini/antigravity-cli/brain/654dfce4-b8df-497b-869d-784f1053ddd2/scratch/verify_generators.py', 'r') as f:
    code = f.read()
code = code.replace('(M * sol - v).is_zero()', '(M * sol - v).is_zero')
with open('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-A1/.gemini/antigravity-cli/brain/654dfce4-b8df-497b-869d-784f1053ddd2/scratch/verify_generators.py', 'w') as f:
    f.write(code)
