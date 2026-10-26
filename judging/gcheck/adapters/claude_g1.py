"""Adapter for Claude Code batch runs, condition G (claude_g1, 2026-10-07).

Only translates encodings / labels of the Worker JSON; no Worker values are changed.
Runs whose committed data contain no usable gamma (or coboundary) data return
(None, info) with info['reason'] stating the recorded fact; runs whose structure file
cannot be read raise ValueError with the fact.

gb label rules (each maps to the reference triple (sign of a_1, boson index j, sign of b_j)):
- 'gb_a1p_b1p', 'gb_a_1_p_b_1_p', 'gb_a1_p_b1_p' ...  -> loader.gbparse (a-sign, j, b-sign)
- 'gb_p_1_m' (sonnet46-b02, opus46-b10, opus48-b02): the Workers state
  'gb_{sigma}_{j}_{s}: sigma in {p,m}, j=1..n, s in {p,m}' (sonnet46-b02 gamma file),
  opus46-b10 lists label gb_p_1_m with fermionic a_1_p, bosonic b_1_m, opus48-b02 states
  rows = fermion sign sigma, cols = (j, s). Rule: gb_{x}_{j}_{y} -> (x, j, y).
- 'gb_a1P_b1M' (opus5-b02): Worker naming 'gb_a1{P|M}_b{k}{P|M}: fermionic sign, bosonic
  index, bosonic sign'. Rule: upper-case P/M -> p/m, then loader.gbparse.
- 'gb_1_pm' (haiku45-b06 gamma_terms): built by the Worker's src/C_gamma_generator.py as
  f"gb_{k}_{suffix}" where k and suffix are copied from the odd generator name
  E_eps1_del{k}_{suffix}; that generator's realization is a_1^{suffix[0]} b_k^{suffix[1]}
  (checked in C_n_structure.json). Rule: gb_{k}_{xy} -> (x, k, y). The parameter list of
  the same file uses gb_a1_{x}_b{k}_{y}, i.e. the same index order.
phi labels are kept as opaque strings (only the set of columns matters);
opus46-b10 rows (phi_source, phi_target) are joined as 'phi_<source>__<target>'.
Coefficients given as sympy strings (opus47-b02, opus48-b02, opus5-b02, haiku45-b06) are
parsed as linear forms in the label symbols; a non-linear or constant term raises ValueError.
"""
import json, os, re
from fractions import Fraction as F
import sympy as sp
from loader import num, add, gbparse, path, FG_ROOT

RUNS = ['thm01-R-haiku45-b02-G', 'thm01-R-haiku45-b04-G', 'thm01-R-haiku45-b06-G',
        'thm01-R-haiku45-b08-G', 'thm01-R-haiku45-b10-G', 'thm01-R-sonnet46-b01-G',
        'thm01-R-sonnet46-b02-G', 'thm01-R-sonnet46-b04-G', 'thm01-R-sonnet46-b07-G',
        'thm01-R-sonnet46-b11-G', 'thm01-R-opus46-b08-G', 'thm01-R-opus46-b10-G',
        'thm01-R-opus47-b02-G', 'thm01-R-opus48-b02-G', 'thm01-R-opus5-b02-G']


# ---------- label parsers ----------
def gb_spj(s):
    m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', s)
    if not m:
        return gbparse(s)
    return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')


def gb_upper(s):
    m = re.fullmatch(r'gb_a1([PM])_b(\d+)([PM])', s)
    if not m:
        raise KeyError(s)
    return gbparse('gb_a1%s_b%s%s' % (m[1].lower(), m[2], m[3].lower()))


def gb_kxy(s):
    m = re.fullmatch(r'gb_(\d+)_([pm])([pm])', s)
    if not m:
        raise KeyError(s)
    return ('+' if m[2] == 'p' else '-', int(m[1]), '+' if m[3] == 'p' else '-')


# ---------- expression parser ----------
def linear_terms(expr):
    """'2*gb_x - gb_y/2' -> {'gb_x': F(2), 'gb_y': F(-1,2)}; raises on non-linear/constant."""
    names = sorted(set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', str(expr))))
    loc = {nm: sp.Symbol(nm) for nm in names}
    e = sp.expand(sp.sympify(str(expr), locals=loc))
    out = {}
    rest = e
    for nm, sym in loc.items():
        c = sp.diff(e, sym)
        if c.free_symbols:
            raise ValueError('non-linear term in %r' % expr)
        if c != 0:
            c = sp.Rational(c)
            out[nm] = F(int(c.p), int(c.q))
            rest = rest - c * sym
    if sp.simplify(rest) != 0:
        raise ValueError('constant term %s in %r' % (rest, expr))
    return out


def _get(d, dotted):
    for k in dotted.split('.'):
        d = d[k]
    return d


def _file(run, n, kind):
    """Actual file names where they differ from data/C_n_<kind>.json."""
    alt = {
        ('thm01-R-haiku45-b02-G', 'coboundary'): 'coboundary_trivial',
        ('thm01-R-haiku45-b02-G', 'evaluated'): 'evaluated_trivial',
        ('thm01-R-haiku45-b08-G', 'coboundary'): 'coboundary_gb1',
        ('thm01-R-haiku45-b08-G', 'evaluated'): 'evaluated_gb1',
        ('thm01-R-opus46-b10-G', 'evaluated'): 'evaluated_all_plus',
    }.get((run, kind), kind)
    return path(run, n, alt)


# ---------- row encodings ----------
def parse_rows(l, form, parse, zkey='Z', **kw):
    """Return {col: {(X,Y,Z): F}} for the row encodings found in these runs."""
    D = {}
    for e in l:
        X, Y = e['X'], e['Y']
        if form == 'dict':          # (X,Y,Z, field={label: coeff})
            for lab, c in e[kw['field']].items():
                add(D, parse(lab), (X, Y, e[zkey]), num(c))
        elif form == 'nested':      # (X,Y, field={label: {Z: coeff}})
            for lab, zs in e[kw['field']].items():
                for Z, c in zs.items():
                    add(D, parse(lab), (X, Y, Z), num(c))
        elif form == 'single':      # (X,Y,Z, labelkey, coeffkey)
            add(D, parse(e[kw['label']]), (X, Y, e[zkey]), num(e[kw['coeff']]))
        elif form == 'expr':        # (X,Y,Z, coeff = linear sympy string in labels)
            for lab, c in linear_terms(e[kw['coeff']]).items():
                add(D, parse(lab), (X, Y, e[zkey]), c)
        elif form == 'phi_st':      # (X,Y,Z, phi_source, phi_target, coeff)
            add(D, 'phi_%s__%s' % (e['phi_source'], e['phi_target']), (X, Y, e[zkey]), num(e['coeff']))
        else:
            raise ValueError(form)
    return D


GAMMA = {
    # run: (list path, form, gb parser, kwargs)
    'thm01-R-sonnet46-b01-G': ('gamma_structure', 'dict', gbparse, dict(field='coeff_expr')),
    'thm01-R-sonnet46-b02-G': ('gamma_coefficients', 'dict', gb_spj, dict(field='gb_coeffs')),
    'thm01-R-sonnet46-b04-G': ('gamma_coefficients', 'single', gbparse, dict(label='gb_param', coeff='numeric_coeff')),
    'thm01-R-sonnet46-b07-G': ('inhomogeneous_deformation.gamma_coefficients', 'dict', gbparse, dict(field='gamma_expr')),
    'thm01-R-sonnet46-b11-G': ('inhomogeneous_deformation.gamma_coefficients', 'nested', gbparse, dict(field='gamma_coeffs')),
    'thm01-R-opus46-b08-G': ('gamma_coefficients', 'single', gbparse, dict(label='gb_param', coeff='coeff', zkey='gamma_Z')),
    'thm01-R-opus46-b10-G': ('gamma_coefficients', 'single', gb_spj, dict(label='gb_param', coeff='coeff')),
    'thm01-R-opus47-b02-G': ('gamma_coefficients', 'expr', gbparse, dict(coeff='coeff')),
    'thm01-R-opus48-b02-G': ('gamma', 'expr', gb_spj, dict(coeff='coeff')),
    'thm01-R-opus5-b02-G': ('inhomogeneous_deformation.entries', 'expr', gb_upper, dict(coeff='coeff')),
    'thm01-R-haiku45-b06-G': ('inhomogeneous_deformation.gamma_terms', 'expr', gb_kxy, dict(coeff='gamma_coeff')),
}

GAMMA_ABSENT = {
    'thm01-R-haiku45-b02-G': "gamma file has inhomogeneous_deformation.gamma_cocycle.status='to be computed'; "
                             "no (X,Y,Z) gamma rows recorded",
    'thm01-R-haiku45-b04-G': "gamma_coefficients.data rows are (X,Y,gamma_symbolic=<gb label or '{gb,gb}'>, "
                             "involves_kappa) with no Z and no coefficient (n=1: 4 rows, n=2: 12 rows)",
    'thm01-R-haiku45-b08-G': "deformation_structure.gamma_structure records only oscillator-level brackets "
                             "(generators=[b_j_s,a_1_sigma], coefficient='-gb_...', result_element='kappa'); "
                             "no (X,Y,Z) rows over the generator basis",
    'thm01-R-haiku45-b10-G': "gamma_structure.gamma_coefficients has only rows with Z='K' and coeff a product of "
                             "two gb symbols (e.g. 'gb_a1_p_b1_p * gb_a1_m_b1_m'; n=1: 1 row, n=2: 4 rows); "
                             "not linear in gb, so no per-parameter gamma columns exist",
}

COB = {
    'thm01-R-sonnet46-b01-G': ('coboundary', 'dict', str, dict(field='phi_coefficients')),
    'thm01-R-sonnet46-b02-G': ('delta_f_coefficients', 'dict', str, dict(field='phi_coeffs')),
    'thm01-R-sonnet46-b04-G': ('coboundary_coefficients', 'single', str, dict(label='phi_param', coeff='coeff')),
    'thm01-R-sonnet46-b11-G': ('coboundary.coboundary_coefficients', 'dict', str, dict(field='phi_coeffs')),
    'thm01-R-opus46-b08-G': ('coboundary_coefficients', 'single', str, dict(label='phi_param', coeff='coeff', zkey='delta_f_Z')),
    'thm01-R-opus46-b10-G': ('coboundary_coefficients', 'phi_st', str, dict()),
    'thm01-R-opus47-b02-G': ('delta_f_coefficients', 'expr', str, dict(coeff='coeff')),
    'thm01-R-opus48-b02-G': ('delta_f', 'expr', str, dict(coeff='coeff')),
}

COB_ABSENT = {
    'thm01-R-haiku45-b02-G': "coboundary_trivial file: coboundary_coefficients.status='to be computed'; no rows",
    'thm01-R-haiku45-b04-G': "coboundary_coefficients.data: rows (X,Y,result,coeff) for one fixed f "
                             "(coboundary_map.parameters with numeric coefficients); no phi labels",
    'thm01-R-haiku45-b06-G': "coboundary_operator.coboundary_terms is an empty list (linear_map_f: 'f = 0 (prototype)')",
    'thm01-R-haiku45-b08-G': "coboundary_gb1 file: coboundary_operator.entries rows (X,Y,f_map_X,f_map_Y,formula,"
                             "sign_X,sign_Y) for one fixed f; no delta-f values, no phi labels",
    'thm01-R-haiku45-b10-G': "coboundary_structure.coboundary_operator.coefficients rows (X,Y,p(X),p(Y),"
                             "computation_framework,f_X_present,f_Y_present) for one fixed f; no values, no phi labels",
    'thm01-R-sonnet46-b07-G': "coboundary_delta_f rows (X,Y,Z,coeff_expr={gb: c}) are delta f for one f family "
                              "f(H_1)=sum gb*E_eps (odd_map_f); columns are gb labels, not phi labels",
    'thm01-R-opus5-b02-G': "coboundary.entries rows (X,Y,Z,coeff=linear form in gb) are delta f for one f "
                           "(f_map.phi given in terms of gb, with K targets); no phi labels",
}


def load_structure(run, n):
    if run == 'thm01-R-haiku45-b02-G':
        S = json.load(open(path(run, n, 'structure')))
        R = S['generator_realization']['realizations']
        bad = sorted({w for g in R for t in R[g]['standard_form'] for w in t['words'] if '{' in w})
        if bad:
            raise ValueError('generator_realization contains unformatted placeholder words %s '
                             '(structure_constants: %d entries; gamma not computed: %s)'
                             % (bad, len(S.get('structure_constants', [])), GAMMA_ABSENT[run]))
    S = json.load(open(path(run, n, 'structure')))
    GR = S['generator_realization']
    R = GR.get('realizations', GR)
    noreal = [g for g in list(S['basis']['even']) + list(S['basis']['odd']) if g not in R]
    if noreal:
        raise ValueError('basis generators without a generator_realization entry: %s (%d of %d basis '
                         'elements realized)' % (noreal, len(R), len(S['basis']['even']) + len(S['basis']['odd'])))
    basis, parity, real, sc = _default_structure(run, n)
    if run == 'thm01-R-sonnet46-b01-G':
        # Worker oscillator labels are 'a1p','b2m' (oscillator_generators.labels; description
        # 'a_1^+, a_1^-', 'b_k^+/-'). Rule: <a|b><k><p|m> -> <a|b>_<k>_<p|m> (refmodel.osc format).
        def w(x):
            m = re.fullmatch(r'([ab])(\d+)([pm])', x)
            if not m:
                raise KeyError(x)
            return '%s_%s_%s' % (m[1], m[2], m[3])
        real = {g: [(c, [w(x) for x in ws]) for c, ws in terms] for g, terms in real.items()}
    return basis, parity, real, sc


def _default_structure(run, n):
    # same as loader.load_structure default (copied to avoid recursion through the dispatcher)
    S = json.load(open(path(run, n, 'structure')))
    B = S['basis']
    basis = list(B['even']) + list(B['odd'])
    parity = {x: 0 for x in B['even']} | {x: 1 for x in B['odd']}
    GR = S['generator_realization']
    R = GR.get('realizations', GR)
    real = {g: [(num(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    sc = {}
    for e in S.get('structure_constants', []):
        sc.setdefault((e['X'], e['Y']), {})[e['Z']] = num(e['coeff'])
    return basis, parity, real, sc


def load_gamma(run, n):
    if run in GAMMA_ABSENT:
        return None, dict(file=os.path.basename(path(run, n, 'gamma')), reason=GAMMA_ABSENT[run])
    lp, form, parse, kw = GAMMA[run]
    l = _get(json.load(open(path(run, n, 'gamma'))), lp)
    D = parse_rows(l, form, parse, **kw)
    info = dict(list_path=lp, entries=len(l), encoding=form + ' ' + json.dumps({k: v for k, v in kw.items()}))
    if run == 'thm01-R-sonnet46-b04-G':
        # cross-check the recorded coeff_expr against (gb_param, numeric_coeff)
        info['coeff_expr_mismatches'] = sum(
            1 for e in l if linear_terms(e['coeff_expr']) != {e['gb_param']: num(e['numeric_coeff'])})
    if run == 'thm01-R-opus48-b02-G':
        info['carriers'] = sorted({e.get('carrier') for e in l})
    return D, info


def load_coboundary(run, n):
    if run in COB_ABSENT:
        return None, dict(file=os.path.basename(_file(run, n, 'coboundary')), reason=COB_ABSENT[run])
    lp, form, parse, kw = COB[run]
    l = _get(json.load(open(path(run, n, 'coboundary'))), lp)
    D = parse_rows(l, form, parse, **kw)
    return D, dict(list_path=lp, entries=len(l), encoding=form + ' ' + json.dumps(kw))


def evaluated_info(run, n):
    from loader import entry_lists
    f = _file(run, n, 'evaluated')
    d = json.load(open(f))
    out = [dict(file=os.path.basename(f))]
    for p, l in entry_lists(d):
        out.append(dict(list_path=p, entries=len(l), keys=sorted({k for e in l for k in e})))
    return out
