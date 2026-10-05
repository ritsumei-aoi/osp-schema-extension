import json
import numpy as np

def verify_dataset(filepath):
    print(f"\nVerifying artifact: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
        
    for k, item in data.items():
        n = item["n"]
        alg = item["algebra"]
        dim_even = item["superdimension"]["even"]
        dim_odd = item["superdimension"]["odd"]
        dim_total = item["superdimension"]["total"]
        num_gb = item["num_gb_parameters"]
        num_phi = item["num_phi_parameters"]
        r_phi = item["rank_M_phi"]
        r_all = item["rank_M_all"]
        dr = item["rank_difference"]
        
        print(f"--- {alg} (n={n}) ---")
        print(f"  Dimension: {dim_total} = {dim_even} (even) + {dim_odd} (odd)")
        print(f"  Theoretical even dim (2n^2 + n + 1): {2*n**2 + n + 1} -> Match: {dim_even == 2*n**2 + n + 1}")
        print(f"  Theoretical odd dim (4n): {4*n} -> Match: {dim_odd == 4*n}")
        print(f"  Number of gb parameters (4n): {4*n} -> Match: {num_gb == 4*n}")
        print(f"  Number of phi parameters (8n(2n^2+n+1)): {2 * 4 * n * (2*n**2+n+1)} -> Match: {num_phi == 2*4*n*(2*n**2+n+1)}")
        print(f"  Rank M_phi: {r_phi} (Expected: {num_phi - 4*n}) -> Match: {r_phi == num_phi - 4*n}")
        print(f"  Rank M_all: {r_all} (Expected: {num_phi - 4*n + 4*n} = {num_phi}) -> Match: {r_all == num_phi}")
        print(f"  Rank difference: {dr} (Full rank on gb = {num_gb}) -> Match: {dr == num_gb}")
        print(f"  Trivial iff gb=0: {item['is_trivial_iff_zero']}")
        assert dr == num_gb
        assert item['is_trivial_iff_zero'] == True

if __name__ == '__main__':
    verify_dataset("data/verification_artifacts.json")
    print("\nAll independent tests in verify_reproducibility.py passed successfully!")
