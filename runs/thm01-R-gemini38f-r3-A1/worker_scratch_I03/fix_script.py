with open('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/brain/1513f3e6-1c5c-4a71-9d5d-5ebc26f33f26/scratch/test_algebra.py', 'r') as f:
    text = f.read()

bad = 'w_coeffs[0] = {f"H_{j}": -c for f"H_{j}", c in w_coeffs[1].items()}'
good = 'w_coeffs[0] = {h_name: -c for h_name, c in w_coeffs[1].items()}'
text = text.replace(bad, good)

with open('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r3-A1/.gemini/antigravity-cli/brain/1513f3e6-1c5c-4a71-9d5d-5ebc26f33f26/scratch/test_algebra.py', 'w') as f:
    f.write(text)
