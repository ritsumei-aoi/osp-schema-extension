"""Quick consistency check for Schema 2 gamma files."""
import json, os
DATA = os.path.join(os.path.dirname(__file__), "..", "data")

for n in [1, 2, 3]:
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)

    gc = s2["inhomogeneous_deformation"]["gamma_coefficients"]
    valid_gb = {p["label"] for p in s2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]}
    basis_all = set(s1["basis"]["even"] + s1["basis"]["odd"] + ["K"])

    invalid_Z = [e for e in gc if e["Z"] not in basis_all]
    print(f"n={n}: {4*n} gb params, {len(gc)} gamma entries, invalid_Z={len(invalid_Z)}")
    if invalid_Z:
        for e in invalid_Z[:3]:
            print(f"  BAD: {e}")
print("Done.")
