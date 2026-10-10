import json
import os
import sys

def evaluate_schema(n):
    path = f'data/C_{n}_gamma.json'
    with open(path, 'r') as f:
        data = json.load(f)
        
    evaluated_struct = {}
    gamma_struct = data['inhomogeneous_deformation']['gamma_structure_constants']
    
    # We set all gb_xxx to 1.0
    for key, expr in gamma_struct.items():
        eval_expr = {}
        for gen, gb_dict in expr.items():
            # gb_dict is a mapping from gb_name to coefficient
            val = sum(coef * 1.0 for gb_name, coef in gb_dict.items())
            if abs(val) > 1e-9:
                eval_expr[gen] = val
        if eval_expr:
            evaluated_struct[key] = eval_expr
            
    schema = {
        "schema_version": "5.0",
        "algebra": data["algebra"],
        "evaluated_deformation": {
            "gb_assignment": "all_plus_one",
            "gb_values": {
                f"gb_{sigma}_{j}_{s}": 1.0 
                for sigma in ('p', 'm') 
                for j in range(1, n+1) 
                for s in ('p', 'm')
            },
            "evaluated_gamma_structure_constants": evaluated_struct
        },
        "metadata": {
            "description": f"Schema 3 for C({n+1}) = osp(2|{2*n}) with evaluated gamma (all_plus_one)"
        }
    }
    return schema

if __name__ == '__main__':
    for n in [1, 2, 3]:
        schema = evaluate_schema(n)
        out_path = f'data/C_{n}_evaluated.json'
        with open(out_path, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {out_path}")
