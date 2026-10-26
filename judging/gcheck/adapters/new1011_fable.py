"""Adapter for Claude Code batch runs, condition G, fable5 / fable51 / fable51-high (added 2026-10-11).

Only label/encoding translation; no Worker value is changed. Files read: the committed
data/C_<n>_gamma.json and data/C_<n>_coboundary.json of each run. Structure and evaluated
files use the default loaders (they load without errors for all runs here).

Gamma: list path and row encoding per run (GAMMA below), all taken from the run's own file:
  fable5-b02        .inhomogeneous_deformation.entries   row (X,Y,terms=[{gb,Z,coeff}])
  fable51-b02       .inhomogeneous_deformation.gamma     row (X,Y,Z,coeff="expr",linear_form={gb:c})
  fable51-b04       .inhomogeneous_deformation.gamma     row (X,Y,Z,coeff="expr",coeff_terms={gb:c})
  fable51-b06       .inhomogeneous_deformation.gamma     row (X,Y,Z,coeff={gb:c},expr="expr")
  fable51-b08       .inhomogeneous_deformation.gamma     row (X,Y,Z,coeff={gb:c},expr="expr")
  fable51-b10       .inhomogeneous_deformation.entries   row (X,Y,Z,coeff="expr",linear_form={gb:c})
  fable51-high-b02  .gamma                               row (X,Y,Z,terms=[{gb,coeff}])
  fable51-high-b04  .inhomogeneous_deformation.gamma     row (X,Y,Z,coeff={gb:c},linear_form="expr")
  The {gb: rational} dict is used as the value; where the row also carries a printable
  expression string, it is parsed as a linear form and must equal the dict (raise otherwise).
  K components: rows whose own Z is 'K' (each file states the target is g + C K with Z='K' the
  constant component). Exception, fable51-b06: the file states "constant (K) terms dropped"
  and keeps them in a separate list .inhomogeneous_deformation.dropped_constant_terms; the
  Worker's gamma is the .gamma list only (no K rows). The dropped list is NOT added; its row
  count is reported in the info dict.

gb label rule. Every file defines gb by "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa" and has a
gb_matrix with rows a_1_<sigma> and columns b_j_<s>. Labels -> reference key (sign of a, j, sign of b):
  gb_a1p_b1m, gb_a_1_p_b_1_m  -> loader.gbparse (a-sign, j, b-sign)  (fable51-*; e.g. b10 states
                                 "gb_a1{sigma}_b{k}{s} = gb_{sigma,k,s}")
  gb_p_1_m (gb_<sigma>_<j>_<s>) -> ('+', 1, '-')                     (fable5-b02; description
                                 "gb_{sigma,j,s}: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa")
  Cross-check: every gb_matrix cell (row a_1_<sigma>, column b_j_<s>) must map to
  (sigma, j, s) under the rule; the table forms are: 2-D list (labels/entries/parameters),
  flat row-major list of length rows*cols (fable5-b02 'labels', shape [2,2n]), or list of
  {label, fermion, boson} (fable51-high-b04). A mismatch or a missing table raises. Every
  gamma label must also be one of the gb_matrix labels (raise otherwise).

Coboundary (Worker's phi-labelled matrix A; phi labels kept as opaque strings):
  fable51-b02  .coboundary.entries row (X,Y,Z,linear_form={phi__to__from: c}); parameter list
               .odd_linear_map.parameters (36, K targets included as recorded); labels checked
               against that list.
  fable51-b08  .coboundary_symbolic row (X,Y,Z,coeff={phi[to][from]: c}); labels checked against
               .f_parameterization.unknowns. (Pairs only with index(X)<=index(Y), as the file states.)
  fable51-high-b04  default loader rows (phi,X,Y,Z,coeff) of .elementary_coboundaries.table.
  Others record only delta f of one fixed f (numeric for one gb profile, or a linear form in gb,
  i.e. columns are gb, not phi) -> (None, info), as the default loader does for unlabelled rows.
"""
import json, re
from fractions import Fraction as F
import sympy as sp
from loader import num, add, gbparse, path, entry_lists, _parse_param_list, PHI_KEYS

RUNS = ['thm01-R-fable5-b02-G'] + ['thm01-R-fable51-b%02d-G' % b for b in (2, 4, 6, 8, 10)] + \
       ['thm01-R-fable51-high-b02-G', 'thm01-R-fable51-high-b04-G']


def _key(run):
    return run[len('thm01-R-'):-len('-G')]


def _get(d, p):
    for k in p:
        d = d[k]
    return d


# run -> (gamma list path, row form, path of gb_matrix)
GAMMA = {
    'fable5-b02': (('inhomogeneous_deformation', 'entries'), 'terms_z_inside', ('gb_matrix',)),
    'fable51-b02': (('inhomogeneous_deformation', 'gamma'), ('linear_form', 'coeff'), ('gb_matrix',)),
    'fable51-b04': (('inhomogeneous_deformation', 'gamma'), ('coeff_terms', 'coeff'), ('gb_matrix',)),
    'fable51-b06': (('inhomogeneous_deformation', 'gamma'), ('coeff', 'expr'),
                    ('inhomogeneous_deformation', 'gb_matrix')),
    'fable51-b08': (('inhomogeneous_deformation', 'gamma'), ('coeff', 'expr'),
                    ('inhomogeneous_deformation', 'gb_matrix')),
    'fable51-b10': (('inhomogeneous_deformation', 'entries'), ('linear_form', 'coeff'), ('gb_matrix',)),
    'fable51-high-b02': (('gamma',), 'terms_z_outside', ('inhomogeneous_deformation', 'gb_matrix')),
    'fable51-high-b04': (('inhomogeneous_deformation', 'gamma'), ('coeff', 'linear_form'), ('gb_matrix',)),
}


def gb3(label):
    """gb label -> (a sign, j, b sign). loader.gbparse plus gb_<sigma>_<j>_<s>."""
    m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', label)
    if m:
        return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')
    return gbparse(label)


def _check_gb_matrix(g):
    rows = g['rows']
    cols = g.get('columns', g.get('cols'))
    cells = []   # (label, row name, col name)
    tab = next((g[k] for k in ('labels', 'entries', 'parameters') if k in g), None)
    if tab is None:
        raise ValueError('gb_matrix without table')
    if isinstance(tab[0], dict):
        cells = [(e['label'], e['fermion'], e['boson']) for e in tab]
        for e in tab:
            if rows[e['row']] != e['fermion'] or cols[e['col']] != e['boson']:
                raise ValueError('gb_matrix entry %s: row/col index disagrees with fermion/boson' % e)
    elif isinstance(tab[0], list):
        cells = [(tab[i][j], r, c) for i, r in enumerate(rows) for j, c in enumerate(cols)]
    else:   # flat list, row-major
        if len(tab) != len(rows) * len(cols):
            raise ValueError('flat gb_matrix labels: length %d != %d x %d' % (len(tab), len(rows), len(cols)))
        cells = [(tab[i * len(cols) + j], r, c) for i, r in enumerate(rows) for j, c in enumerate(cols)]
    for lab, r, c in cells:
        ra, cb = r.split('_'), c.split('_')
        want = ('+' if ra[2] == 'p' else '-', int(cb[1]), '+' if cb[2] == 'p' else '-')
        if gb3(lab) != want:
            raise ValueError('gb label %s at (%s,%s) does not follow the rule' % (lab, r, c))
    return {lab for lab, _r, _c in cells}, 'gb_matrix cross-checked (%dx%d)' % (len(rows), len(cols))


def _linear(s):
    """Linear expression string -> {symbol name: Fraction}. Raises if not linear."""
    names = sorted(set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', str(s))))
    loc = {nm: sp.Symbol(nm) for nm in names}
    e = sp.expand(sp.sympify(str(s), locals=loc))
    out = {}
    for nm, sym in loc.items():
        c = sp.diff(e, sym)
        if c.free_symbols:
            raise ValueError('non-linear coefficient %r' % s)
        if c != 0:
            c = sp.Rational(c)
            out[nm] = F(int(c.p), int(c.q))
    rest = sp.expand(e - sum(sp.Rational(v.numerator, v.denominator) * loc[k] for k, v in out.items()))
    if rest != 0:
        raise ValueError('constant/non-linear part %r in %r' % (rest, s))
    return out


def load_gamma(run, n):
    k = _key(run)
    d = json.load(open(path(run, n, 'gamma')))
    lp, form, gp = GAMMA[k]
    labels, chk = _check_gb_matrix(_get(d, gp))
    l = _get(d, lp)
    D = {}
    xchecked = 0

    def put(lab, X, Y, Z, c):
        if lab not in labels:
            raise ValueError('gamma label %s not in gb_matrix' % lab)
        add(D, gb3(lab), (X, Y, Z), c)

    for e in l:
        X, Y = e['X'], e['Y']
        if form == 'terms_z_inside':
            for t in e['terms']:
                put(t['gb'], X, Y, t['Z'], num(t['coeff']))
        elif form == 'terms_z_outside':
            for t in e['terms']:
                put(t['gb'], X, Y, e['Z'], num(t['coeff']))
        else:
            dk, sk = form
            dv = {lab: num(c) for lab, c in e[dk].items()}
            dv = {lab: c for lab, c in dv.items() if c != 0}
            if sk in e:
                if _linear(e[sk]) != dv:
                    raise ValueError('row %s: %s=%r disagrees with %s=%r' % ((X, Y, e['Z']), sk, e[sk], dk, e[dk]))
                xchecked += 1
            for lab, c in dv.items():
                put(lab, X, Y, e['Z'], c)
    if form == 'terms_z_inside':
        enc = 'row (X,Y,terms=[{gb,Z,coeff}])'
    elif form == 'terms_z_outside':
        enc = 'row (X,Y,Z,terms=[{gb,coeff}])'
    else:
        enc = 'row (X,Y,Z,%s={gb:c}); %s string cross-checked in %d rows' % (form[0], form[1], xchecked)
    info = dict(list_path='.' + '.'.join(lp), entries=len(l), encoding=enc + '; ' + chk)
    if k == 'fable51-b06':
        dr = d['inhomogeneous_deformation'].get('dropped_constant_terms', [])
        info['dropped_constant_terms_not_included'] = len(dr)
        info['dropped_constant_terms_Z'] = sorted({e['Z'] for e in dr})
    return D, info


def load_coboundary(run, n):
    k = _key(run)
    d = json.load(open(path(run, n, 'coboundary')))
    D = {}
    if k == 'fable51-b02':
        params = {p['label'] for p in d['odd_linear_map']['parameters']}
        l = d['coboundary']['entries']
        for e in l:
            for lab, c in e['linear_form'].items():
                if lab not in params:
                    raise ValueError('phi label %s not in odd_linear_map.parameters' % lab)
                add(D, lab, (e['X'], e['Y'], e['Z']), num(c))
        return D, dict(list_path='.coboundary.entries', entries=len(l),
                       encoding='row (X,Y,Z,linear_form={phi__to__from:c}); %d parameters' % len(params))
    if k == 'fable51-b08':
        params = set(d['f_parameterization']['unknowns'])
        l = d['coboundary_symbolic']
        for e in l:
            for lab, c in e['coeff'].items():
                if lab not in params:
                    raise ValueError('phi label %s not in f_parameterization.unknowns' % lab)
                add(D, lab, (e['X'], e['Y'], e['Z']), num(c))
        return D, dict(list_path='.coboundary_symbolic', entries=len(l),
                       encoding='row (X,Y,Z,coeff={phi[to][from]:c}); %d unknowns; pairs index(X)<=index(Y)'
                       % len(params))
    if k == 'fable51-high-b04':   # same as the default loader
        for p, l in entry_lists(d):
            D, enc = _parse_param_list(l, PHI_KEYS, str)
            if D is not None:
                return D, dict(list_path=p, entries=len(l), encoding=enc)
        raise ValueError('no phi-labelled coboundary list')
    reason = {
        'fable5-b02': '.coboundary: numeric delta f for one f (gb_assignment all_plus_one); no phi labels',
        'fable51-b04': '.coboundary.entries: delta f for one f family (odd_linear_map given in gb), '
                       'coefficients linear in gb; columns are gb, not phi',
        'fable51-b06': '.delta_f: delta f for the canonical odd map (odd_map_f.phi given in gb); columns are gb, not phi',
        'fable51-b10': '.coboundary.entries: numeric delta f for one f (profile all_plus); .symbolic: same in gb; no phi labels',
        'fable51-high-b02': '.coboundary: numeric delta f for one f (canonical_gb, all_plus_one); no phi labels',
    }[k]
    return None, dict(file='C_%d_coboundary.json' % n, reason=reason)
