"""Scratch check kept for reproducibility: delta(f_gb) == gamma(gb) for random integer gb.

Run from src/:  python3 _explore.py   (formal tests live in tests/test_C_coboundary.py)
"""
import random

import C_coboundary as B
import C_gamma as CG

if __name__ == "__main__":
    for n in (1, 2, 3):
        for seed in range(3):
            rnd = random.Random(seed)
            gb = dict((k, rnd.randint(-3, 3)) for k in CG.gb_keys(n))
            f = B.trivializing_map(n, gb)
            _, gam = CG.gamma_table(n, gb)
            print(n, seed, B.delta_f(n, f) == gam, B.f_is_odd(f))
