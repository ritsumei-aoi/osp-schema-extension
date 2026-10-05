import json

def test_gamma_consistency():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            struct = json.load(f)
        with open(f"data/C_{n}_gamma.json") as f:
            gamma = json.load(f)
            
        assert struct["algebra"]["n"] == gamma["algebra"]["n"]
        assert gamma["schema_version"] == "5.0"
        
        # Check gb matrix size
        assert len(gamma["gb_matrix"]["parameters"]) == 4 * n
        
        # Check constants refer to valid basis elements
        basis = set(struct["basis"]["even"] + struct["basis"]["odd"])
        for const in gamma["inhomogeneous_deformation"]["gamma_constants"]:
            assert const["X"] in basis
            assert const["Y"] in basis
            assert const["Z"] in basis
            assert const["gb_term"] in gamma["gb_matrix"]["parameters"]
