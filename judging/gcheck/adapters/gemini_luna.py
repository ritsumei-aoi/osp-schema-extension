"""Adapter for thm01-R gemini31p-b{02,04,06,08,10}-G and luna-b{04,08,10}-G (judging/gcheck, 2026-10-07).

Only labels/encodings are translated; values are taken as recorded (no fixing).
Rows recorded in one ordering only are left as is (analyze.py fills by graded
antisymmetry). Rows with Z == 'K' are kept. Repeated (X,Y,Z,param) rows are summed
(loader.add), as the default loader does; the number of repeats is reported in info.

gb label rules
- 'gb_<sigma>_<j>_<s>' (gemini31p b02/b04/b06/b10): the Worker code builds it as
  f"gb_{sigma}_{j}_{s}" with sigma = sign of the fermion a_1^sigma, j = boson index,
  s = sign of the boson b_j^s (e.g. gemini31p-b02 src/C_gamma.py get_c,
  gemini31p-b06 src/C_gamma_generators.py: "b_j^s a_1^sigma = a_1^sigma b_j^s - gb*kappa").
  Mapped to the reference tuple (sign of a, boson index, sign of b) = (sigma, j, s).
- 'gb_a_1_<p|m>_b_<j>_<p|m>' (gemini31p-b08, luna): parsed by loader.gbparse.
phi labels: used verbatim as column keys (only the column set matters for ranks).

Per-run formats
- gemini31p-b02: gamma .gamma_structure = rows (X,Y) with gamma_expansion=[{Z,gb_param,coeff}];
  coboundary .coboundary_structure = rows (X,Y) with coboundary_expansion=[{Z,phi_param,coeff}];
  evaluated file is data/C_n_evaluated_all_ones.json (no C_n_evaluated.json).
- gemini31p-b04: gamma .inhomogeneous_deformation = rows (X,Y,Z,gamma_coeff) where gamma_coeff
  is a sympy expression string linear in gb symbols (e.g. "-gb_m_1_m"); coboundary
  .coboundary_deformation = rows (X,Y,Z,coboundary_coeff) linear in phi symbols.
  Expressions are parsed with sympy; non-linear or non-rational terms raise ValueError.
- gemini31p-b06: gamma .inhomogeneous_deformation.gamma_structure_constants = rows
  (X,Y,Z,gb_param,coeff); coboundary handled by the default loader (phi_param rows).
- gemini31p-b08: gamma .gamma_structure_constants rows (X,Y,Z,gb_terms={gb: coeff});
  coboundary .coboundary_structure_constants rows (X,Y,Z,f_terms={f: coeff}).
- gemini31p-b10: gamma file holds a single entry and the generating script
  (src/C_gamma_generators.py) writes it as a fixed literal ("representative gamma constants
  to satisfy the schema structure", "simplified placeholder for Z"); coboundary likewise
  a single literal entry (src/C_coboundary_generators.py). Not computed data -> load_gamma
  and load_coboundary return (None, info) with the reason.
- luna-b04: gamma .inhomogeneous_deformation.gamma_coefficients rows (X,Y,Z,gb_parameter,coeff);
  coboundary .coboundary.coefficients rows (X,Y,Z,phi_parameter,coeff).
- luna-b08: gamma .inhomogeneous_deformation.gamma_coefficients rows
  (X,Y,Z,coefficients=[{parameter,coeff}]); coboundary .coboundary_coefficients same encoding.
- luna-b10: gamma .inhomogeneous_deformation.gamma_coefficients rows (X,Y,Z,gb_parameter,coeff);
  coboundary .coboundary_coefficients rows (X,Y,Z,terms=[{phi_parameter,coeff}]).
Structure files are read by the default load_structure for all runs.
"""
import json, os, re
from fractions import Fraction as F
import sympy as sp
from loader import num, add, gbparse, path, FG_ROOT

RUNS = ['thm01-R-gemini31p-b02-G', 'thm01-R-gemini31p-b04-G', 'thm01-R-gemini31p-b06-G',
        'thm01-R-gemini31p-b08-G', 'thm01-R-gemini31p-b10-G',
        'thm01-R-luna-b04-G', 'thm01-R-luna-b08-G', 'thm01-R-luna-b10-G']

_FAM = {r: r.split('thm01-R-')[1].rsplit('-G', 1)[0] for r in RUNS}


def gb_label(s):
    """'gb_<sigma>_<j>_<s>' -> (sigma, j, s) as (sign a, boson idx, sign b); else loader.gbparse."""
    m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', s)
    if m:
        return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')
    return gbparse(s)


def _get(d, p):
    for k in p.split('.'):
        d = d[k]
    return d


def _linear(expr_str, prefix):
    """Parse a sympy expression linear in symbols starting with prefix -> {symbol_name: Fraction}."""
    e = sp.expand(sp.sympify(expr_str))
    if e == 0:
        return {}
    out = {}
    for term in sp.Add.make_args(e):
        c, rest = term.as_coeff_Mul()
        if not (isinstance(rest, sp.Symbol) and rest.name.startswith(prefix)) or not c.is_Rational:
            raise ValueError('non-linear or non-rational term %r in %r' % (term, expr_str))
        out[rest.name] = out.get(rest.name, F(0)) + F(int(c.p), int(c.q))
    return out


# (list path, row reader) per family; reader yields (X, Y, Z, param_label, coeff Fraction)
def _rows_flat(pkey):
    def rd(e):
        yield e['X'], e['Y'], e['Z'], e[pkey], num(e['coeff'])
    return rd


def _rows_nested(listkey, pkey):
    def rd(e):
        for t in e[listkey]:
            yield e['X'], e['Y'], t['Z'], t[pkey], num(t['coeff'])
    return rd


def _rows_terms(listkey, pkey):
    def rd(e):
        for t in e[listkey]:
            yield e['X'], e['Y'], e['Z'], t[pkey], num(t['coeff'])
    return rd


def _rows_dict(dkey):
    def rd(e):
        for p, c in e[dkey].items():
            yield e['X'], e['Y'], e['Z'], p, num(c)
    return rd


def _rows_expr(ckey, prefix):
    def rd(e):
        for p, c in _linear(e[ckey], prefix).items():
            yield e['X'], e['Y'], e['Z'], p, c
    return rd


_PLACEHOLDER = ('placeholder: generating script writes a single fixed literal entry '
                '("representative ... to satisfy the schema structure"); not computed data')

GAMMA = {
    'gemini31p-b02': ('gamma_structure', _rows_nested('gamma_expansion', 'gb_param'),
                      'one row per (X,Y) with gamma_expansion=[{Z,gb_param,coeff}]'),
    'gemini31p-b04': ('inhomogeneous_deformation', _rows_expr('gamma_coeff', 'gb_'),
                      'one row per (X,Y,Z) with gamma_coeff = sympy expression linear in gb symbols'),
    'gemini31p-b06': ('inhomogeneous_deformation.gamma_structure_constants', _rows_flat('gb_param'),
                      'one row per (X,Y,Z,gb_param,coeff), gb label gb_<sigma>_<j>_<s>'),
    'gemini31p-b08': ('gamma_structure_constants', _rows_dict('gb_terms'),
                      'one row per (X,Y,Z) with gb_terms={gb: coeff}'),
    'luna-b04': ('inhomogeneous_deformation.gamma_coefficients', _rows_flat('gb_parameter'),
                 'one row per (X,Y,Z,gb_parameter,coeff)'),
    'luna-b08': ('inhomogeneous_deformation.gamma_coefficients', _rows_terms('coefficients', 'parameter'),
                 'one row per (X,Y,Z) with coefficients=[{parameter,coeff}]'),
    'luna-b10': ('inhomogeneous_deformation.gamma_coefficients', _rows_flat('gb_parameter'),
                 'one row per (X,Y,Z,gb_parameter,coeff)'),
}

COB = {
    'gemini31p-b02': ('coboundary_structure', _rows_nested('coboundary_expansion', 'phi_param'),
                      'one row per (X,Y) with coboundary_expansion=[{Z,phi_param,coeff}]'),
    'gemini31p-b04': ('coboundary_deformation', _rows_expr('coboundary_coeff', 'phi_'),
                      'one row per (X,Y,Z) with coboundary_coeff = sympy expression linear in phi symbols'),
    'gemini31p-b06': ('coboundary_structure.coboundary_constants', _rows_flat('phi_param'),
                      'one row per (X,Y,Z,phi_param,coeff)'),
    'gemini31p-b08': ('coboundary_structure_constants', _rows_dict('f_terms'),
                      'one row per (X,Y,Z) with f_terms={f: coeff}'),
    'luna-b04': ('coboundary.coefficients', _rows_flat('phi_parameter'),
                 'one row per (X,Y,Z,phi_parameter,coeff)'),
    'luna-b08': ('coboundary_coefficients', _rows_terms('coefficients', 'parameter'),
                 'one row per (X,Y,Z) with coefficients=[{parameter,coeff}]'),
    'luna-b10': ('coboundary_coefficients', _rows_terms('terms', 'phi_parameter'),
                 'one row per (X,Y,Z) with terms=[{phi_parameter,coeff}]'),
}


def _load(run, n, kind, table, parse):
    fam = _FAM[run]
    if fam == 'gemini31p-b10':
        d = json.load(open(path(run, n, kind)))
        lp = 'inhomogeneous_deformation.gamma_constants' if kind == 'gamma' else 'coboundary_structure.coboundary_constants'
        return None, dict(list_path='.' + lp, entries=len(_get(d, lp)), encoding=_PLACEHOLDER)
    lp, rd, enc = table[fam]
    l = _get(json.load(open(path(run, n, kind))), lp)
    D, seen, rep = {}, set(), 0
    for e in l:
        for X, Y, Z, p, c in rd(e):
            k = (X, Y, Z, p)
            rep += k in seen
            seen.add(k)
            add(D, parse(p), (X, Y, Z), c)
    return D, dict(list_path='.' + lp, entries=len(l), encoding=enc, repeated_rows_summed=rep)


def load_gamma(run, n):
    return _load(run, n, 'gamma', GAMMA, gb_label)


def load_coboundary(run, n):
    return _load(run, n, 'coboundary', COB, str)


def evaluated_info(run, n):
    fn = path(run, n, 'evaluated')
    if _FAM[run] == 'gemini31p-b02':   # only C_n_evaluated_all_ones.json is committed
        fn = os.path.join(FG_ROOT, run, 'data', 'C_%d_evaluated_all_ones.json' % n)
    d = json.load(open(fn))
    out = []

    def walk(o, p=''):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + '.' + k)
        elif isinstance(o, list) and o and isinstance(o[0], dict) and 'X' in o[0] and 'Y' in o[0]:
            out.append(dict(file=os.path.basename(fn), list_path=p, entries=len(o),
                            keys=sorted({k for e in o for k in e})))
    walk(d)
    return out
