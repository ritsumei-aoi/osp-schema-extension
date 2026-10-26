"""
Scratch script to run compute_structure_constants for n=3 and test timing & validity.
"""
import time
from src.C_generators import compute_structure_constants

t0 = time.time()
sc3, schema3 = compute_structure_constants(3)
t1 = time.time()

print(f"n=3 completed in {t1 - t0:.2f} s")
print(f"Non-zero structure constants for n=3: {len(sc3)}")

# Verify skew-supersymmetry on n=3
parity = schema3["parity"]
bracket_dict = {}
for sc in sc3:
    bracket_dict[(sc["X"], sc["Y"], sc["Z"])] = float(sc["coeff"])

valid = True
for sc in sc3:
    X, Y, Z = sc["X"], sc["Y"], sc["Z"]
    pX, pY, pZ = parity[X], parity[Y], parity[Z]
    assert pZ == (pX + pY) % 2
    sign = -1 if (pX * pY) % 2 == 1 else 1
    c_xy = bracket_dict.get((X, Y, Z), 0.0)
    c_yx = bracket_dict.get((Y, X, Z), 0.0)
    if abs(c_yx - (-sign * c_xy)) > 1e-9:
        print(f"Skew-symmetry failed for {X}, {Y}")
        valid = False
        break

print(f"n=3 skew-supersymmetry and parity check: {valid}")
