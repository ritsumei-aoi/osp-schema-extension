"""Independent reference expressed in a Worker's own generator basis.

Reuses the definitions of ../../experiment/scripts/independent_triviality4.py
(everything before its rank section) for a given n, then replaces the
generator realizations by the Worker's realizations (from the Worker's
C_n_structure.json). Consequently no separate scaling factor lambda is needed:
the reference gamma is computed directly for the Worker's generators, and
expanded in the Worker's basis + K.

Worker realizations are normal-ordered with the UNdeformed relations (as the
reference does for its own generators); all Worker realizations seen here put
fermions left of bosons, so this choice does not matter for them.
"""
import os, sys
from fractions import Fraction as F

_HERE = os.path.dirname(os.path.abspath(__file__))
_REF = os.path.join(_HERE, '..', '..', 'experiment', 'scripts', 'independent_triviality4.py')
_cache = {}


def ref_namespace(n):
    if n in _cache:
        return _cache[n]
    src = open(_REF).read().split("A = list(Dcols.values())")[0]
    ns = {'__name__': 'ref%d' % n}
    old = sys.argv
    sys.argv = ['x', str(n)]
    try:
        exec(src, ns)
    finally:
        sys.argv = old
    _cache[n] = ns
    return ns


def osc(word):
    """'a_1_p' -> ('a','+'); 'b_2_m' -> ('b2','-')"""
    parts = word.split('_')
    name, idx, s = parts[0], parts[1], parts[2]
    sg = {'p': '+', 'm': '-'}[s]
    return ('a', sg) if name == 'a' else ('b%d' % int(idx), sg)


class WorkerBasisRef:
    def __init__(self, n, basis, parity, realization):
        """basis: list of Worker labels; parity: {label: 0/1};
        realization: {label: [(coef Fraction, [word,...]), ...]}"""
        ns = ref_namespace(n)
        self.ns, self.n = ns, n
        self.basis, self.parity = list(basis), dict(parity)
        for g in self.basis:
            poly = {}
            for c, ws in realization[g]:
                key = (tuple(osc(w) for w in ws), False)
                poly[key] = poly.get(key, 0) + F(c)
            ns['GEN'][g] = ns['normalize'](poly)
            ns['parity'][g] = self.parity[g]
        ns['COLS'] = [ns['GEN'][g] for g in self.basis] + [{((), False): F(1)}]
        ns['LABELS'] = self.basis + ['K']
        self.gb_params = ns['gb_params']
        self._sc = None

    def structure_constants(self):
        """Undeformed brackets in the Worker basis: {(X,Y): {Z: c}} (K allowed)."""
        if self._sc is None:
            ns = self.ns
            self._sc = {}
            for X in self.basis:
                for Y in self.basis:
                    self._sc[(X, Y)] = ns['solve_coords'](ns['graded_bracket'](X, Y, False, False, None))
        return self._sc

    def gamma(self, param, sign):
        """{(X,Y,Z): c} over all ordered pairs, Z in basis or 'K'."""
        ns = self.ns
        def gbval(a, b):
            return F(1) if (a[1], int(b[0][1:]), b[1]) == param else F(0)
        G = {}
        for X in self.basis:
            for Y in self.basis:
                br = ns['graded_bracket'](X, Y, True, sign, gbval)
                kap = {(w, False): c for (w, k), c in br.items() if k}
                for z, c in ns['solve_coords'](kap).items():
                    G[(X, Y, z)] = c
        return G

    def coboundary_columns(self):
        """delta f columns for elementary odd maps f_(t<-s), t,s in basis (no K target).
        Returns {(t,s): {(X,Y,Z): c}} over all ordered pairs."""
        sc = self.structure_constants()
        p = self.parity
        br = lambda x, y: {z: c for z, c in sc[(x, y)].items() if z != 'K'}
        phis = [(t, s) for s in self.basis for t in self.basis if p[t] != p[s]]
        D = {ph: {} for ph in phis}
        def acc(ph, k, c):
            if c:
                D[ph][k] = D[ph].get(k, 0) + c
                if D[ph][k] == 0:
                    del D[ph][k]
        for X in self.basis:
            for Y in self.basis:
                for (t, s) in phis:
                    if s == Y:
                        for z, c in br(X, t).items():
                            acc((t, s), (X, Y, z), (-1) ** p[X] * c)
                    if s == X:
                        for z, c in br(Y, t).items():
                            acc((t, s), (X, Y, z), -(-1) ** ((p[X] + 1) * p[Y]) * c)
                for w, c in br(X, Y).items():
                    for (t, s) in phis:
                        if s == w:
                            acc((t, s), (X, Y, t), -c)
        return D

    def rank(self, cols):
        return self.ns['rank'](cols)
