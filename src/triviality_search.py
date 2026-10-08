import json

def compare_layers(n):
    with open(f"data/C_{n}_evaluated.json") as f:
        eval_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        cob_data = json.load(f)
    
    # We compare the lengths of the coefficient arrays
    len_eval = len(eval_data.get("evaluated_gamma_coefficients", []))
    len_cob = len(cob_data["coboundary_structure"].get("delta_f_coefficients", []))
    
    return len_eval == len_cob

if __name__ == "__main__":
    for n in [1, 2, 3]:
        match = compare_layers(n)
        print(f"n={n}: Match={match}")
