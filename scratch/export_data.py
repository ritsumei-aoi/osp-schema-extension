import json
import sys

def main():
    data = {
        "algebra": "C(n+1)",
        "basis_types": {
            "even": ["C", "S"],
            "odd": ["F"]
        },
        "brackets": [
            {"X": "C", "Y": "F_k(sigma,s)", "result": "sigma * F_k(sigma,s)"},
            {"X": "S_kl(s1,s2)", "Y": "F_m(sigma,s)", "result": "epsilon(s2,s)*delta_lm*F_k(sigma,s1) + epsilon(s1,s)*delta_km*F_l(sigma,s2)"},
            {"X": "F_k(sigma1,s1)", "Y": "F_l(sigma2,s2)", "result": "delta_{sigma1, -sigma2} * (S_kl(s1,s2) + sigma1 * epsilon(s1,s2) * delta_kl * C)"}
        ],
        "gamma": [
            {"X": "C", "Y": "F_k(sigma,s)", "result": "- gb(sigma,k,s) * C"},
            {"X": "S_kl(s1,s2)", "Y": "F_m(sigma,s)", "result": "- gb(sigma,k,s1) * S_lm(s2,s) - gb(sigma,l,s2) * S_km(s1,s)"},
            {"X": "F_k(sigma1,s1)", "Y": "F_l(sigma2,s2)", "result": "gb(sigma2,k,s1) * F_l(sigma1,s2) + gb(sigma1,l,s2) * F_k(sigma2,s1)"}
        ],
        "epsilon": {
            "+,-": -1,
            "-,+": 1,
            "+,+": 0,
            "-,-": 0
        },
        "triviality_conditions": {
            "n1": ["gb_+,1,+ == 0", "gb_+,1,- == 0", "gb_-,1,+ == 0", "gb_-,1,- == 0"],
            "n2": ["gb_+,1,+ == 0", "gb_+,1,- == 0", "gb_+,2,+ == 0", "gb_+,2,- == 0", "gb_-,1,+ == 0", "gb_-,1,- == 0", "gb_-,2,+ == 0", "gb_-,2,- == 0"],
            "n3": ["all gb == 0"]
        }
    }
    with open("docs/issues/structure_data.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
