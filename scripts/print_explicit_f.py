"""
Print explicit formulas for f for each basis deformation parameter for n=1 and n=2.
"""
from general_solver import run_verification

res1 = run_verification(1)
print("\n=== Explicit f for n=1 ===")
for p, f in res1['solutions'].items():
    print(f"Parameter {p}:")
    for (src, tgt), val in sorted(f.items()):
        print(f"  f({src:10s}) = {str(val):8s} * {tgt}")

res2 = run_verification(2)
print("\n=== Explicit f for n=2 ===")
for p, f in res2['solutions'].items():
    print(f"Parameter {p}:")
    for (src, tgt), val in sorted(f.items()):
        print(f"  f({src:10s}) = {str(val):8s} * {tgt}")
