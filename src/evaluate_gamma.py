import json
import fractions

def evaluate_gamma(n, gb_values):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
        
    # Combine schema 1 and gamma
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema1 = json.load(f)
        
    brackets = {}
    
    # 0-th order
    for const in schema1["structure_constants"]:
        x, y, z, coeff = const["X"], const["Y"], const["Z"], const["coeff"]
        brackets[(x, y, z)] = fractions.Fraction(coeff)
        
    # Gamma terms
    for term in schema2["inhomogeneous_deformation"]:
        x, y, z = term["X"], term["Y"], term["Z"]
        gb = term["gb_parameter"]
        c = fractions.Fraction(term["coeff"])
        
        val = gb_values.get(gb, fractions.Fraction(1))
        brackets[(x, y, z)] = brackets.get((x, y, z), fractions.Fraction(0)) + c * val
        
    constants = []
    for (x, y, z), c in brackets.items():
        if c != 0:
            constants.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": str(c),
                "sign_rule": "graded"
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "gb_profile": gb_values,
        "basis": schema1["basis"],
        "parity": schema1["parity"],
        "structure_constants": constants
    }
    return schema3

if __name__ == "__main__":
    for n in [1, 2, 3]:
        # get all gb parameters
        with open(f"data/C_{n}_gamma.json", "r") as f:
            schema2 = json.load(f)
            gbs = set(t["gb_parameter"] for t in schema2["inhomogeneous_deformation"])
            
        # assignment: all 1
        gb_values = {gb: 1 for gb in gbs}
        
        s3 = evaluate_gamma(n, gb_values)
        out_name = f"data/C_{n}_evaluated_all1.json"
        with open(out_name, "w") as f:
            json.dump(s3, f, indent=2)
        print(f"n={n}: Evaluated structure with {len(s3['structure_constants'])} brackets.")
