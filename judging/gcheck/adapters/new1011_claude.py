"""Adapter for Claude Code batch runs, condition G, added 2026-10-11
(haiku45-v293-b02, haiku55-b02/b04/b06/b08/b10, opus46-high-b02/b04, sonnet46-b12/b14/b16/b18/b20).

Only label / encoding translation of the Worker JSON; no Worker value is changed.
Every rule below was read from the run's own files; where the file carries its own
definition of a label, the rule is cross-checked against it and a mismatch raises.

Structure (C_<n>_structure.json)
- default loader, except:
  * opus46-high-b02/b04, sonnet46-b12: structure_constants rows are (X, Y, result=[{Z, coeff}]);
    each result term is one (X,Y,Z,coeff) entry.
  * haiku55-b02: structure_constants = {brackets: [(X,Y,Z,coeff,kappa_coeff)], constant_terms: []}.
    'brackets' rows are taken as (X,Y,Z,coeff); kappa_coeff must be "0" (Schema 1 file,
    metadata.gb_provided=False) and constant_terms must be empty, otherwise ValueError
    (no format for them is defined in the file). generator_realization has no
    'realizations' level (default handles that).
  * haiku55-b02, sonnet46-b12: oscillator words are written 'a1p', 'b2m'. Rule
    <a|b><k><p|m> -> <a|b>_<k>_<p|m> (refmodel.osc format). Source: haiku55-b02
    handover/notation.md ('a1p' = a_1^+) and docs/issues/I01.md ("oscillators a1p, a1m, bkp,
    bkm in the code; a_1_p, a_1_m, b_k_p, b_k_m in JSON"); sonnet46-b12 frappat_form of every
    generator (e.g. 'a1p b1p' <-> 'a_1^+ b_1^+'). Cross-checks: the translated words must be
    the set oscillator_generators.labels (haiku55-b02, JSON form) resp. the untranslated words
    must be oscillator_generators.labels (sonnet46-b12) and, for sonnet46-b12, each translated
    word a_k_s must occur as a_k^{+|-} in the generator's frappat_form.

Gamma (C_<n>_gamma.json) -> {(sign of a_1, j, sign of b_j): {(X,Y,Z): c}}
All files define gb through "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa"; the reference key is
(sigma, j, s). Row encodings / list paths / label rules per run:
  haiku55-b02   .inhomogeneous_deformation.gamma, row (X,Y,Z,terms={gb: c});
                label gb_a1<s>_b<j><s> -> loader.gbparse; checked vs gb_matrix rows x columns.
  haiku55-b04   .gamma, row (X,Y,Z,terms=[{gb, coeff}]); loader.gbparse;
                checked vs gb_matrix.parameters (label, sigma, k, s).
  haiku55-b06   .inhomogeneous_deformation.gamma, row (X,Y,Z,coeff="linear expr in gb");
                label gb_<sigma>_<j>_<s>; checked vs gb_matrix rows x cols.
  haiku55-b08   .inhomogeneous_deformation.gamma, row (X,Y,Z,coeff="linear expr in gb");
                label gb_a_1_<sigma>__b_<j>_<s>; checked vs gb_matrix rows x columns
                (description "row = fermion a_1^sigma, column = boson b_j^s").
  opus46-high-b02 .gamma_coefficients, row (X,Y,gb_parameter,result=[{Z,coeff}]); loader.gbparse;
                checked vs gb_matrix.parameters (label, fermion a_1_<sigma>, boson b_<j>_<s>).
  opus46-high-b04 .gamma_coefficients, row (X,Y,result=[{Z,coeff,gb_param}]); label
                gb_a1<sigma>_b<j>_<s> -> loader.gbparse; checked vs gb_matrix.parameters.
  sonnet46-b12  .inhomogeneous_deformation.gamma_coefficients, row (X,Y,Z,coeff_expr="linear expr");
                label gb_<sigma><j><s>; checked vs gb_matrix.parameters (label, fermion a1<sigma>,
                boson b<j><s>).
  sonnet46-b14  .gamma_coefficients, row (X,Y,Z,gb_param,coeff); label gb_<sigma>_<j>_<s>;
                checked vs gb_matrix.parameters {label: {sigma, j, s}}.
  sonnet46-b16  .inhomogeneous_deformation.gamma_coefficients, row (X,Y,Z,gb_param,coeff);
                label gb_<sigma><j><s>: gb_matrix.index_convention "sigma in {p,m} for a_1^sigma,
                j in 1..n, s in {p,m} for b_j^s" and docs/issues/I05.md "Label convention:
                gb_{sigma}{j}{s} (e.g. gb_p1p = gb_{a_1^+, b_1^+})"; checked that the labels used
                are exactly gb_matrix.labels (no per-label table in the file).
  sonnet46-b18  .inhomogeneous_deformation.gamma_coefficients, row (X,Y,Z,coeff_expr="linear expr");
                loader.gbparse; checked labels used == gb_matrix.parameters (list of names only).
                (The file's top-level .structure_constants list is the Schema 1 copy, not gamma.)
  sonnet46-b20  .inhomogeneous_deformation.gamma_coefficients, row (X,Y,Z,gamma_coeff="linear expr");
                loader.gbparse; checked vs gb_matrix.parameters {label: {index: {sigma, j, s}}}.
  haiku55-b10   .inhomogeneous_deformation.entries, row (X,Y,Z,gb,coeff), plus
                .inhomogeneous_deformation.K_components, row (X,Y,gb,coeff) without Z. The run's
                docs/json_schema_specification.md (Schema 2) states: "`entries` gives the g-valued
                gamma: the coefficient of kappa*gb*Z" and "`K_components` gives the coefficient of
                kappa*gb*K (K = identity)"; so Z = 'K' is assigned to K_components rows.
                Label gb_a1<sigma>_b<j><s> -> loader.gbparse; checked vs gb_matrix: rows = sign of
                a_1 ('+','-'), columns b_<j>_<s>, labels = flat list in row-major order of shape
                [2, 2n] (same spec, whose example lists gb_a1p_b1p, gb_a1p_b1m, gb_a1m_b1p, ...).
  haiku45-v293-b02: no gamma rows (inhomogeneous_deformation.note = "To be computed for specific
                representations") -> (None, info).
K components: rows whose Z is the literal 'K' (haiku55-b02/b04/b06/b08, sonnet46-b12), and the
K_components list of haiku55-b10 (see above). The other
files contain no Z='K' row and no separate central list; their K part is empty as recorded.
Linear expressions are parsed with every identifier as a symbol; a non-linear or constant
term, or a symbol that is not a declared gb label, raises ValueError.

Coboundary (C_<n>_coboundary.json) -> Worker's phi-labelled A (labels kept as strings)
  haiku55-b02   .coboundary.terms, row (X,Y,Z,phi={phi_i_j: c}).
  haiku55-b04   .maps[k] = {name, source, target, entries [(X,Y,Z,coeff)]}: column label 'name'
                (checked name == '<source>-><target>').
  haiku55-b06   .coboundary.entries, row (X,Y,Z,coeff="linear expr in phi_i_j") (symbols checked
                against map.parameters[].symbol).
  haiku55-b10   .maps[k] = {i, j, coboundary [(X,Y,Z,coeff)]}, file map_convention "f(X_j) = X_i,
                other basis elements to 0": column label '<i><-<j>' (checked p(i) != p(j)).
  haiku55-b08   .coboundary_maps[k] = {phi, map, coboundary_entries [(X,Y,Z,coeff)]}: label 'phi'.
  opus46-high-b02 .coboundary_coefficients, row (X,Y,phi_parameter,result=[{Z,coeff}]).
  opus46-high-b04 .coboundary_coefficients, row (X,Y,result=[{Z,phi_param,coeff}]).
  sonnet46-b12  .coboundary.coefficients, row (X,Y,Z,coeff_expr) with symbols written
                'phi_{A,B}'; each such token is one opaque column label.
  sonnet46-b14, sonnet46-b16: default loader (row (X,Y,Z,phi_param,coeff)).
  sonnet46-b18, sonnet46-b20: default loader -> rows of delta f for one fixed f, no phi labels.
  haiku45-v293-b02: coboundary_allpos file, coboundary_data.coboundary_coefficients = [] -> (None, info).

Evaluated files: default, except haiku45-v293-b02 whose files are C_<n>_evaluated_allpos.json
(and C_<n>_coboundary_allpos.json); there is no C_<n>_evaluated.json in that run.
"""
import json, os, re
from fractions import Fraction as F
import sympy as sp
from loader import num, add, gbparse, path, entry_lists

RUNS = ['thm01-R-haiku45-v293-b02-G', 'thm01-R-haiku55-b02-G', 'thm01-R-haiku55-b04-G',
        'thm01-R-haiku55-b06-G', 'thm01-R-haiku55-b08-G', 'thm01-R-haiku55-b10-G', 'thm01-R-opus46-high-b02-G',
        'thm01-R-opus46-high-b04-G', 'thm01-R-sonnet46-b12-G', 'thm01-R-sonnet46-b14-G',
        'thm01-R-sonnet46-b16-G', 'thm01-R-sonnet46-b18-G', 'thm01-R-sonnet46-b20-G']

PM = {'p': '+', 'm': '-', '+': '+', '-': '-'}


def _key(run):
    return run[len('thm01-R-'):-len('-G')]


def _get(d, p):
    for k in p.split('.'):
        d = d[k]
    return d


# ---------------- gb label rules ----------------
def gb_s_j_s(s):          # gb_<sigma>_<j>_<s>
    m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', s)
    if not m:
        raise KeyError(s)
    return (PM[m[1]], int(m[2]), PM[m[3]])


def gb_sjs(s):            # gb_<sigma><j><s>
    m = re.fullmatch(r'gb_([pm])(\d+)([pm])', s)
    if not m:
        raise KeyError(s)
    return (PM[m[1]], int(m[2]), PM[m[3]])


def gb_dbl(s):            # gb_a_1_<sigma>__b_<j>_<s>
    m = re.fullmatch(r'gb_a_1_([pm])__b_(\d+)_([pm])', s)
    if not m:
        raise KeyError(s)
    return (PM[m[1]], int(m[2]), PM[m[3]])


GBRULE = {
    'haiku55-b02': gbparse, 'haiku55-b04': gbparse, 'haiku55-b06': gb_s_j_s, 'haiku55-b08': gb_dbl,
    'haiku55-b10': gbparse,
    'opus46-high-b02': gbparse, 'opus46-high-b04': gbparse, 'sonnet46-b12': gb_sjs,
    'sonnet46-b14': gb_s_j_s, 'sonnet46-b16': gb_sjs, 'sonnet46-b18': gbparse, 'sonnet46-b20': gbparse,
}


def _osc(name):
    """'a_1_p' / 'b_2_m' -> (letter, k, sign)."""
    m = re.fullmatch(r'([ab])_(\d+)_([pm])', name)
    if not m:
        raise ValueError('oscillator label %r' % name)
    return m[1], int(m[2]), PM[m[3]]


def _osc_short(name):
    """'a1p' -> (letter, k, sign)."""
    m = re.fullmatch(r'([ab])(\d+)([pm])', name)
    if not m:
        raise ValueError('oscillator label %r' % name)
    return m[1], int(m[2]), PM[m[3]]


def _gb_table(k, d):
    """The file's own gb definitions as {label: (sigma, j, s)}; None if only a list of names."""
    T = {}
    if k in ('haiku55-b02', 'haiku55-b06', 'haiku55-b08'):
        g = d['gb_matrix']
        cols = g.get('columns', g.get('cols'))
        for i, r in enumerate(g['rows']):
            a = _osc(r)
            for j, c in enumerate(cols):
                b = _osc(c)
                if a[0] != 'a' or b[0] != 'b':
                    raise ValueError('gb_matrix row/col %s/%s' % (r, c))
                T[g['entries'][i][j]] = (a[2], b[1], b[2])
    elif k == 'haiku55-b10':
        g = d['gb_matrix']
        rows, cols, labs = g['rows'], g['columns'], g['labels']
        if list(g['shape']) != [len(rows), len(cols)] or len(labs) != len(rows) * len(cols):
            raise ValueError('gb_matrix shape %s vs rows/columns/labels' % g['shape'])
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                b = _osc(c)
                if b[0] != 'b':
                    raise ValueError('gb_matrix column %s' % c)
                T[labs[i * len(cols) + j]] = (PM[r], b[1], b[2])
    elif k == 'haiku55-b04':
        for p in d['gb_matrix']['parameters']:
            T[p['label']] = (PM[p['sigma']], int(p['k']), PM[p['s']])
    elif k in ('opus46-high-b02', 'opus46-high-b04'):
        for p in d['gb_matrix']['parameters']:
            a, b = _osc(p['fermion']), _osc(p['boson'])
            T[p['label']] = (a[2], b[1], b[2])
    elif k == 'sonnet46-b12':
        for p in d['inhomogeneous_deformation']['gb_matrix']['parameters']:
            a, b = _osc_short(p['fermion']), _osc_short(p['boson'])
            T[p['label']] = (a[2], b[1], b[2])
    elif k == 'sonnet46-b14':
        for lab, p in d['gb_matrix']['parameters'].items():
            T[lab] = (PM[p['sigma']], int(p['j']), PM[p['s']])
    elif k == 'sonnet46-b20':
        for lab, p in d['gb_matrix']['parameters'].items():
            ix = p['index']
            T[lab] = (PM[ix['sigma']], int(ix['j']), PM[ix['s']])
    else:
        return None
    return T


def _gb_names(k, d):
    if k == 'sonnet46-b16':
        return set(d['gb_matrix']['labels'])
    if k == 'sonnet46-b18':
        return set(d['inhomogeneous_deformation']['gb_matrix']['parameters'])
    return set(_gb_table(k, d))


# ---------------- linear expressions ----------------
def linear_terms(expr, allowed=None):
    """'2*gb_x - gb_y/2' -> {'gb_x': F(2), 'gb_y': F(-1,2)}; raises on non-linear/constant/unknown."""
    s = str(expr)
    toks = {}
    def sub(m):
        t = m.group(0)
        toks.setdefault(t, '_PHITOK%d' % len(toks))
        return toks[t]
    s2 = re.sub(r'phi_\{[^{}]*\}', sub, s)
    back = {v: k for k, v in toks.items()}
    names = sorted(set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', s2)))
    loc = {nm: sp.Symbol(nm) for nm in names}
    e = sp.expand(sp.sympify(s2, locals=loc))
    out, rest = {}, e
    for nm, sym in loc.items():
        c = sp.diff(e, sym)
        if c.free_symbols:
            raise ValueError('non-linear term in %r' % expr)
        if c != 0:
            c = sp.Rational(c)
            lab = back.get(nm, nm)
            if allowed is not None and lab not in allowed:
                raise ValueError('symbol %r in %r is not a declared label' % (lab, expr))
            out[lab] = F(int(c.p), int(c.q))
            rest = rest - c * sym
    if sp.simplify(rest) != 0:
        raise ValueError('constant term %s in %r' % (rest, expr))
    return out


# ---------------- structure ----------------
SHORT_WORDS = ('haiku55-b02', 'sonnet46-b12')
RESULT_SC = ('opus46-high-b02', 'opus46-high-b04', 'sonnet46-b12')


def load_structure(run, n):
    k = _key(run)
    S = json.load(open(path(run, n, 'structure')))
    B = S['basis']
    basis = list(B['even']) + list(B['odd'])
    parity = {x: 0 for x in B['even']} | {x: 1 for x in B['odd']}
    GR = S['generator_realization']
    R = GR.get('realizations', GR)
    real = {g: [(num(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    sc = {}
    if k in RESULT_SC:
        for e in S['structure_constants']:
            for t in e['result']:
                d = sc.setdefault((e['X'], e['Y']), {})
                if t['Z'] in d:
                    raise ValueError('duplicate Z %s in structure row %s,%s' % (t['Z'], e['X'], e['Y']))
                d[t['Z']] = num(t['coeff'])
    elif k == 'haiku55-b02':
        SC = S['structure_constants']
        if set(SC) != {'brackets', 'constant_terms'} or SC['constant_terms']:
            raise ValueError('haiku55-b02 structure_constants keys %s / constant_terms %r'
                             % (sorted(SC), SC.get('constant_terms')))
        for e in SC['brackets']:
            if num(e['kappa_coeff']) != 0:
                raise ValueError('nonzero kappa_coeff in Schema 1 row %s' % e)
            sc.setdefault((e['X'], e['Y']), {})[e['Z']] = num(e['coeff'])
    else:
        for e in S.get('structure_constants', []):
            sc.setdefault((e['X'], e['Y']), {})[e['Z']] = num(e['coeff'])
    if k in SHORT_WORDS:
        osc = S['oscillator_generators']
        labels = list(osc['fermions']['labels']) + list(osc['bosons']['labels'])
        words = {w for terms in real.values() for _c, ws in terms for w in ws}
        def tr(x):
            a = _osc_short(x)
            return '%s_%d_%s' % (a[0], a[1], {'+': 'p', '-': 'm'}[a[2]])
        if k == 'haiku55-b02':
            if {tr(w) for w in words} != set(labels):
                raise ValueError('translated words %s != oscillator labels %s' % (sorted(words), labels))
        else:
            if words != set(labels):
                raise ValueError('words %s != oscillator labels %s' % (sorted(words), labels))
            for g in basis:
                ff = R[g].get('frappat_form')
                for _c, ws in real[g]:
                    for w in ws:
                        a = _osc_short(w)
                        if '%s_%d^%s' % a not in ff:
                            raise ValueError('word %s not in frappat_form %r of %s' % (w, ff, g))
        real = {g: [(c, [tr(w) for w in ws]) for c, ws in terms] for g, terms in real.items()}
    return basis, parity, real, sc


# ---------------- gamma ----------------
GAMMA_PATH = {
    'haiku55-b02': 'inhomogeneous_deformation.gamma', 'haiku55-b04': 'gamma',
    'haiku55-b06': 'inhomogeneous_deformation.gamma', 'haiku55-b08': 'inhomogeneous_deformation.gamma',
    'haiku55-b10': 'inhomogeneous_deformation.entries',
    'opus46-high-b02': 'gamma_coefficients', 'opus46-high-b04': 'gamma_coefficients',
    'sonnet46-b12': 'inhomogeneous_deformation.gamma_coefficients', 'sonnet46-b14': 'gamma_coefficients',
    'sonnet46-b16': 'inhomogeneous_deformation.gamma_coefficients',
    'sonnet46-b18': 'inhomogeneous_deformation.gamma_coefficients',
    'sonnet46-b20': 'inhomogeneous_deformation.gamma_coefficients',
}
EXPR_FIELD = {'haiku55-b06': 'coeff', 'haiku55-b08': 'coeff', 'sonnet46-b12': 'coeff_expr',
              'sonnet46-b18': 'coeff_expr', 'sonnet46-b20': 'gamma_coeff'}


def _gamma_terms(k, e, names):
    """One row -> list of (gb label, Z, Fraction)."""
    if k == 'haiku55-b02':
        return [(g, e['Z'], num(c)) for g, c in e['terms'].items()]
    if k == 'haiku55-b04':
        return [(t['gb'], e['Z'], num(t['coeff'])) for t in e['terms']]
    if k == 'opus46-high-b02':
        return [(e['gb_parameter'], t['Z'], num(t['coeff'])) for t in e['result']]
    if k == 'opus46-high-b04':
        return [(t['gb_param'], t['Z'], num(t['coeff'])) for t in e['result']]
    if k in ('sonnet46-b14', 'sonnet46-b16'):
        return [(e['gb_param'], e['Z'], num(e['coeff']))]
    if k == 'haiku55-b10':
        return [(e['gb'], e['Z'], num(e['coeff']))]
    return [(g, e['Z'], c) for g, c in linear_terms(e[EXPR_FIELD[k]], names).items()]


def load_gamma(run, n):
    k = _key(run)
    if k == 'haiku45-v293-b02':
        d = json.load(open(path(run, n, 'gamma')))
        return None, dict(file=os.path.basename(path(run, n, 'gamma')),
                          reason='no gamma rows; inhomogeneous_deformation = %s'
                                 % json.dumps(d.get('inhomogeneous_deformation')))
    d = json.load(open(path(run, n, 'gamma')))
    rule = GBRULE[k]
    T = _gb_table(k, d)
    names = _gb_names(k, d)
    if T is not None:
        for lab, want in T.items():
            if rule(lab) != want:
                raise ValueError('gb label %s: rule gives %s, file defines %s' % (lab, rule(lab), want))
        chk = 'label rule cross-checked against the file definitions (%d labels)' % len(T)
    else:
        for lab in names:
            rule(lab)
        chk = 'labels checked against the declared label list (%d); no per-label table in file' % len(names)
    l = _get(d, GAMMA_PATH[k])
    D, used = {}, set()
    for e in l:
        for lab, Z, c in _gamma_terms(k, e, names):
            if lab not in names:
                raise ValueError('gb label %s not declared in the file' % lab)
            used.add(lab)
            add(D, rule(lab), (e['X'], e['Y'], Z), c)
    extra = ''
    if k == 'haiku55-b10':
        kl = d['inhomogeneous_deformation']['K_components']
        for e in kl:
            if 'Z' in e:
                raise ValueError('K_components row with Z: %s' % e)
            if e['gb'] not in names:
                raise ValueError('gb label %s not declared in the file' % e['gb'])
            add(D, rule(e['gb']), (e['X'], e['Y'], 'K'), num(e['coeff']))
        extra = ' + .inhomogeneous_deformation.K_components(%d, Z=K assigned)' % len(kl)
    enc = {'haiku55-b02': 'row (X,Y,Z,terms={gb:c})', 'haiku55-b04': 'row (X,Y,Z,terms=[{gb,coeff}])',
           'opus46-high-b02': 'row (X,Y,gb_parameter,result=[{Z,coeff}])',
           'opus46-high-b04': 'row (X,Y,result=[{Z,coeff,gb_param}])',
           'sonnet46-b14': 'row (X,Y,Z,gb_param,coeff)', 'haiku55-b10': 'row (X,Y,Z,gb,coeff)', 'sonnet46-b16': 'row (X,Y,Z,gb_param,coeff)'}.get(
        k, 'row (X,Y,Z,%s="linear expr in gb")' % EXPR_FIELD.get(k))
    return D, dict(list_path='.' + GAMMA_PATH[k] + extra, entries=len(l),
                   encoding='%s; gb rule %s; %s' % (enc, rule.__name__, chk))


# ---------------- coboundary ----------------
def load_coboundary(run, n):
    k = _key(run)
    if k == 'haiku45-v293-b02':
        f = path(run, n, 'coboundary_allpos')
        d = json.load(open(f))
        l = d['coboundary_data']['coboundary_coefficients']
        if l:
            raise ValueError('haiku45-v293-b02 coboundary_coefficients not empty (%d rows)' % len(l))
        return None, dict(file=os.path.basename(f), reason='coboundary_data.coboundary_coefficients is an empty list')
    if k in ('sonnet46-b14', 'sonnet46-b16', 'sonnet46-b18', 'sonnet46-b20'):
        return _default_coboundary(run, n)
    d = json.load(open(path(run, n, 'coboundary')))
    D = {}
    if k == 'haiku55-b02':
        l = d['coboundary']['terms']
        for e in l:
            for ph, c in e['phi'].items():
                add(D, ph, (e['X'], e['Y'], e['Z']), num(c))
        info = dict(list_path='.coboundary.terms', entries=len(l), encoding='row (X,Y,Z,phi={phi:c})')
    elif k == 'haiku55-b04':
        m = d['maps']
        for mp in m:
            if mp['name'] != '%s->%s' % (mp['source'], mp['target']):
                raise ValueError('map name %s vs source/target' % mp['name'])
            for e in mp['entries']:
                add(D, mp['name'], (e['X'], e['Y'], e['Z']), num(e['coeff']))
        info = dict(list_path='.maps[*].entries', entries=sum(len(mp['entries']) for mp in m),
                    encoding='one elementary map per column (name=source->target), rows (X,Y,Z,coeff)')
    elif k == 'haiku55-b06':
        syms = {p['symbol'] for p in d['map']['parameters']}
        l = d['coboundary']['entries']
        for e in l:
            for ph, c in linear_terms(e['coeff'], syms).items():
                add(D, ph, (e['X'], e['Y'], e['Z']), c)
        info = dict(list_path='.coboundary.entries', entries=len(l),
                    encoding='row (X,Y,Z,coeff="linear expr in phi"), symbols in map.parameters')
    elif k == 'haiku55-b10':
        S = json.load(open(path(run, n, 'structure')))
        par = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
        m = d['maps']
        if len(m) != d['number_of_maps']:
            raise ValueError('number_of_maps %s vs %d maps' % (d['number_of_maps'], len(m)))
        for mp in m:
            if par[mp['i']] == par[mp['j']]:
                raise ValueError('map %s<-%s does not reverse parity' % (mp['i'], mp['j']))
            for e in mp['coboundary']:
                add(D, '%s<-%s' % (mp['i'], mp['j']), (e['X'], e['Y'], e['Z']), num(e['coeff']))
        info = dict(list_path='.maps[*].coboundary', entries=sum(len(mp['coboundary']) for mp in m),
                    encoding='one elementary map f(X_j)=X_i per column (label i<-j), rows (X,Y,Z,coeff)')
    elif k == 'haiku55-b08':
        m = d['coboundary_maps']
        for mp in m:
            for e in mp['coboundary_entries']:
                add(D, mp['phi'], (e['X'], e['Y'], e['Z']), num(e['coeff']))
        info = dict(list_path='.coboundary_maps[*].coboundary_entries',
                    entries=sum(len(mp['coboundary_entries']) for mp in m),
                    encoding='one elementary map per column (label phi), rows (X,Y,Z,coeff)')
    elif k == 'opus46-high-b02':
        l = d['coboundary_coefficients']
        for e in l:
            for t in e['result']:
                add(D, e['phi_parameter'], (e['X'], e['Y'], t['Z']), num(t['coeff']))
        info = dict(list_path='.coboundary_coefficients', entries=len(l),
                    encoding='row (X,Y,phi_parameter,result=[{Z,coeff}])')
    elif k == 'opus46-high-b04':
        l = d['coboundary_coefficients']
        for e in l:
            for t in e['result']:
                add(D, t['phi_param'], (e['X'], e['Y'], t['Z']), num(t['coeff']))
        info = dict(list_path='.coboundary_coefficients', entries=len(l),
                    encoding='row (X,Y,result=[{Z,phi_param,coeff}])')
    elif k == 'sonnet46-b12':
        l = d['coboundary']['coefficients']
        for e in l:
            for ph, c in linear_terms(e['coeff_expr']).items():
                if not re.fullmatch(r'phi_\{[^{}]*\}', ph):
                    raise ValueError('non-phi symbol %r in coboundary' % ph)
                add(D, ph, (e['X'], e['Y'], e['Z']), c)
        info = dict(list_path='.coboundary.coefficients', entries=len(l),
                    encoding='row (X,Y,Z,coeff_expr="linear expr in phi_{A,B}")')
    else:
        raise ValueError(k)
    return D, info


def _default_coboundary(run, n):
    # same as loader.load_coboundary default (copied to avoid recursion through the dispatcher)
    from loader import _parse_param_list, PHI_KEYS
    d = json.load(open(path(run, n, 'coboundary')))
    info = None
    for p, l in entry_lists(d):
        D, enc = _parse_param_list(l, PHI_KEYS, str)
        if D is not None:
            return D, dict(list_path=p, entries=len(l), encoding=enc)
        info = dict(list_path=p, entries=len(l), encoding='rows (X,Y,Z,coeff) without phi labels: keys=%s'
                    % sorted({k for e in l for k in e}))
    return None, info


def evaluated_info(run, n):
    f = path(run, n, 'evaluated_allpos' if _key(run) == 'haiku45-v293-b02' else 'evaluated')
    d = json.load(open(f))
    out = [dict(file=os.path.basename(f))]
    for p, l in entry_lists(d):
        out.append(dict(list_path=p, entries=len(l), keys=sorted({k for e in l for k in e})))
    return out
