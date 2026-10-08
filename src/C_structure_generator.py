"""
C_structure_generator.py
Generate Schema 1 JSON (structure constants) for C(n+1) = osp(2|2n).

Oscillator algebra conventions (handover/notation.md, I01-1):
  Generator indices (PBW order):
    0: a_1_p  (parity 1)    1: a_1_m  (parity 1)
    2k:   b_k_p (parity 0)  for k=1..n
    2k+1: b_k_m (parity 0)

  Relations in the associative oscillator algebra:
    a_1_m * a_1_p  = 1 - a_1_p * a_1_m    (CAR, anticommutator)
    b_k_m * b_k_p  = b_k_p * b_k_m + 1    (CCR, commutator)
    all other adjacent pairs commute freely

  Graded bracket: [X, Y} = X*Y - (-1)^{p(X)*p(Y)} * Y*X
"""

from fractions import Fraction
from collections import defaultdict
import json
import datetime


# ---------------------------------------------------------------------------
# Oscillator algebra: polynomial representation and PBW reduction
# ---------------------------------------------------------------------------

class OscAlgebra:
    """Associative oscillator algebra for C(n+1) = osp(2|2n)."""

    def __init__(self, n: int):
        self.n = n
        # Generator parities: 0=a_1_p, 1=a_1_m, 2k=b_k_p, 2k+1=b_k_m
        self.gen_parity = [1, 1] + [0] * (2 * n)
        self.num_gens = 2 + 2 * n

    # -- index helpers -------------------------------------------------------
    def bp(self, k: int) -> int:
        """PBW index of b_k_p (k=1..n)."""
        return 2 * k

    def bm(self, k: int) -> int:
        """PBW index of b_k_m (k=1..n)."""
        return 2 * k + 1

    # -- one-step PBW reduction rule -----------------------------------------
    def _swap(self, word: list, pos: int):
        """
        Apply the commutation relation at position pos where word[pos] > word[pos+1].
        Returns list of (new_word_tuple, coeff) pairs representing the result.

        Conventions:
          a_1_m * a_1_p  -> 1 - a_1_p * a_1_m    (indices 1,0)
          b_k_m * b_k_p  -> b_k_p * b_k_m + 1    (indices 2k+1, 2k)
          all others     -> commute freely
        """
        a, b = word[pos], word[pos + 1]   # a > b (out of PBW order)
        before = word[:pos]
        after = word[pos + 2:]
        swapped = tuple(before + [b, a] + after)
        lower = tuple(before + after)

        if a == 1 and b == 0:
            # a_1_m * a_1_p = 1 - a_1_p * a_1_m
            return [(swapped, Fraction(-1)), (lower, Fraction(1))]
        if b >= 2 and a == b + 1 and b % 2 == 0:
            # b_k_m * b_k_p = b_k_p * b_k_m + 1
            return [(swapped, Fraction(1)), (lower, Fraction(1))]
        # Free commutativity (boson+fermion of different types, bosons of different k)
        return [(swapped, Fraction(1))]

    # -- full PBW reduction --------------------------------------------------
    def reduce(self, word: tuple, coeff: Fraction = Fraction(1)) -> dict:
        """
        Reduce a single word to PBW normal form.
        Returns {tuple: Fraction}.
        """
        polys = {word: coeff}
        while True:
            new_polys: dict = defaultdict(Fraction)
            changed = False
            for w, c in polys.items():
                if c == 0:
                    continue
                wl = list(w)
                reduced = False
                for i in range(len(wl) - 1):
                    a, b = wl[i], wl[i + 1]
                    # Fermionic nilpotency: same fermionic index twice -> 0
                    if a == b and self.gen_parity[a] == 1:
                        reduced = True
                        changed = True
                        break
                    if a > b:
                        for ww, cc in self._swap(wl, i):
                            new_polys[ww] += c * cc
                        reduced = True
                        changed = True
                        break
                if not reduced:
                    new_polys[w] += c
            polys = {k: v for k, v in new_polys.items() if v != 0}
            if not changed:
                break
        return dict(polys)

    # -- polynomial multiplication -------------------------------------------
    def mul(self, p1: dict, p2: dict) -> dict:
        """Multiply two polynomials and reduce to PBW form."""
        result: dict = defaultdict(Fraction)
        for w1, c1 in p1.items():
            for w2, c2 in p2.items():
                combined = w1 + w2
                for w, c in self.reduce(combined, c1 * c2).items():
                    result[w] += c
        return {k: v for k, v in result.items() if v != 0}

    # -- graded Lie bracket --------------------------------------------------
    def bracket(self, X: dict, pX: int, Y: dict, pY: int) -> dict:
        """[X, Y} = XY - (-1)^{pX*pY} YX."""
        XY = self.mul(X, Y)
        YX = self.mul(Y, X)
        sign = (-1) ** (pX * pY)
        result: dict = defaultdict(Fraction)
        for w, c in XY.items():
            result[w] += c
        for w, c in YX.items():
            result[w] -= sign * c
        return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Generator realizations for C(n+1)
# ---------------------------------------------------------------------------

def build_generators(alg: OscAlgebra) -> tuple[dict, dict]:
    """
    Return (gens, parity):
      gens   : {label -> {word_tuple -> Fraction}}
      parity : {label -> int (0 or 1)}
    """
    n = alg.n
    bp = alg.bp
    bm = alg.bm
    gens: dict = {}
    par: dict = {}

    # Cartan elements
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens['H_1'] = {(0, 1): Fraction(1), (bp(1), bm(1)): Fraction(1)}
    par['H_1'] = 0

    # H_k for k=2..n: b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
    for k in range(2, n + 1):
        gens[f'H_{k}'] = {
            (bp(k - 1), bm(k - 1)): Fraction(1),
            (bp(k), bm(k)): Fraction(-1),
        }
        par[f'H_{k}'] = 0

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f'H_{n+1}'] = {(bp(n), bm(n)): Fraction(-1), (): Fraction(-1, 2)}
    par[f'H_{n+1}'] = 0

    # Odd generators: E_eps_del{k}_{ss}
    for k in range(1, n + 1):
        gens[f'E_eps_del{k}_pp'] = {(0, bp(k)): Fraction(1)}
        gens[f'E_eps_del{k}_pm'] = {(0, bm(k)): Fraction(1)}
        gens[f'E_eps_del{k}_mp'] = {(1, bp(k)): Fraction(1)}
        gens[f'E_eps_del{k}_mm'] = {(1, bm(k)): Fraction(1)}
        for suf in ('pp', 'pm', 'mp', 'mm'):
            par[f'E_eps_del{k}_{suf}'] = 1

    # Even Sp generators
    for k in range(1, n + 1):
        gens[f'E_2del{k}_p'] = {(bp(k), bp(k)): Fraction(1, 2)}
        gens[f'E_2del{k}_m'] = {(bm(k), bm(k)): Fraction(1, 2)}
        par[f'E_2del{k}_p'] = 0
        par[f'E_2del{k}_m'] = 0

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_pp'] = {(bp(i), bp(j)): Fraction(1)}
            gens[f'E_del{i}_del{j}_pm'] = {(bp(i), bm(j)): Fraction(1)}
            gens[f'E_del{i}_del{j}_mp'] = {(bm(i), bp(j)): Fraction(1)}
            gens[f'E_del{i}_del{j}_mm'] = {(bm(i), bm(j)): Fraction(1)}
            for suf in ('pp', 'pm', 'mp', 'mm'):
                par[f'E_del{i}_del{j}_{suf}'] = 0

    return gens, par


def basis_order(n: int) -> list[str]:
    """PBW basis ordering as in handover/notation.md (ε-first, Option A)."""
    odd: list[str] = []
    for k in range(1, n + 1):
        odd.append(f'E_eps_del{k}_pp')
    for k in range(1, n + 1):
        odd.append(f'E_eps_del{k}_pm')
    for k in range(1, n + 1):
        odd.append(f'E_eps_del{k}_mp')
    for k in range(1, n + 1):
        odd.append(f'E_eps_del{k}_mm')

    even: list[str] = [f'H_{k}' for k in range(1, n + 2)]
    for k in range(1, n + 1):
        even.append(f'E_2del{k}_p')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f'E_del{i}_del{j}_pp')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f'E_del{i}_del{j}_pm')
    for k in range(1, n + 1):
        even.append(f'E_2del{k}_m')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f'E_del{i}_del{j}_mm')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f'E_del{i}_del{j}_mp')

    return odd + even


# ---------------------------------------------------------------------------
# Decompose a bracket polynomial into the basis
# ---------------------------------------------------------------------------

def poly_to_basis(poly: dict, alg: OscAlgebra) -> dict:
    """
    Express a PBW polynomial as a linear combination of basis generators.
    Returns {label: Fraction} or raises ValueError on unexpected monomials.

    Cartan extraction uses the linear system derived in I03-1:
      c_0       = f_1
      c_{1,1}   = f_1 + f_2          (for n>=2) or f_1 - f_2  (n=1)
      c_{k,k}   = -f_k + f_{k+1}     (k=2..n-1, n>=3)
      c_{n,n}   = -f_n - f_{n+1}
      c_const   = -f_{n+1}/2
    """
    n = alg.n
    bp, bm = alg.bp, alg.bm
    result: dict = {}
    res = dict(poly)

    # Step 1: odd generators (each is a unique single-monomial word)
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

    # Step 2: Sp even generators (unique monomials)
    for k in range(1, n + 1):
        c = res.pop((bp(k), bp(k)), Fraction(0))
        if c:
            result[f'E_2del{k}_p'] = 2 * c   # E_2del = (1/2)*mon => coeff=2*poly_coeff
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

    # Step 3: Cartan generators from remaining monomials
    c0 = res.pop((0, 1), Fraction(0))                                  # (a_1_p, a_1_m)
    ckk = [res.pop((bp(k), bm(k)), Fraction(0)) for k in range(1, n + 1)]
    cconst = res.pop((), Fraction(0))

    if res:
        raise ValueError(f'Unexpected PBW monomials: {res}')

    if n == 1:
        # c_{1,1} = f_1 - f_2,  c_const = -f_2/2
        f1 = c0
        f2 = f1 - ckk[0]
        if -f2 / 2 != cconst:
            raise ValueError(f'Cartan consistency fail (n=1): -f2/2={-f2/2}, c_const={cconst}')
        if f1:
            result['H_1'] = f1
        if f2:
            result['H_2'] = f2
    else:
        # n >= 2
        f = [Fraction(0)] * (n + 2)
        f[1] = c0
        f[2] = ckk[0] - f[1]           # c_{1,1} = f_1 + f_2
        for k in range(2, n):
            f[k + 1] = ckk[k - 1] + f[k]   # c_{k,k} = -f_k + f_{k+1}
        f[n + 1] = -ckk[n - 1] - f[n]      # c_{n,n} = -f_n - f_{n+1}
        if -f[n + 1] / 2 != cconst:
            raise ValueError(
                f'Cartan consistency fail (n={n}): -f[n+1]/2={-f[n+1]/2}, c_const={cconst}'
            )
        for k in range(1, n + 2):
            if f[k]:
                result[f'H_{k}'] = f[k]

    return result


# ---------------------------------------------------------------------------
# Structure constant computation
# ---------------------------------------------------------------------------

def compute_structure_constants(n: int) -> list[dict]:
    """Compute all non-zero [X,Y} = sum_Z f*Z structure constants for C(n+1)."""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)

    sc_list: list[dict] = []
    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            X, Y = basis[i], basis[j]
            br = alg.bracket(gens[X], par[X], gens[Y], par[Y])
            if not br:
                continue
            decomp = poly_to_basis(br, alg)
            for Z, coeff in decomp.items():
                if coeff:
                    sc_list.append({
                        'X': X, 'Y': Y, 'Z': Z,
                        'coeff': str(coeff),
                        'sign_rule': 'graded',
                    })
    return sc_list


# ---------------------------------------------------------------------------
# JSON schema assembly
# ---------------------------------------------------------------------------

def build_schema1_json(n: int) -> dict:
    """Assemble the full Schema 1 JSON for C(n+1) with bosonic rank n."""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)
    odd_basis = [b for b in basis if par[b] == 1]
    even_basis = [b for b in basis if par[b] == 0]

    even_dim = 2 * n**2 + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim

    boson_labels = [f'b_{k}_{s}' for k in range(1, n + 1) for s in ('p', 'm')]

    sc = compute_structure_constants(n)

    # Generator realization entries
    def frac_str(f: Fraction) -> str:
        return str(f) if f.denominator != 1 else str(f.numerator)

    def poly_to_realization(poly: dict) -> list[dict]:
        entries = []
        for word, c in sorted(poly.items(), key=lambda x: (len(x[0]), x[0])):
            # Map index tuples back to label lists
            labels = [alg.gen_labels[i] for i in word] if hasattr(alg, 'gen_labels') else [str(i) for i in word]
            entries.append({'words': labels, 'coeff': frac_str(c)})
        return entries

    # Attach gen labels to alg for the helper above
    alg.gen_labels = ['a_1_p', 'a_1_m'] + [
        f'b_{k}_{s}' for k in range(1, n + 1) for s in ('p', 'm')
    ]

    realizations = {}
    for label, poly in gens.items():
        realizations[label] = {
            'standard_form': poly_to_realization(poly),
            'parity': par[label],
        }

    schema = {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n+1})',
            'alternative_notation': {
                'osp': f'osp(2|{2*n})',
                'dimension_formula': 'osp(2m|2n) with m=1',
            },
            'dimension': {
                'total': total_dim,
                'even': even_dim,
                'odd': odd_dim,
            },
        },
        'central_elements': {
            'kappa': {
                'label': 'kappa',
                'parity': 1,
                'nilpotency': 'kappa^2 = 0',
                'role': 'Odd central element; appears in [X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y)',
            },
            'K': {
                'label': 'K',
                'parity': 0,
                'role': 'Even central element; identified with scalar 1 in all current applications',
            },
        },
        'oscillator_generators': {
            'fermions': {
                'm': 1,
                'labels': ['a_1_p', 'a_1_m'],
                'parity': 1,
                'description': "Standard fermionic pair a_1^± with CAR: {a_1^-, a_1^+} = 1",
            },
            'bosons': {
                'count': 2 * n,
                'n': n,
                'labels': boson_labels,
                'description': f"Bosonic oscillators b_k^± with k=1,...,{n}; CCR: [b_k^-, b_l^+] = delta_kl",
            },
        },
        'oscillator_relations': {
            'fermionic_anticommutators': {
                'description': 'CAR for the standard fermionic pair a_1^±',
                'relations': {
                    'conjugate_pair': '{a_1^-, a_1^+} = 1',
                    'same_sign': '{a_1^s, a_1^s} = 0 for s in {+,-}',
                },
            },
            'bosonic_commutators': {
                'description': 'CCR for bosonic oscillators',
                'relations': {
                    'same_type': '[b_i^s, b_j^s] = 0 for all i,j,s',
                    'conjugate_pair': '[b_i^-, b_j^+] = delta_{ij}',
                },
            },
            'mixed_commutators': {
                'description': 'Boson-fermion mixed relations (undeformed)',
                'relations': {
                    'boson_fermion': '[b_k^s, a_1^sigma] = 0 for all k, s, sigma',
                },
            },
        },
        'basis': {
            'even': even_basis,
            'odd': odd_basis,
            'ordering_convention': 'PBW: [odd, eps-first] < [even, Cartan < positive-Sp < negative-Sp < mixed-Sp]',
        },
        'parity': {label: par[label] for label in basis},
        'generator_realization': {
            'description': 'Standard form with PBW ordering',
            'ordering': ', '.join(alg.gen_labels),
            'realizations': realizations,
        },
        'structure_constants': sc,
        'metadata': {
            'generated_by': 'src/C_structure_generator.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'algebra': f'C({n+1}) = osp(2|{2*n})',
            'references': [
                'Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras',
                'handover/notation.md (I01-1)',
                'docs/json_schema_specification.md (I02-1)',
            ],
        },
    }
    return schema


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import os, sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    os.makedirs(out_dir, exist_ok=True)
    for n in (1, 2, 3):
        print(f'Generating C_{n}_structure.json  (C({n+1}) = osp(2|{2*n}))...')
        schema = build_schema1_json(n)
        sc_count = len(schema['structure_constants'])
        print(f'  Basis: {schema["algebra"]["dimension"]["even"]} even, '
              f'{schema["algebra"]["dimension"]["odd"]} odd; '
              f'{sc_count} non-zero structure constants')
        fname = os.path.join(out_dir, f'C_{n}_structure.json')
        with open(fname, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f'  Written: {fname}')


if __name__ == '__main__':
    main()
