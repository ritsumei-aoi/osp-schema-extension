"""Adapter for the May runs (thm01-01/02/04/05) and the interactive thm01-R luna / sonnet46 runs.

Only translates encodings and labels; Worker values are never changed.
Per-run table _CFG gives, for each run, the JSON list path of the gamma rows and of the
coboundary rows (None = the file holds no phi-labelled coboundary data), and the
gb-label rule.

Row encodings handled (one coefficient field per row, see _terms):
  - '<param key>' + numeric 'coeff'            (one row per (X,Y,Z,param))
  - coefficient dict {label: coeff}            ('coeff', 'coeff_gb', 'coeff_phi', 'gamma_coeff', 'coboundary_coeff')
  - list of terms [{parameter|gb|phi: label, coeff|scalar: c}]   ('coefficients', 'terms', 'gb_terms', 'phi_terms')
  - string linear expression in labels, e.g. '-2*gb_a1p_b1p' or 'phi_a + 2*phi_b'
    (parsed with sympy; must be homogeneous linear, otherwise ValueError)
thm01-R-sonnet46-A1 uses keys a, b, c for X, Y, Z (its metadata: 'gamma^c_{ab}: coefficient of
e_c in gamma(e_a, e_b)', index_convention 'upper_c'); mapped a->X, b->Y, c->Z.

gb labels (mapped to the reference tuple (sigma, j, s) of [b_j^s, a_1^sigma] = -gb kappa):
  - gb_a1p_b1p, gb_a1_p_b1_p, gb_a_1_p_b_1_p: loader.gbparse (a-sign, b index, b-sign).
  - gb_p_1_p (sonnet46-G, -A1, -r3-G): 'gb_{sigma}_{j}_{s}' as documented by the Worker
    (sonnet46-G gb_matrix.index_description 'gb[sigma][j][s] = gb_{a_1^sigma, b_j^s}';
    sonnet46-r3-G gb_matrix.description 'gb_{sigma}_{j}_{s}'; sonnet46-A1
    gb_matrix.entries[a_1_sigma][b_j_s] = 'gb_sigma_j_s').
  - gb_p1_p (sonnet46-r2-G): taken from the Worker's own gb_matrix.parameters[label]
    fields sigma / k / s.
Realization words 'a1p' / 'b2m' (sonnet46-G) are rewritten to 'a_1_p' / 'b_2_m'.

thm01-01: C_n_structure.json has no generator realization. The realization is recorded by
the Worker in docs/math/Cn1_definition.md, table 'Generator label convention (JSON
schema)' (same as src/C_generators.py get_generators). It is transcribed in
_thm0101_realization below (E_2del{k}_p = (b_k^+)^2, NOT the 1/2 (b_n^+)^2 of the
'Simple generators' display in the same document). The structure_constants vs realization
check in analyze.py tests this transcription against the Worker's own structure constants.

evaluated_info: reads every data/C_n_evaluated*.json; list_path is prefixed by the file name.
"""
import glob, json, os, re
import sympy as sp
from loader import num, add, entry_lists, gbparse, FG_ROOT

RUNS = ['thm01-01', 'thm01-02', 'thm01-04', 'thm01-05',
        'thm01-R-luna-A', 'thm01-R-luna-A2', 'thm01-R-luna-F', 'thm01-R-luna-G', 'thm01-R-luna-r3-G',
        'thm01-R-sonnet46-A1', 'thm01-R-sonnet46-F', 'thm01-R-sonnet46-G',
        'thm01-R-sonnet46-r2-G', 'thm01-R-sonnet46-r3-G']

# run: (gamma list path, coboundary list path or None, gb rule)
_CFG = {
    'thm01-01': ('inhomogeneous_deformation.gamma_matrix', 'coboundary_matrix', 'loader'),
    'thm01-02': ('inhomogeneous_deformation.gamma_structure', None, 'loader'),
    'thm01-04': ('inhomogeneous_deformation.gamma_matrix', None, 'loader'),
    'thm01-05': ('inhomogeneous_deformation.gamma_matrix', 'coboundary_map.coboundary_coefficients', 'loader'),
    'thm01-R-luna-A': ('inhomogeneous_deformation.gamma_structure', 'coboundary.coboundary_structure', 'loader'),
    'thm01-R-luna-A2': ('inhomogeneous_deformation.gamma_structure', 'coboundary.structure', 'loader'),
    'thm01-R-luna-F': ('inhomogeneous_deformation.gamma_coefficients', 'coboundary_coefficients', 'loader'),
    'thm01-R-luna-G': ('inhomogeneous_deformation.gamma_coefficients', 'coboundary_definition.coboundary_coefficients', 'loader'),
    'thm01-R-luna-r3-G': ('inhomogeneous_deformation.gamma_coefficients', 'coboundary.coefficients', 'loader'),
    'thm01-R-sonnet46-A1': ('gamma_cocycle', 'coboundary', 'sigma_j_s'),
    'thm01-R-sonnet46-F': ('inhomogeneous_deformation.gamma_entries', 'coboundary_entries', 'loader'),
    'thm01-R-sonnet46-G': ('gamma_coefficients', 'coboundary_coefficients', 'sigma_j_s'),
    'thm01-R-sonnet46-r2-G': ('gamma_coefficients', 'coboundary_coefficients', 'gb_matrix_fields'),
    'thm01-R-sonnet46-r3-G': ('inhomogeneous_deformation.gamma_coefficients', 'coboundary_coefficients', 'sigma_j_s'),
}

PARAM_KEYS = ('parameter', 'gb', 'gb_label', 'phi', 'phi_label')
DICT_OR_EXPR_KEYS = ('coeff_gb', 'coeff_phi', 'gamma_coeff', 'coboundary_coeff', 'coeff')
TERM_LIST_KEYS = ('coefficients', 'terms', 'gb_terms', 'phi_terms')


def _data(run, n, pattern):
    fs = sorted(glob.glob(os.path.join(FG_ROOT, run, 'data', pattern % n)))
    if not fs:
        raise FileNotFoundError('%s: no data/%s' % (run, pattern % n))
    return fs


def _get(d, p):
    for k in p.split('.'):
        d = d[k]
    return d


_IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


def _linexpr(s):
    """'-2*gb_x + gb_y/2' -> {'gb_x': F(-2), 'gb_y': F(1,2)}; must be homogeneous linear."""
    names = set(_IDENT.findall(s))
    syms = {nm: sp.Symbol(nm) for nm in names}
    e = sp.expand(sp.sympify(s, locals=syms))
    if e == 0:
        return {}
    P = sp.Poly(e, *[syms[nm] for nm in sorted(names)])
    out = {}
    for mon, c in P.terms():
        if sum(mon) != 1:
            raise ValueError('non-linear or constant term in %r' % s)
        nm = sorted(names)[mon.index(1)]
        c = sp.Rational(c)
        out[nm] = num('%d/%d' % (c.p, c.q))
    return out


def _terms(e):
    """Yield (label, Fraction) for one row, plus a short encoding tag."""
    pk = next((k for k in PARAM_KEYS if k in e), None)
    if pk is not None and 'coeff' in e and not isinstance(e['coeff'], (dict, list)):
        return [(e[pk], num(e['coeff']))], "(X,Y,Z,%s,coeff)" % pk
    for k in TERM_LIST_KEYS:
        if k in e and isinstance(e[k], list):
            out = []
            for t in e[k]:
                lk = next(x for x in ('parameter', 'gb', 'phi', 'param') if x in t)
                ck = next(x for x in ('coeff', 'scalar', 'coefficient') if x in t)
                out.append((t[lk], num(t[ck])))
            return out, "(X,Y,Z,%s=[{label,coeff}])" % k
    for k in DICT_OR_EXPR_KEYS:
        if k in e:
            v = e[k]
            if isinstance(v, dict):
                return [(l, num(c)) for l, c in v.items()], "(X,Y,Z,%s={label: coeff})" % k
            if isinstance(v, str) and _IDENT.search(v):
                return list(_linexpr(v).items()), "(X,Y,Z,%s='linear expression in labels')" % k
    raise ValueError('cannot decode row %r' % (e,))


def _xyz(e):
    if 'X' in e:
        return e['X'], e['Y'], e['Z']
    return e['a'], e['b'], e['c']   # sonnet46-A1: gamma^c_{ab}


def _gb_rule(run, n):
    rule = _CFG[run][2]
    if rule == 'loader':
        return gbparse
    if rule == 'sigma_j_s':
        def f(s):
            m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', s)
            if not m:
                raise KeyError(s)
            pm = {'p': '+', 'm': '-'}
            return (pm[m[1]], int(m[2]), pm[m[3]])
        return f
    if rule == 'gb_matrix_fields':
        P = json.load(open(_data(run, n, 'C_%d_gamma.json')[0]))['gb_matrix']['parameters']
        tab = {lab: (v['sigma'], int(v['k']), v['s']) for lab, v in P.items()}
        assert all(t[0] in '+-' and t[2] in '+-' for t in tab.values())
        return lambda s: tab[s]
    raise KeyError(rule)


def _parse(rows, labelmap):
    """Rows whose argument X or Y is 'K' (thm01-01 treats K as an algebra element and records
    (delta f)(X, K)) are outside g x g, which is what analyze.py compares; they are skipped and
    counted (returned as the third value). Z == 'K' rows are kept."""
    D, encs, skipped = {}, set(), 0
    for e in rows:
        X, Y, Z = _xyz(e)
        if X == 'K' or Y == 'K':
            skipped += 1
            continue
        ts, enc = _terms(e)
        encs.add(enc)
        for lab, c in ts:
            add(D, labelmap(lab), (X, Y, Z), c)
    return D, ' | '.join(sorted(encs)), skipped


def load_gamma(run, n):
    f = _data(run, n, 'C_%d_gamma.json')[0]
    p = _CFG[run][0]
    rows = _get(json.load(open(f)), p)
    D, enc, sk = _parse(rows, _gb_rule(run, n))
    return D, dict(list_path='.' + p, entries=len(rows), encoding='one row per ' + enc,
                   skipped_rows_with_K_argument=sk)


def load_coboundary(run, n):
    f = _data(run, n, 'C_%d_coboundary*.json')
    if len(f) != 1:
        raise ValueError('%s: expected one coboundary file, got %s' % (run, f))
    f = f[0]
    p = _CFG[run][1]
    d = json.load(open(f))
    if p is None:
        lists = list(entry_lists(d))
        if lists:
            info = '; '.join('%s: %d rows (X,Y,Z,coeff) without phi labels: keys=%s'
                             % (lp, len(l), sorted({k for e in l for k in e})) for lp, l in lists)
        else:
            info = 'no (X,Y,Z) rows; top-level keys=%s' % sorted(d)
        return None, dict(file=os.path.basename(f), list_path=None, entries=0, encoding=info)
    rows = _get(d, p)
    D, enc, sk = _parse(rows, str)
    return D, dict(file=os.path.basename(f), list_path='.' + p, entries=len(rows), encoding='one row per ' + enc,
                   skipped_rows_with_K_argument=sk)


def evaluated_info(run, n):
    out = []
    for f in _data(run, n, 'C_%d_evaluated*.json'):
        d = json.load(open(f))
        for p, l in entry_lists(d):
            out.append(dict(list_path=os.path.basename(f) + ':' + p, entries=len(l),
                            keys=sorted({k for e in l for k in e})))
    return out


def _word(w):
    m = re.fullmatch(r'([ab])(\d+)([pm])', w)      # sonnet46-G: 'a1p' -> 'a_1_p'
    return '%s_%s_%s' % (m[1], m[2], m[3]) if m else w


def _thm0101_realization(n):
    """Transcribed from thm01-01 docs/math/Cn1_definition.md, 'Generator label convention' tables."""
    bp = lambda k: 'b_%d_p' % k
    bm = lambda k: 'b_%d_m' % k
    R = {'H_1': [(1, ['a_1_p', 'a_1_m']), (1, [bp(1), bm(1)])]}
    for k in range(2, n + 1):
        R['H_%d' % k] = [(1, [bp(k - 1), bm(k - 1)]), (-1, [bp(k), bm(k)])]
    R['H_%d' % (n + 1)] = [(-1, [bp(n), bm(n)]), (num('-1/2'), [])]
    for k in range(1, n + 1):
        R['E_2del%d_p' % k] = [(1, [bp(k), bp(k)])]
        R['E_2del%d_m' % k] = [(1, [bm(k), bm(k)])]
        R['E_eps1_del%d_pp' % k] = [(1, ['a_1_p', bp(k)])]
        R['E_eps1_del%d_pm' % k] = [(1, ['a_1_p', bm(k)])]
        R['E_eps1_del%d_mp' % k] = [(1, ['a_1_m', bp(k)])]
        R['E_eps1_del%d_mm' % k] = [(1, ['a_1_m', bm(k)])]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            R['E_del%d_del%d_pp' % (i, j)] = [(1, [bp(i), bp(j)])]
            R['E_del%d_del%d_mm' % (i, j)] = [(1, [bm(i), bm(j)])]
            R['E_del%d_del%d_pm' % (i, j)] = [(1, [bp(i), bm(j)])]
            R['E_del%d_del%d_mp' % (i, j)] = [(1, [bm(i), bp(j)])]
    return {g: [(num(c), ws) for c, ws in v] for g, v in R.items()}


def load_structure(run, n):
    S = json.load(open(_data(run, n, 'C_%d_structure.json')[0]))
    B = S['basis']
    basis = list(B['even']) + list(B['odd'])
    parity = {x: 0 for x in B['even']} | {x: 1 for x in B['odd']}
    if run == 'thm01-01':
        if 'generator_realization' in S:
            raise ValueError('thm01-01 now has generator_realization; adapter assumption outdated')
        R = _thm0101_realization(n)
        missing = set(basis) ^ set(R)
        if missing:
            raise ValueError('thm01-01: transcribed realization does not match basis: %s' % sorted(missing))
        real = {g: R[g] for g in basis}
    else:
        GR = S['generator_realization']
        R = GR.get('realizations', GR)
        real = {g: [(num(t['coeff']), [_word(w) for w in t['words']]) for t in R[g]['standard_form']]
                for g in basis}
    sc = {}
    for e in S.get('structure_constants', []):
        sc.setdefault((e['X'], e['Y']), {})[e['Z']] = num(e['coeff'])
    return basis, parity, real, sc
