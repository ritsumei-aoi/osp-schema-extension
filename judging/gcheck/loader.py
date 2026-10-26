"""Loaders for the committed data/*.json of every run with generator realizations
(generalized from analysis_scripts/flash_gamma for judging/, 2026-10-07).
Run-specific formats are handled by adapters/<family>.py, which list their runs in RUNS
and may define load_structure / load_gamma / load_coboundary / evaluated_info
(same signatures and return values as the defaults below).

Copies of each Worker workspace (git archive HEAD) are expected under
$FG_ROOT/<run>/ (default: the scratchpad copy used on 2026-10-05).
"""
import json, os, re
from fractions import Fraction as F
import sympy as sp

FG_ROOT = os.environ['FG_ROOT']   # <root>/<run>/ = git archive copy (final or first)
_INV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inventory.csv')
import csv as _csv
_ROWS = list(_csv.DictReader(open(_INV)))
ALL_RUNS = [r['run'] for r in _ROWS if r.get('s1_realization') == '1']
VERSION = {r['run']: r['model'] + ' / ' + r['condition'] for r in _ROWS}

GB_KEYS = ('gb_param', 'param', 'gb', 'parameter', 'gb_label', 'gb_key')
PHI_KEYS = ('map_param', 'phi_param', 'phi_id', 'f_param', 'phi', 'phi_label')


def path(run, n, kind):
    return os.path.join(FG_ROOT, run, 'data', 'C_%d_%s.json' % (n, kind))


def num(x):
    if isinstance(x, (int,)):
        return F(x)
    s = str(x).strip()
    try:
        return F(s)
    except ValueError:
        v = sp.Rational(sp.nsimplify(sp.sympify(s)))
        return F(int(v.p), int(v.q))


def gbparse(s):
    m = re.fullmatch(r'gb_?a_?1_?([pm])_?b_?(\d+)_?([pm])', s)
    if not m:
        m2 = re.fullmatch(r'gb_([pm])([pm])_(\d+)', s)   # gb_{sigma s}_j (sonnet46-A)
        if m2:
            return ('+' if m2[1] == 'p' else '-', int(m2[3]), '+' if m2[2] == 'p' else '-')
        raise KeyError(s)
    return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')


def entry_lists(o, p=''):
    """all lists of dicts whose first element has X and Y, with their JSON path"""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from entry_lists(v, p + '.' + k)
    elif isinstance(o, list) and o and isinstance(o[0], dict) and 'X' in o[0] and 'Y' in o[0]:
        yield p, o


def add(D, col, key, c):
    if c == 0:
        return
    d = D.setdefault(col, {})
    d[key] = d.get(key, 0) + c
    if d[key] == 0:
        del d[key]


def _parse_param_list(l, keys, parse):
    """Return ({col: {(X,Y,Z): F}}, encoding description) or (None, None) if no param data."""
    D, enc = {}, None
    for e in l:
        X, Y = e['X'], e['Y']
        k = next((k for k in keys if k in e), None)
        if k is not None and 'Z' in e:
            enc = 'one row per (X,Y,Z,%s,coeff)' % k
            add(D, parse(e[k]), (X, Y, e['Z']), num(e['coeff']))
        elif 'linear_combination' in e:
            enc = 'one row per (X,Y,Z) with linear_combination=[{param,coeff}]'
            for t in e['linear_combination']:
                add(D, parse(t['param']), (X, Y, e['Z']), num(t['coeff']))
        elif 'symbolic_phi_terms' in e:
            enc = 'one row per (X,Y,Z) with symbolic_phi_terms={phi: coeff} (+ evaluated_coeff)'
            for ph, c in e['symbolic_phi_terms'].items():
                add(D, parse(ph), (X, Y, e['Z']), num(c))
        elif 'gamma_value' in e or 'delta_f_value' in e:
            fld = 'gamma_value' if 'gamma_value' in e else 'delta_f_value'
            enc = 'one row per (X,Y) with %s={param: [{Z,coeff}]}' % fld
            for ph, terms in e[fld].items():
                for t in terms:
                    add(D, parse(ph), (X, Y, t['Z']), num(t['coeff']))
        else:
            return None, None
    return D, enc


import importlib, glob as _glob
_ADAPTERS = {}
for _f in sorted(_glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adapters', '*.py'))):
    _m = os.path.basename(_f)[:-3]
    if _m.startswith('_'):
        continue
    _mod = importlib.import_module('adapters.' + _m)
    for _r in getattr(_mod, 'RUNS', []):
        _ADAPTERS[_r] = _mod
        if _r not in ALL_RUNS:   # e.g. thm01-01: realization recorded outside Schema 1
            ALL_RUNS.append(_r)


def _override(name):
    """Return the adapter's function `name` for a run, if its adapter defines one."""
    def deco(default):
        def f(run, n, *a):
            mod = _ADAPTERS.get(run)
            if mod is not None and hasattr(mod, name):
                return getattr(mod, name)(run, n, *a)
            return default(run, n, *a)
        f.__name__ = default.__name__
        return f
    return deco


@_override('load_gamma')
def load_gamma(run, n):
    d = json.load(open(path(run, n, 'gamma')))
    for p, l in entry_lists(d):
        D, enc = _parse_param_list(l, GB_KEYS, gbparse)
        if D is not None:
            return D, dict(list_path=p, entries=len(l), encoding=enc)
    return None, None


@_override('load_coboundary')
def load_coboundary(run, n):
    """Coboundary matrix A as {phi_label: {(X,Y,Z): F}}; None if the file records no phi structure."""
    d = json.load(open(path(run, n, 'coboundary')))
    info = None
    for p, l in entry_lists(d):
        D, enc = _parse_param_list(l, PHI_KEYS, str)
        if D is not None:
            return D, dict(list_path=p, entries=len(l), encoding=enc)
        info = dict(list_path=p, entries=len(l), encoding='rows (X,Y,Z,coeff) without phi labels: keys=%s'
                    % sorted({k for e in l for k in e}))
    return None, info


@_override('evaluated_info')
def evaluated_info(run, n):
    d = json.load(open(path(run, n, 'evaluated')))
    out = []
    for p, l in entry_lists(d):
        out.append(dict(list_path=p, entries=len(l), keys=sorted({k for e in l for k in e})))
    return out


@_override('load_structure')
def load_structure(run, n):
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
