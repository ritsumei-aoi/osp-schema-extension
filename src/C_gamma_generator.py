"""
C_gamma_generator.py
Compute the gamma (inhomogeneous deformation) structure for C(n+1) = osp(2|2n).

Mathematical framework (docs/math/C_inhomogeneous_definition.md):
  Deformed exchange relation:  [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ
  Deformed bracket:            [X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)

  γ(X, Y) is computed to first order in gb by evaluating [X,Y]_γ symbolically
  using the deformed oscillator relations and extracting the κ-coefficient.

Sign convention (Convention A, document-faithful):
  When a boson b_j^s (PBW index ≥ 2) passes a fermion a_1^σ (PBW index < 2)
  during PBW reduction, a κ-term −gb_{σ,j,s} · (lower word) is generated.
  This follows [b_j^s, a_1^σ] = −gb_{σ,j,s} · κ exactly.

gb_label format: "gb_{σs}_{j}" where σ=p(+)/m(−) for a_1^σ, s=p(+)/m(−) for b_j^s, j=1..n
  gb_pp_{j}: gb_{+,j,+} = (a_1^+ | b_j^+) in the Gram form
  gb_pm_{j}: gb_{+,j,−}
  gb_mp_{j}: gb_{−,j,+}
  gb_mm_{j}: gb_{−,j,−}

Output: Schema 2 JSON (C_{n}_gamma.json) — NOT written until human approval.
         Use --dry-run to inspect γ values without writing files.
"""

import sys
import json
import datetime
from fractions import Fraction
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from C_structure_generator import (
    OscAlgebra, build_generators, basis_order, poly_to_basis, build_schema1_json,
)


# ---------------------------------------------------------------------------
# gb label convention
# ---------------------------------------------------------------------------

def gb_label(sigma: int, j: int, s: int) -> str:
    """
    Canonical label for the gb deformation parameter.
      sigma : 0 = a_1^+, 1 = a_1^−  (PBW fermion index)
      j     : bosonic pair index 1..n
      s     : 0 = b_j^+, 1 = b_j^−  (PBW boson sign)
    Returns e.g. "gb_pp_1", "gb_mm_2".
    """
    σs = 'p' if sigma == 0 else 'm'
    ss = 'p' if s == 0 else 'm'
    return f'gb_{σs}{ss}_{j}'


def gb_label_human(sigma: int, j: int, s: int) -> str:
    """Human-readable: gb_{σ,j,s} notation."""
    σs = '+' if sigma == 0 else '−'
    ss = '+' if s == 0 else '−'
    return f'gb_{{{σs},{j},{ss}}}'


# ---------------------------------------------------------------------------
# Deformed oscillator algebra: first-order gb extension
# ---------------------------------------------------------------------------

class DeformedOscAlgebra(OscAlgebra):
    """
    Extends OscAlgebra to track first-order gb deformation (κ-terms).

    Elements are represented as (poly0, polyk) pairs:
      poly0 : {word_tuple: Fraction}         — standard PBW polynomial
      polyk : {gb_key: {word_tuple: Fraction}} — κ-coefficient per gb parameter

    Since κ² = 0, second-order terms are dropped throughout.

    Deformed rule (applied during PBW reduction of poly0 part only):
      When boson b_j^s (index a ≥ 2) passes fermion a_1^σ (index b < 2):
        b_j^s · a_1^σ  →  a_1^σ · b_j^s  −  gb_{σ,j,s} · κ · 1
      The κ-contribution is: (lower word, coeff −1) tagged with gb_label(b, a//2, a%2).
    """

    def _reduce_kappa(self, word, coeff: Fraction = Fraction(1)):
        """
        Reduce a word to PBW form, collecting first-order κ-corrections.

        Returns (poly0, polyk):
          poly0 : {word_tuple: Fraction}
          polyk : {gb_key_str: {word_tuple: Fraction}}
        """
        # Queue entries: (word_list, coeff, is_kappa_part, gb_key)
        queue = [(list(word), coeff, False, None)]
        poly0: dict = defaultdict(Fraction)
        polyk: dict = defaultdict(lambda: defaultdict(Fraction))

        while queue:
            w, c, is_k, gk = queue.pop()
            reduced = False
            for i in range(len(w) - 1):
                a, b = w[i], w[i + 1]
                # Fermionic nilpotency: drop word
                if a == b and self.gen_parity[a] == 1:
                    reduced = True
                    break
                if a > b:
                    # Standard PBW swap
                    for new_w, new_c in self._swap(w, i):
                        if new_c != 0:
                            queue.append((list(new_w), c * new_c, is_k, gk))
                    # κ-correction: boson before fermion, only at zeroth κ-order
                    if a >= 2 and b < 2 and not is_k:
                        sigma = b          # fermion index (0 or 1)
                        j = a // 2         # bosonic pair index 1..n
                        s = a % 2          # 0 = b_j^+, 1 = b_j^−
                        gk_new = gb_label(sigma, j, s)
                        kappa_w = w[:i] + w[i + 2:]   # remove the two generators
                        queue.append((kappa_w, c * Fraction(-1), True, gk_new))
                    reduced = True
                    break
            if not reduced:
                key = tuple(w)
                if not is_k:
                    poly0[key] += c
                else:
                    polyk[gk][key] += c

        return (
            {k: v for k, v in poly0.items() if v != 0},
            {k: {w: v for w, v in v.items() if v != 0} for k, v in polyk.items()},
        )

    def _mul_kappa(self, A, B):
        """
        Multiply two deformed elements A = (A0, Ak), B = (B0, Bk).
        Returns (C0, Ck) to first order in gb (κ² = 0 throughout).
        """
        A0, Ak = A
        B0, Bk = B
        C0: dict = defaultdict(Fraction)
        Ck: dict = defaultdict(lambda: defaultdict(Fraction))

        # A0 * B0 with κ-corrections from boson–fermion swaps
        for wa, ca in A0.items():
            for wb, cb in B0.items():
                p0, pk = self._reduce_kappa(wa + wb, ca * cb)
                for w, c in p0.items():
                    C0[w] += c
                for gk, poly in pk.items():
                    for w, c in poly.items():
                        Ck[gk][w] += c

        # A0 * κBk  (already O(κ) → standard reduce, no further κ)
        for gk, Bk_gk in Bk.items():
            for w, c in self.mul(A0, Bk_gk).items():
                Ck[gk][w] += c

        # κAk * B0
        for gk, Ak_gk in Ak.items():
            for w, c in self.mul(Ak_gk, B0).items():
                Ck[gk][w] += c

        return (
            {k: v for k, v in C0.items() if v != 0},
            {k: {w: v for w, v in v.items() if v != 0} for k, v in Ck.items()},
        )

    def bracket_gamma(self, X0: dict, pX: int, Y0: dict, pY: int):
        """
        Compute [X, Y}_γ = (br0, brk):
          br0  : standard bracket [X, Y]_0       ({word: Fraction})
          brk  : κ-coefficient = γ(X, Y)         ({gb_key: {word: Fraction}})

        X0, Y0 are standard generator polynomials (no κ-part initially).
        """
        X = (X0, {})
        Y = (Y0, {})
        XY = self._mul_kappa(X, Y)
        YX = self._mul_kappa(Y, X)
        sign = (-1) ** (pX * pY)

        br0: dict = defaultdict(Fraction, XY[0])
        brk: dict = defaultdict(lambda: defaultdict(Fraction))
        for w, c in YX[0].items():
            br0[w] -= sign * c
        for gk in set(XY[1].keys()) | set(YX[1].keys()):
            for w, c in XY[1].get(gk, {}).items():
                brk[gk][w] += c
            for w, c in YX[1].get(gk, {}).items():
                brk[gk][w] -= sign * c

        return (
            {k: v for k, v in br0.items() if v != 0},
            {k: {w: v for w, v in v.items() if v != 0} for k, v in brk.items()},
        )


# ---------------------------------------------------------------------------
# Extended basis decomposition (handles K central element component)
# ---------------------------------------------------------------------------

def poly_to_basis_gamma(poly: dict, alg: OscAlgebra) -> dict:
    """
    Decompose a γ-polynomial into basis elements plus an optional K component.

    Unlike poly_to_basis, γ-polynomials can carry an extra constant term that
    does not arise from the Cartan generators H_k.  This excess constant is
    the coefficient of K, the even central element (identified with scalar 1).

    Returns {label: Fraction} where label ∈ basis ∪ {'K'}.
    'K' appears when γ(X,Y) has a scalar component beyond what H_{n+1} provides.
    """
    n = alg.n
    bp, bm = alg.bp, alg.bm
    result: dict = {}
    res = dict(poly)

    # Odd generators (unique monomials)
    for k in range(1, n + 1):
        for suf, mon in [
            ('pp', (0, bp(k))),
            ('pm', (0, bm(k))),
            ('mp', (1, bp(k))),
            ('mm', (1, bm(k))),
        ]:
            c = res.pop(mon, Fraction(0))
            if c:
                result[f'E_eps_del{k}_{suf}'] = c

    # Even Sp generators (unique monomials)
    for k in range(1, n + 1):
        c = res.pop((bp(k), bp(k)), Fraction(0))
        if c:
            result[f'E_2del{k}_p'] = 2 * c
        c = res.pop((bm(k), bm(k)), Fraction(0))
        if c:
            result[f'E_2del{k}_m'] = 2 * c

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suf, mon in [
                ('pp', (bp(i), bp(j))),
                ('pm', (bp(i), bm(j))),
                ('mp', (bm(i), bp(j))),
                ('mm', (bm(i), bm(j))),
            ]:
                c = res.pop(mon, Fraction(0))
                if c:
                    result[f'E_del{i}_del{j}_{suf}'] = c

    # Cartan generators: solve the linear system (same as poly_to_basis)
    c0 = res.pop((0, 1), Fraction(0))
    ckk = [res.pop((bp(k), bm(k)), Fraction(0)) for k in range(1, n + 1)]
    c_const = res.pop((), Fraction(0))

    if res:
        raise ValueError(f'Unexpected PBW monomials in γ-poly: {res}')

    if n == 1:
        f1, f2 = c0, c0 - ckk[0]
        if f1:
            result['H_1'] = f1
        if f2:
            result['H_2'] = f2
        K_coeff = c_const + f2 / 2
    else:
        f = [Fraction(0)] * (n + 2)
        f[1] = c0
        f[2] = ckk[0] - f[1]
        for k in range(2, n):
            f[k + 1] = ckk[k - 1] + f[k]
        f[n + 1] = -ckk[n - 1] - f[n]
        for k in range(1, n + 2):
            if f[k]:
                result[f'H_{k}'] = f[k]
        K_coeff = c_const + f[n + 1] / 2

    if K_coeff:
        result['K'] = K_coeff

    return result


# ---------------------------------------------------------------------------
# Gamma structure constant computation
# ---------------------------------------------------------------------------

def compute_gamma_structure(n: int) -> list[dict]:
    """
    Compute all non-zero γ(X, Y)_Z coefficients for C(n+1).

    Each entry represents: [X, Y]_γ = [X, Y]_0 + κ · sum_Z (coeff · gb · Z)
    where coeff is rational, gb is a gb parameter label.
    """
    alg = DeformedOscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)

    entries = []
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            _br0, brk = alg.bracket_gamma(gens[X], par[X], gens[Y], par[Y])
            for gk, poly in brk.items():
                decomp = poly_to_basis_gamma(poly, alg)
                for Z, coeff in decomp.items():
                    if coeff:
                        entries.append({
                            'X': X, 'Y': Y, 'Z': Z,
                            'gb': gk,
                            'coeff': str(coeff),
                            'sign_rule': 'graded',
                        })
    return entries


def build_schema2_json(n: int) -> dict:
    """Assemble Schema 2 JSON for C(n+1) with bosonic rank n."""
    s1 = build_schema1_json(n)

    # gb parameter catalogue
    gb_params = {}
    for sigma in [0, 1]:
        for jj in range(1, n + 1):
            for s in [0, 1]:
                key = gb_label(sigma, jj, s)
                gb_params[key] = {
                    'sigma': '+' if sigma == 0 else '-',
                    'j': jj,
                    's': '+' if s == 0 else '-',
                    'description': (
                        f'[b_{jj}^{"+" if s==0 else "-"}, '
                        f'a_1^{"+" if sigma==0 else "-"}] = -gb * kappa'
                    ),
                }

    gamma = compute_gamma_structure(n)

    return {
        'schema_version': '5.0',
        'schema_layer': 2,
        'algebra': s1['algebra'],
        'central_elements': s1['central_elements'],
        'gb_matrix': {
            'description': (
                'Inhomogeneous deformation parameters for C(n+1). '
                'Deformed exchange relation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa. '
                'Gram matrix: (a_1^sigma | b_j^s) = gb_{sigma,j,s} '
                'in the pre-oscillator bilinear form.'
            ),
            'size': f'2 x 2n = {4 * n} parameters',
            'sign_convention': 'Negative: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa',
            'gram_matrix_convention': (
                'Row index: sigma in {+,-} (a_1^sigma); '
                'Column index: (j, s) ordered (1,+),(1,-),(2,+),(2,-),... '
                'gb_label format: gb_{sigma_str}{s_str}_{j}'
            ),
            'parameters': gb_params,
        },
        'gamma_structure': gamma,
        'metadata': {
            'generated_by': 'src/C_gamma_generator.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'algebra': f'C({n + 1}) = osp(2|{2 * n})',
            'n_gamma_entries': len(gamma),
            'references': [
                'Frappat, Sciarrino, Sorba (2000)',
                'docs/math/C_inhomogeneous_definition.md',
            ],
        },
    }


# ---------------------------------------------------------------------------
# Dry-run report: show γ structure without writing files
# ---------------------------------------------------------------------------

def dry_run_report(n: int):
    """Print a summary of the gamma structure for C(n+1)."""
    print(f'\n{"=" * 64}')
    print(f'C({n+1}) = osp(2|{2*n}),  n = {n}')
    alg = DeformedOscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)

    entries = compute_gamma_structure(n)
    gamma_by_pair: dict = defaultdict(list)
    for e in entries:
        gamma_by_pair[(e['X'], e['Y'])].append(e)

    print(f'  Total γ entries: {len(entries)}')
    print(f'  Non-zero (X,Y) pairs with γ ≠ 0: {len(gamma_by_pair)}')

    # Sample: first 6 non-zero pairs
    print('\n  Sample γ(X, Y) coefficients (first 6 pairs):')
    for (X, Y), elist in list(gamma_by_pair.items())[:6]:
        terms = ', '.join(
            f'{e["coeff"]}·{e["gb"]}·{e["Z"]}' for e in elist
        )
        print(f'    γ({X}, {Y}) =')
        for e in elist:
            print(f'      + {e["coeff"]} · {e["gb"]} · {e["Z"]}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir', nargs='?', default='data')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print report but do not write JSON files')
    args = parser.parse_args()

    for n in [1, 2, 3]:
        if args.dry_run:
            dry_run_report(n)
        else:
            out = Path(args.out_dir)
            out.mkdir(parents=True, exist_ok=True)
            schema = build_schema2_json(n)
            path = out / f'C_{n}_gamma.json'
            with open(path, 'w') as f:
                json.dump(schema, f, indent=2)
            n_entries = schema['metadata']['n_gamma_entries']
            print(f'Wrote {path} ({n_entries} γ entries)')


if __name__ == '__main__':
    main()
