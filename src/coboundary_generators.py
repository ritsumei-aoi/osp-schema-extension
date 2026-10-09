import json
import os
from collections import defaultdict

def generate_coboundary(n):
    with open(f"data/C_{n}_structure.json") as f:
        schema1 = json.load(f)
        
    basis_even = schema1["basis"]["even"]
    basis_odd = schema1["basis"]["odd"]
    parity = schema1["parity"]
    all_gens = basis_even + basis_odd
    
    C = defaultdict(float)
    for entry in schema1["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = float(entry["coeff"])
        C[(x, y, z)] = c
        if x != y:
            sign = -1 if (parity[x] * parity[y] == 1) else 1
            C[(y, x, z)] = -sign * c
            
    f_parameters = []
    for gen_y in all_gens:
        for gen_x in all_gens:
            if parity[gen_x] != parity[gen_y]:
                # f(Y) = sum_X phi_X_Y * X
                f_parameters.append(f"phi_{gen_x}_{gen_y}")
                
    coboundary_evaluated = []
    
    for i in range(len(all_gens)):
        for j in range(i, len(all_gens)):
            X = all_gens[i]
            Y = all_gens[j]
            px = parity[X]
            py = parity[Y]
            
            # We want to collect terms for each phi parameter.
            # Z' component of df(X, Y)
            # df(X, Y) = (-1)^pX [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X,Y])
            
            # Result is a dict of (Z_out, phi_param) -> coeff
            df_components = defaultdict(float)
            
            # Term 1: (-1)^pX [X, f(Y)]
            # f(Y) = sum_Z phi_{Z, Y} Z
            # [X, Z] = sum_Zout C_{X,Z}^{Zout} Zout
            sign1 = -1 if px == 1 else 1
            for Z in all_gens:
                if parity[Z] != parity[Y]:
                    phi_param = f"phi_{Z}_{Y}"
                    for Zout in all_gens:
                        if (X, Z, Zout) in C:
                            c = C[(X, Z, Zout)]
                            if c != 0:
                                df_components[(Zout, phi_param)] += sign1 * c
                                
            # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
            # f(X) = sum_Z phi_{Z, X} Z
            # [Y, Z] = sum_Zout C_{Y,Z}^{Zout} Zout
            sign2 = -1 if ((px + 1) * py) % 2 == 1 else 1
            for Z in all_gens:
                if parity[Z] != parity[X]:
                    phi_param = f"phi_{Z}_{X}"
                    for Zout in all_gens:
                        if (Y, Z, Zout) in C:
                            c = C[(Y, Z, Zout)]
                            if c != 0:
                                df_components[(Zout, phi_param)] -= sign2 * c
                                
            # Term 3: - f([X, Y])
            # [X, Y] = sum_W C_{X,Y}^W W
            # f(W) = sum_Zout phi_{Zout, W} Zout
            for W in all_gens:
                if (X, Y, W) in C:
                    c_xyw = C[(X, Y, W)]
                    if c_xyw != 0:
                        for Zout in all_gens:
                            if parity[Zout] != parity[W]:
                                phi_param = f"phi_{Zout}_{W}"
                                df_components[(Zout, phi_param)] -= c_xyw
                                
            for (Zout, phi_param), c in df_components.items():
                if abs(c) > 1e-9:
                    val_str = str(int(c)) if c.is_integer() else str(c)
                    coboundary_evaluated.append({
                        "X": X,
                        "Y": Y,
                        "Z": Zout,
                        "phi_param": phi_param,
                        "coeff": val_str
                    })
                    
    schema4 = {
        "schema_version": "5.0",
        "algebra_ref": f"C({n+1})",
        "f_parameters": f_parameters,
        "coboundary_evaluated": coboundary_evaluated,
        "metadata": {
            "generated_by": "coboundary_generators.py"
        }
    }
    
    with open(f"data/C_{n}_coboundary.json", "w") as f:
        json.dump(schema4, f, indent=2)
    print(f"Generated data/C_{n}_coboundary.json")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        generate_coboundary(n)
