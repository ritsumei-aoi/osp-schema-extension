"""
Unit test for C(n+1) triviality analysis.
"""

from fractions import Fraction
from src.analyze_triviality import analyze_triviality_for_n

def test_triviality_results():
    for n in [1, 2, 3]:
        # All gb = 0 => trivial
        zero_map = {f"gb_{sigma}_b{j}{s}": Fraction(0) 
                    for sigma in ['a1p', 'a1m'] 
                    for j in range(1, n+1) 
                    for s in ['p', 'm']}
        res_zero = analyze_triviality_for_n(n, zero_map)
        assert res_zero["is_trivial"]

        # Unit profile (all gb = 1) => non-trivial
        res_unit = analyze_triviality_for_n(n)
        assert not res_unit["is_trivial"]
        assert res_unit["rank_aug"] == res_unit["rank_M"] + 1
