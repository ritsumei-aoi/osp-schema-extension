"""Sanity checks for the oscillator engine and osp(2|2n) closure."""
from sympy import symbols
from osp_engine import make_gb_symbols, normal_order, super_bracket
from basis import build_basis, monomial_to_index


def decompose(elem, idx, parity_check=None):
    """Split a normal-ordered element into:
       g_part:  dict basis_index -> coeff      (kappa^0, degree-2 g generators)
       central: dict (kpow,tokens) -> coeff    (everything else: scalars, kappa terms, deg!=2)
    """
    g0 = {}      # kappa^0 g-part
    other = {}
    for (kp, toks), c in elem.items():
        if kp == 0 and toks in idx:
            g0[idx[toks]] = g0.get(idx[toks], 0) + c
        else:
            other[(kp, toks)] = c
    return g0, other


def run(n):
    print(f"\n===== n = {n}  (C({n+1}) = osp(2|{2*n})) =====")
    gb = make_gb_symbols(n)
    basis, parity, names = build_basis(n)
    idx = monomial_to_index(n, names)
    D = len(basis)
    nev = parity.count(0)
    nod = parity.count(1)
    print(f"dim g = {D}  (even {nev}, odd {nod})")
    assert nev == 2 * n * n + n + 1
    assert nod == 4 * n
    assert D == 2 * n * n + 5 * n + 1

    # zero out gb (undeformed) by substituting 0
    zero_sub = {gb[k]: 0 for k in gb}

    # Check undeformed closure: [Z_a,Z_b] has no kappa term and lands in g up to central scalars
    bad = 0
    for a in range(D):
        for b in range(a, D):
            br = super_bracket(basis[a], basis[b], parity[a], parity[b], gb)
            br = {k: v.subs(zero_sub) for k, v in br.items()}
            br = {k: v for k, v in br.items() if v != 0}
            g0, other = decompose(br, idx)
            # 'other' should only be central scalars: kpow=0, len(tokens) in {0}
            for (kp, toks), c in other.items():
                if not (kp == 0 and len(toks) == 0):
                    print(f"  NON-CLOSURE [{names[a]},{names[b]}] -> stray {(kp,toks)}:{c}")
                    bad += 1
    print(f"undeformed closure violations (non-scalar leftovers): {bad}")

    # super-antisymmetry spot check: [Za,Zb] = -(-1)^{pa pb}[Zb,Za]
    import random
    random.seed(0)
    for _ in range(5):
        a = random.randrange(D); b = random.randrange(D)
        ab = super_bracket(basis[a], basis[b], parity[a], parity[b], gb)
        ba = super_bracket(basis[b], basis[a], parity[b], parity[a], gb)
        sign = -1 if (parity[a]*parity[b]) % 2 == 1 else 1
        # ab + sign*ba == 0
        check = dict(ab)
        for k, v in ba.items():
            check[k] = check.get(k, 0) + sign * v
        check = {k: v for k, v in check.items() if v != 0}
        assert not check, f"antisymmetry fail {names[a]},{names[b]}: {check}"
    print("super-antisymmetry: OK")
    return bad


if __name__ == "__main__":
    import sys
    tot = 0
    for n in (1, 2):
        tot += run(n)
    print("\nTOTAL closure violations:", tot)
