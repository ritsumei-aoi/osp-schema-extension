import json
import os
import sys

def build_coboundary_schema(n):
    path = f'data/C_{n}_structure.json'
    with open(path, 'r') as f:
        data = json.load(f)
        
    parity = data['parity']
    struct = data['structure_constants']
    basis_odd = data['basis']['odd']
    basis_even = data['basis']['even']
    basis = basis_odd + basis_even
    
    def get_bracket(x, y):
        key = f"{x},{y}"
        if key in struct:
            return struct[key]
        return {}

    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # Let f(Z) = sum_c phi_{c}_{Z} c
    # Then [X, f(Y)] = sum_c phi_{c}_{Y} [X, c]
    # And f([X, Y]) = sum_c f( c_i Z_i ) = sum_i c_i f(Z_i) = sum_i c_i sum_d phi_{d}_{Z_i} d
    
    delta_f_struct = {}
    
    for x in basis:
        for y in basis:
            pX = parity.get(x, 0)
            pY = parity.get(y, 0)
            
            res_terms = {} # dict of (generator, phi_name) -> coef
            
            # Term 1: (-1)^{p(X)} [X, f(Y)]
            # f(Y) = sum_{c} phi_{c}_{Y} c
            sign1 = -1 if pX == 1 else 1
            for c in basis:
                pC = parity.get(c, 0)
                if pC != pY: # f is odd
                    br = get_bracket(x, c)
                    for res_gen, coef in br.items():
                        phi_name = f"phi_{c}_{y}"
                        key = (res_gen, phi_name)
                        res_terms[key] = res_terms.get(key, 0.0) + sign1 * coef
                        
            # Term 2: - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
            power = (pX + 1) * pY
            sign2 = -1 if power % 2 == 1 else 1
            for c in basis:
                pC = parity.get(c, 0)
                if pC != pX:
                    br = get_bracket(y, c)
                    for res_gen, coef in br.items():
                        phi_name = f"phi_{c}_{x}"
                        key = (res_gen, phi_name)
                        res_terms[key] = res_terms.get(key, 0.0) - sign2 * coef
                        
            # Term 3: - f([X, Y])
            # [X, Y] = sum_k c_k Z_k
            # - f(sum_k c_k Z_k) = sum_k -c_k f(Z_k) = sum_k sum_d -c_k phi_{d}_{Z_k} d
            br_xy = get_bracket(x, y)
            for z_k, c_k in br_xy.items():
                pZk = parity.get(z_k, 0)
                for d in basis:
                    pD = parity.get(d, 0)
                    if pD != pZk:
                        phi_name = f"phi_{d}_{z_k}"
                        key = (d, phi_name)
                        res_terms[key] = res_terms.get(key, 0.0) - c_k
                        
            # Aggregate into schema structure:
            # { "res_gen": { "phi_name": coef, ... }, ... }
            out_expr = {}
            for (res_gen, phi_name), coef in res_terms.items():
                if abs(coef) > 1e-9:
                    if res_gen not in out_expr:
                        out_expr[res_gen] = {}
                    out_expr[res_gen][phi_name] = coef
                    
            if out_expr:
                delta_f_struct[f"{x},{y}"] = out_expr
                
    schema = {
        "schema_version": "5.0",
        "algebra": data["algebra"],
        "coboundary_structure": {
            "description": "Coboundary operator delta f applied to basis pairs",
            "delta_f_constants": delta_f_struct
        },
        "metadata": {
            "description": f"Schema 4 for C({n+1}) = osp(2|{2*n}) coboundary"
        }
    }
    return schema

if __name__ == '__main__':
    for n in [1, 2, 3]:
        schema = build_coboundary_schema(n)
        out_path = f'data/C_{n}_coboundary.json'
        with open(out_path, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {out_path}")
