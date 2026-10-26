"""Adapter for Claude Code batch runs, condition G (opus55 / sonnet55, b02..b10).

Only label/encoding translation; no Worker value is changed. Files read: the
committed data/C_<n>_gamma.json and data/C_<n>_coboundary.json of each run.
Structure and evaluated files use the default loaders.

Gamma encodings (list paths are explicit per run; see GAMMA below):
  - row (X,Y,Z,coeff) with coeff = {gb_label: "rational"}            (most runs)
  - row (X,Y,Z,coeff) with coeff = linear expression string,
    e.g. "2*gb_p_1_p" or "-1/2*gb_m_2_p"                             (opus55-b02)
  - row (X,Y,Z,gamma=[{param, coeff}])                                (sonnet55-b06)
  - central rows without a Z key, stored in a separate list whose name says
    "central" (opus55-b04 gamma_central, sonnet55-b10 central_component.entries):
    the file states these are the coefficient of kappa*K, so Z = 'K' is assigned.
    (opus55-b08 central_component rows already carry Z = 'K'.)

gb label rule. Every file defines gb via "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa"
with gb_matrix rows a_1_<sigma> and columns b_j_<s>. Labels are mapped to the
reference key (sign of a, j, sign of b):
  gb_a1p_b1m, gb_a_1_p_b_1_m   -> default loader.gbparse (a-sign, j, b-sign)
  gb_p_1_m  (gb_<sigma>_<j>_<s>) -> ('+', 1, '-')  [new rule, opus55-b02/b08/b10]
The rule is cross-checked against the file's own gb_matrix (rows x columns) when
the file has one; a mismatch raises.

Coboundary encodings (Worker's phi-labelled matrix A; labels kept as strings):
  opus55-b02  .coboundary, coeff = linear expression in phi_i_j / phi_K_j
  opus55-b04  .coboundary_coefficients {phi: c} + .coboundary_central {psi: c} (Z='K')
  opus55-b06  .coboundary.entries terms [[k, c]] -> label odd_linear_map.unknowns[k]
  opus55-b08  .general_coboundary {phi[..|..]: c}   (reference_map.* is delta f_gb, not A; not used)
  opus55-b10  .coboundary.entries {phi__..__..|psi__..: c}
  sonnet55-b04 .coboundary_structure.entries {f_a_1_s_b_j_t: c}: delta f for the 4n-parameter
               family f_c only (the Worker's recorded A has 4n columns, not the general odd map)
  sonnet55-b06 .elementary_maps[k] = {from, to, delta_f rows}: column label 'to<-from'
  sonnet55-b02/b08/b10: only delta f of one fixed f (one gb profile), no phi labels
               -> (None, info), as the default loader does for unlabelled rows.
K-target columns (phi_K / psi / phi[K|..]) are kept as recorded.
"""
import json, re
from fractions import Fraction as F
import sympy as sp
from loader import num, add, gbparse, path

RUNS = ['thm01-R-%s-b%02d-G' % (m, b) for m in ('opus55', 'sonnet55') for b in (2, 4, 6, 8, 10)]

# run -> list of (json path tuple, implicit Z for rows without Z)
GAMMA = {
    'opus55-b02': [(('inhomogeneous_deformation', 'gamma'), None)],
    'opus55-b04': [(('inhomogeneous_deformation', 'gamma_coefficients'), None),
                   (('inhomogeneous_deformation', 'gamma_central'), 'K')],
    'opus55-b06': [(('inhomogeneous_deformation', 'entries'), None)],
    'opus55-b08': [(('inhomogeneous_deformation', 'gamma'), None),
                   (('inhomogeneous_deformation', 'central_component'), 'K')],
    'opus55-b10': [(('inhomogeneous_deformation', 'gamma'), None)],
    'sonnet55-b02': [(('inhomogeneous_deformation', 'gamma'), None)],
    'sonnet55-b04': [(('inhomogeneous_deformation', 'gamma_structure'), None)],
    'sonnet55-b06': [(('inhomogeneous_deformation', 'gamma_structure'), None)],
    'sonnet55-b08': [(('inhomogeneous_deformation', 'gamma'), None)],
    'sonnet55-b10': [(('inhomogeneous_deformation', 'gamma'), None),
                     (('inhomogeneous_deformation', 'central_component', 'entries'), 'K')],
}


def _key(run):
    return run[len('thm01-R-'):-len('-G')]


def _get(d, p):
    for k in p:
        d = d[k]
    return d


def gb2(label):
    """gb label -> (a sign, j, b sign). Extends loader.gbparse by gb_<sigma>_<j>_<s>."""
    m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', label)
    if m:
        return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')
    return gbparse(label)


def _check_gb_matrix(d):
    """Cross-check the label rule against the file's gb_matrix (rows a_1_s, cols b_j_t)."""
    def find(o):
        if isinstance(o, dict):
            if 'gb_matrix' in o:
                return o['gb_matrix']
            for v in o.values():
                r = find(v)
                if r is not None:
                    return r
        return None
    g = find(d)
    if not g:
        return 'no gb_matrix'
    rows = g.get('rows')
    cols = g.get('cols', g.get('columns'))
    tab = next((g[k] for k in ('symbols', 'labels', 'entries') if k in g), None)
    if tab is None and isinstance(g.get('parameters'), list) and isinstance(g['parameters'][0], str):
        tab = [g['parameters'][i * len(cols):(i + 1) * len(cols)] for i in range(len(rows))]
    if not (rows and cols and tab):
        return 'gb_matrix without table'
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            ra, cb = r.split('_'), c.split('_')
            want = ('+' if ra[2] == 'p' else '-', int(cb[1]), '+' if cb[2] == 'p' else '-')
            if gb2(tab[i][j]) != want:
                raise ValueError('gb label %s at (%s,%s) does not follow the rule' % (tab[i][j], r, c))
    return 'gb_matrix cross-checked (%dx%d)' % (len(rows), len(cols))


def _linear(s):
    """Linear expression string -> {symbol name: Fraction}. Raises if not linear."""
    e = sp.expand(sp.sympify(s))
    out = {}
    for sym in sorted(e.free_symbols, key=str):
        c = e.coeff(sym)
        if c.free_symbols:
            raise ValueError('non-linear coefficient %r' % s)
        out[str(sym)] = F(int(sp.Rational(c).p), int(sp.Rational(c).q))
    rest = sp.expand(e - sum(sp.Rational(v.numerator, v.denominator) * sp.Symbol(k) for k, v in out.items()))
    if rest != 0:
        raise ValueError('constant/non-linear part %r in %r' % (rest, s))
    return out


def _terms(e):
    """One row -> list of (param label, Fraction)."""
    if 'gamma' in e and isinstance(e['gamma'], list):
        return [(t['param'], num(t['coeff'])) for t in e['gamma']]
    c = e['coeff']
    if isinstance(c, dict):
        return [(k, num(v)) for k, v in c.items()]
    return list(_linear(c).items())


def load_gamma(run, n):
    d = json.load(open(path(run, n, 'gamma')))
    chk = _check_gb_matrix(d)
    D, parts = {}, []
    for p, zdef in GAMMA[_key(run)]:
        l = _get(d, p)
        for e in l:
            Z = e.get('Z', zdef)
            if Z is None:
                raise ValueError('row without Z in %s' % '.'.join(p))
            for lab, c in _terms(e):
                add(D, gb2(lab), (e['X'], e['Y'], Z), c)
        parts.append('%s(%d%s)' % ('.'.join(p), len(l), ', Z=K assigned' if zdef else ''))
    enc = {dict: 'row (X,Y,Z,coeff={gb:c})', str: 'row (X,Y,Z,coeff="linear expr in gb")'}
    first = _get(d, GAMMA[_key(run)][0][0])[0]
    e0 = ('row (X,Y,Z,gamma=[{param,coeff}])' if 'gamma' in first
          else enc[type(first['coeff'])])
    return D, dict(list_path=' + '.join(parts), entries=sum(len(_get(d, p)) for p, _ in GAMMA[_key(run)]),
                   encoding=e0 + '; ' + chk)


def load_coboundary(run, n):
    k = _key(run)
    d = json.load(open(path(run, n, 'coboundary')))
    D = {}

    def rows(l, zdef=None, label=None):
        for e in l:
            Z = e.get('Z', zdef)
            if label is not None:
                add(D, label, (e['X'], e['Y'], Z), num(e['coeff']))
                continue
            if 'terms' in e:
                for idx, c in e['terms']:
                    add(D, d['odd_linear_map']['unknowns'][idx], (e['X'], e['Y'], Z), num(c))
                continue
            for lab, c in _terms(e):
                add(D, lab, (e['X'], e['Y'], Z), c)

    if k == 'opus55-b02':
        l = d['coboundary']; rows(l)
        info = dict(list_path='.coboundary', entries=len(l), encoding='row (X,Y,Z,coeff="linear expr in phi_i_j/phi_K_j")')
    elif k == 'opus55-b04':
        a, b = d['coboundary_coefficients'], d['coboundary_central']
        rows(a); rows(b, 'K')
        info = dict(list_path='.coboundary_coefficients + .coboundary_central (Z=K assigned)', entries=len(a) + len(b),
                    encoding='row (X,Y,Z,coeff={phi|psi:c})')
    elif k == 'opus55-b06':
        l = d['coboundary']['entries']; rows(l)
        info = dict(list_path='.coboundary.entries', entries=len(l),
                    encoding='row (X,Y,Z,terms=[[unknown index,c]]) -> odd_linear_map.unknowns')
    elif k == 'opus55-b08':
        l = d['general_coboundary']; rows(l)
        info = dict(list_path='.general_coboundary', entries=len(l), encoding='row (X,Y,Z,coeff={phi[..|..]:c})')
    elif k == 'opus55-b10':
        l = d['coboundary']['entries']; rows(l)
        info = dict(list_path='.coboundary.entries', entries=len(l), encoding='row (X,Y,Z,coeff={phi__..|psi__..:c})')
    elif k == 'sonnet55-b04':
        l = d['coboundary_structure']['entries']; rows(l)
        info = dict(list_path='.coboundary_structure.entries', entries=len(l),
                    encoding='row (X,Y,Z,coeff={f_a_1_s_b_j_t:c}); only the 4n-parameter family f_c')
    elif k == 'sonnet55-b06':
        m = d['elementary_maps']
        for em in m:
            rows(em['delta_f'], label='%s<-%s' % (em['to'], em['from']))
        info = dict(list_path='.elementary_maps[*].delta_f', entries=sum(len(em['delta_f']) for em in m),
                    encoding='one elementary map (from,to) per column, rows (X,Y,Z,coeff)')
    else:  # sonnet55-b02/b08/b10
        l = d['coboundary']['delta_f']
        return None, dict(list_path='.coboundary.delta_f', entries=len(l),
                          encoding='rows (X,Y,Z,coeff) of delta f for one fixed f (gb profile) without phi labels')
    return D, info
