"""Adapter for thm01-R gemini31p-b{12,22,24}-G, gemini31p-high-b02-G and luna-b{14,18,20}-G
(judging/gcheck, 2026-10-11).

Only labels/encodings are translated; values are taken as recorded (no fixing).
Rows recorded in one ordering only are left as is (analyze.py fills by graded antisymmetry).
Rows with Z == 'K' are kept. Repeated (X,Y,Z,param) rows are summed (loader.add), as the
default loader does; the number of repeats is reported in info. Every X, Y, Z must be a basis
label of the run's own C_n_structure.json (Z may also be 'K'), else ValueError.
Float coefficients (gemini31p-high-b02 stores JSON floats) are accepted only when the float is
exactly the decimal it prints as (e.g. 2.0, -0.5); otherwise ValueError (no rounding to rationals).

Reference gb tuple = (sign of fermion a_1, boson index j, sign of boson b_j), the reference's
gb_{sigma,j,s} in "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa" (definition doc
C_inhomogeneous_definition.md, copied in every run's docs/math/).

gb label rules (each derived from the run's own files; cross-checks raise on mismatch)
- gemini31p-b12: 'gb_a<sigma>_b<j><s>' (e.g. gb_ap_b1p). src/C_gamma.py commute(op1, op2) with
  op1 = 'b<j><s>', op2 = 'a<sigma>' ("b a = a b - gb kappa") returns f"gb_{op2}_{op1}".
  -> (sigma, j, s). Check: that source line is present; the label set of each n is exactly the
  4n labels {a p/m} x {b 1..n} x {p/m}.
- gemini31p-b22: 'gb_a1_<sigma>_b<j>_<s>' (oscillator labels a1_<sigma>, b<j>_<s> of its
  structure file). src/gamma_generators.py: left = b, right = a, "[b, a] = - gb * kappa",
  gb_name = f"gb_{right}_{left}". -> (sigma, j, s). Check: source line present; label set ==
  inhomogeneous_deformation.gb_matrix.parameters.
- gemini31p-b24: 'gb_<sigma>_<j>_<s>'. src/C_gamma.py eta(): sigma = sign of the a oscillator,
  j = boson index, s = sign of the boson, res[f"gb_{sigma}_{j}_{s}"]. -> (sigma, j, s).
  Check: source line present; label set == inhomogeneous_deformation.gb_labels.
- gemini31p-high-b02: 'gb_<sigma>_<j>_<s>'. src/C_gamma_generators.py sort_ops ("bj a = a bj -
  gb_{a, b} kappa"): sigma = 'p' if the a token is 'a+', j = boson index, s = sign of the b token,
  gb_name = f'gb_{sigma}_{j}_{s}'. -> (sigma, j, s). Check: source line present; every label
  parses; the row label sigma agrees with gb_matrix rows (row 0 = gb_p_*, row 1 = gb_m_*).
- luna-b14: label -> (fermion, boson) from inhomogeneous_deformation.gb_matrix.parameters
  [{label, fermion 'a_1_<sigma>', boson 'b_<j>_<s>'}] -> (sigma, j, s). Check: the label text
  'gb_a1_<sigma>_b<j>_<s>' agrees with the recorded fermion/boson.
- luna-b18: label -> (rows[i], columns[k]) from inhomogeneous_deformation.gb_matrix
  {rows: a_1_<sigma>, columns: b_<j>_<s>, values[i][k]: label}. Same check on the label text.
- luna-b20: label -> (rows[i], columns[k]) from top-level gb_matrix {rows, columns, entries}.
  Same check on the label text.
phi labels: used verbatim as column keys (only the column set matters for ranks);
gemini31p-b24 has no phi label, its column key is the recorded pair (f_in, f_out).

Per-run formats
- gemini31p-b12: gamma .inhomogeneous_deformation.gamma_constants rows (X,Y,Z,gamma_terms=[{gb,coeff}]);
  coboundary .coboundary_structure.constants rows (X,Y,Z,coboundary_terms=[{phi,coeff}]).
- gemini31p-b22: structure realizations use oscillator words 'a1_<p|m>', 'b<j>_<p|m>' (its own
  oscillator_generators labels and generator_realization.ordering); translated to 'a_1_<p|m>',
  'b_<j>_<p|m>' (check: every word is one of the file's oscillator labels; a-index is 1).
  gamma .inhomogeneous_deformation.gamma_structure rows (X,Y,Z,gb_param,coeff);
  coboundary .coboundary_evaluated rows (X,Y,Z,phi_param,coeff) (labels listed in .f_parameters;
  check: every used label is in that list).
- gemini31p-b24: gamma .gamma_structure rows (X,Y,Z,gb,coeff); coboundary .coboundary_structure
  rows (X,Y,Z,f_in,f_out,coeff); evaluated file is data/C_n_evaluated_all_ones.json.
- gemini31p-high-b02: structure: basis lists as usual; generator_realization {g: string} written by
  src/C_generators.py format_realization: terms joined by " + " then "+ -" -> "- "; a term is
  "c" (constant), "c ops", "- ops" (c = -1) or "ops" (c = 1); ops tokens 'a+', 'a-', 'b<j>+',
  'b<j>-' (src p(): 'a+'/'a-' are the fermion). Parsed as: whitespace tokens; '+'/'-' tokens
  are signs that start a term; an optional number; then operator tokens. Words translated
  'a+' -> a_1_p, 'a-' -> a_1_m, 'b<j>+' -> b_<j>_p, 'b<j>-' -> b_<j>_m (check: each translated word
  is in oscillator_generators labels; any other token raises). structure_constants
  {"X,Y": {Z: coeff}} (src: key = f"{x},{y}"; check: two basis labels).
  gamma .inhomogeneous_deformation.gamma_structure_constants {"X,Y": {Z: {gb: coeff}}};
  coboundary .coboundary_structure.delta_f_constants {"X,Y": {Z: {phi: coeff}}};
  evaluated .evaluated_deformation.evaluated_gamma_structure_constants {"X,Y": {Z: coeff}}.
- luna-b14: gamma .inhomogeneous_deformation.gamma_coefficients rows
  (X,Y,Z,coefficients=[{parameter,coeff}]); coboundary .coboundary.coboundary_coefficients same.
- luna-b18: gamma .inhomogeneous_deformation.gamma_coefficients rows (X,Y,Z,coeff) where coeff is a
  sympy expression linear in gb symbols (e.g. "-gb_a1_m_b1_m/2"); non-linear/non-rational raises.
  coboundary: .coboundary.coboundary_coefficients is delta_f of ONE fixed odd map (.coboundary.odd_map,
  2 terms), no phi parameters -> load_coboundary returns (None, info) (as the default loader does
  for rows without phi labels).
- luna-b20: gamma .inhomogeneous_deformation.gamma_coefficients rows (X,Y,Z,terms=[{parameter,coeff}]);
  coboundary .coboundary.coefficients same encoding.
Structure files of gemini31p-b12, gemini31p-b24 and luna-* are read by the default load_structure.

Left out: gemini31p-b18-G. Its final C_n_structure.json (n=1,2,3) has generator_realization = {}
and structure_constants = [], and C_n_gamma / C_n_coboundary have empty lists: no realization
or gamma data to compare (the default loader fails with KeyError 'H_1').
"""
import json, os, re
from fractions import Fraction as F
import sympy as sp
from loader import num, add, path, FG_ROOT

RUNS = ['thm01-R-gemini31p-b12-G', 'thm01-R-gemini31p-b22-G', 'thm01-R-gemini31p-b24-G',
        'thm01-R-gemini31p-high-b02-G',
        'thm01-R-luna-b14-G', 'thm01-R-luna-b18-G', 'thm01-R-luna-b20-G']

_FAM = {r: r.split('thm01-R-')[1].rsplit('-G', 1)[0] for r in RUNS}
_PM = {'p': '+', 'm': '-'}


def _get(d, p):
    for k in p.split('.'):
        d = d[k]
    return d


def _src(run, rel):
    return open(os.path.join(FG_ROOT, run, rel)).read()


def _require_src(run, rel, text):
    if text not in _src(run, rel):
        raise ValueError('%s: expected gb construction %r not found in %s' % (run, text, rel))


def _exact(x):
    """Coefficient -> Fraction. JSON floats must equal the decimal they print as."""
    if isinstance(x, float):
        if F(x) != F(repr(x)):
            raise ValueError('float %r is not exactly its decimal' % x)
        return F(repr(x))
    return num(x)


def _n_of(run, n):
    return json.load(open(path(run, n, 'structure')))['algebra']['n']


def _full_set(n):
    return {(a, j, b) for a in '+-' for j in range(1, n + 1) for b in '+-'}


# ---------- gb label maps: return {label: (sigma, j, s)} for the run and n ----------

def _ferm_bos(label, fermion, boson):
    mf = re.fullmatch(r'a_1_([pm])', fermion)
    mb = re.fullmatch(r'b_(\d+)_([pm])', boson)
    if not (mf and mb):
        raise ValueError('unexpected fermion/boson %r %r for %r' % (fermion, boson, label))
    t = (_PM[mf[1]], int(mb[1]), _PM[mb[2]])
    expect = 'gb_a1_%s_b%s_%s' % (mf[1], mb[1], mb[2])
    if label != expect:
        raise ValueError('label %r disagrees with its recorded (fermion, boson) %r %r' % (label, fermion, boson))
    return t


def _gbmap(run, n):
    fam = _FAM[run]
    G = json.load(open(path(run, n, 'gamma')))
    nn = _n_of(run, n)
    M = {}
    if fam == 'gemini31p-b12':
        _require_src(run, 'src/C_gamma.py', 'return -1, f"gb_{op2}_{op1}"')
        for a in 'pm':
            for j in range(1, nn + 1):
                for b in 'pm':
                    M['gb_a%s_b%d%s' % (a, j, b)] = (_PM[a], j, _PM[b])
    elif fam == 'gemini31p-b22':
        _require_src(run, 'src/gamma_generators.py', 'gb_name = f"gb_{right}_{left}"')
        for lab in G['inhomogeneous_deformation']['gb_matrix']['parameters']:
            m = re.fullmatch(r'gb_a1_([pm])_b(\d+)_([pm])', lab)
            if not m:
                raise ValueError('unexpected gb label %r' % lab)
            M[lab] = (_PM[m[1]], int(m[2]), _PM[m[3]])
    elif fam in ('gemini31p-b24', 'gemini31p-high-b02'):
        if fam == 'gemini31p-b24':
            _require_src(run, 'src/C_gamma.py', 'res[f"gb_{sigma}_{j}_{s}"] = 1')
            labels = G['inhomogeneous_deformation']['gb_labels']
        else:
            _require_src(run, 'src/C_gamma_generators.py', "gb_name = f'gb_{sigma}_{j}_{s}'")
            rows = G['inhomogeneous_deformation']['gb_matrix']
            for sg, row in zip('pm', rows):
                for lab in row:
                    if lab != '...' and not lab.startswith('gb_%s_' % sg):
                        raise ValueError('gb_matrix row %s holds %r' % (sg, lab))
            labels = ['gb_%s_%d_%s' % (a, j, b) for a in 'pm' for j in range(1, nn + 1) for b in 'pm']
        for lab in labels:
            m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', lab)
            if not m:
                raise ValueError('unexpected gb label %r' % lab)
            M[lab] = (_PM[m[1]], int(m[2]), _PM[m[3]])
    elif fam == 'luna-b14':
        for e in G['inhomogeneous_deformation']['gb_matrix']['parameters']:
            M[e['label']] = _ferm_bos(e['label'], e['fermion'], e['boson'])
    elif fam in ('luna-b18', 'luna-b20'):
        gm = G['inhomogeneous_deformation']['gb_matrix'] if fam == 'luna-b18' else G['gb_matrix']
        vals = gm['values'] if fam == 'luna-b18' else gm['entries']
        for f, row in zip(gm['rows'], vals):
            if len(row) != len(gm['columns']):
                raise ValueError('gb_matrix row length mismatch')
            for b, lab in zip(gm['columns'], row):
                M[lab] = _ferm_bos(lab, f, b)
    else:
        raise KeyError(run)
    if set(M.values()) != _full_set(nn) or len(M) != 4 * nn:
        raise ValueError('%s n=%d: gb labels do not cover the 4n parameters exactly: %s' % (run, n, sorted(M)))
    return M


# ---------- row readers: yield (X, Y, Z, label, Fraction) ----------

def _rows_terms(listkey, pkey, ckey='coeff'):
    def rd(e):
        for t in e[listkey]:
            yield e['X'], e['Y'], e['Z'], t[pkey], _exact(t[ckey])
    return rd


def _rows_flat(pkey):
    def rd(e):
        yield e['X'], e['Y'], e['Z'], e[pkey], _exact(e['coeff'])
    return rd


def _rows_b24cob(e):
    yield e['X'], e['Y'], e['Z'], (e['f_in'], e['f_out']), _exact(e['coeff'])


def _linear(expr_str, prefix):
    e = sp.expand(sp.sympify(expr_str))
    out = {}
    if e == 0:
        return out
    for term in sp.Add.make_args(e):
        c, rest = term.as_coeff_Mul()
        if not (isinstance(rest, sp.Symbol) and rest.name.startswith(prefix)) or not c.is_Rational:
            raise ValueError('non-linear or non-rational term %r in %r' % (term, expr_str))
        out[rest.name] = out.get(rest.name, F(0)) + F(int(c.p), int(c.q))
    return out


def _rows_expr(e):
    for p, c in _linear(e['coeff'], 'gb_').items():
        yield e['X'], e['Y'], e['Z'], p, c


def _nested_rows(d):
    """{"X,Y": {Z: {label: coeff}}} -> rows"""
    for xy, zs in d.items():
        X, Y = xy.split(',')
        for Z, terms in zs.items():
            for p, c in terms.items():
                yield X, Y, Z, p, _exact(c)


GAMMA = {
    'gemini31p-b12': ('inhomogeneous_deformation.gamma_constants', _rows_terms('gamma_terms', 'gb'),
                      'one row per (X,Y,Z) with gamma_terms=[{gb,coeff}], gb label gb_a<sigma>_b<j><s>'),
    'gemini31p-b22': ('inhomogeneous_deformation.gamma_structure', _rows_flat('gb_param'),
                      'one row per (X,Y,Z,gb_param,coeff), gb label gb_a1_<sigma>_b<j>_<s>'),
    'gemini31p-b24': ('gamma_structure', _rows_flat('gb'),
                      'one row per (X,Y,Z,gb,coeff), gb label gb_<sigma>_<j>_<s>'),
    'gemini31p-high-b02': ('inhomogeneous_deformation.gamma_structure_constants', None,
                           'nested {"X,Y": {Z: {gb: coeff}}}, gb label gb_<sigma>_<j>_<s>, float coeffs'),
    'luna-b14': ('inhomogeneous_deformation.gamma_coefficients', _rows_terms('coefficients', 'parameter'),
                 'one row per (X,Y,Z) with coefficients=[{parameter,coeff}], labels from gb_matrix.parameters'),
    'luna-b18': ('inhomogeneous_deformation.gamma_coefficients', _rows_expr,
                 'one row per (X,Y,Z) with coeff = sympy expression linear in gb symbols, labels from gb_matrix'),
    'luna-b20': ('inhomogeneous_deformation.gamma_coefficients', _rows_terms('terms', 'parameter'),
                 'one row per (X,Y,Z) with terms=[{parameter,coeff}], labels from gb_matrix'),
}

COB = {
    'gemini31p-b12': ('coboundary_structure.constants', _rows_terms('coboundary_terms', 'phi'),
                      'one row per (X,Y,Z) with coboundary_terms=[{phi,coeff}]'),
    'gemini31p-b22': ('coboundary_evaluated', _rows_flat('phi_param'),
                      'one row per (X,Y,Z,phi_param,coeff)'),
    'gemini31p-b24': ('coboundary_structure', _rows_b24cob,
                      'one row per (X,Y,Z,f_in,f_out,coeff); column key (f_in, f_out)'),
    'gemini31p-high-b02': ('coboundary_structure.delta_f_constants', None,
                           'nested {"X,Y": {Z: {phi: coeff}}}, float coeffs'),
    'luna-b14': ('coboundary.coboundary_coefficients', _rows_terms('coefficients', 'parameter'),
                 'one row per (X,Y,Z) with coefficients=[{parameter,coeff}]'),
    'luna-b20': ('coboundary.coefficients', _rows_terms('terms', 'parameter'),
                 'one row per (X,Y,Z) with terms=[{parameter,coeff}]'),
}


def _basis_set(run, n):
    B = json.load(open(path(run, n, 'structure')))['basis']
    return set(B['even']) | set(B['odd'])


def _load(run, n, kind, table, parse):
    fam = _FAM[run]
    lp, rd, enc = table[fam]
    obj = _get(json.load(open(path(run, n, kind))), lp)
    rows = _nested_rows(obj) if rd is None else (r for e in obj for r in rd(e))
    basis = _basis_set(run, n)
    D, seen, rep = {}, set(), 0
    for X, Y, Z, p, c in rows:
        if X not in basis or Y not in basis or (Z not in basis and Z != 'K'):
            raise ValueError('%s n=%d %s: label not in basis: %r' % (run, n, kind, (X, Y, Z)))
        k = (X, Y, Z, p)
        rep += k in seen
        seen.add(k)
        add(D, parse(p), (X, Y, Z), c)
    return D, dict(list_path='.' + lp, entries=len(obj), encoding=enc, repeated_rows_summed=rep)


def load_gamma(run, n):
    M = _gbmap(run, n)

    def parse(lab):
        if lab not in M:
            raise KeyError('gb label %r not defined by the run (%s)' % (lab, sorted(M)))
        return M[lab]
    return _load(run, n, 'gamma', GAMMA, parse)


def load_coboundary(run, n):
    fam = _FAM[run]
    if fam == 'luna-b18':
        c = json.load(open(path(run, n, 'coboundary')))['coboundary']
        return None, dict(list_path='.coboundary.coboundary_coefficients', entries=len(c['coboundary_coefficients']),
                          encoding='delta_f of one fixed odd map .coboundary.odd_map (%d terms), rows (X,Y,Z,coeff) '
                                   'without phi parameters' % len(c['odd_map']))
    if fam == 'gemini31p-b22':
        d = json.load(open(path(run, n, 'coboundary')))
        allowed = set(d['f_parameters'])
        used = {e['phi_param'] for e in d['coboundary_evaluated']}
        if not used <= allowed:
            raise ValueError('phi labels not in f_parameters: %s' % sorted(used - allowed))
    return _load(run, n, 'coboundary', COB, str)


# ---------- structure ----------

def _words_b22(words, labels):
    out = []
    for w in words:
        if w not in labels:
            raise ValueError('word %r not an oscillator label %s' % (w, sorted(labels)))
        m = re.fullmatch(r'([ab])(\d+)_([pm])', w)
        if not m or (m[1] == 'a' and m[2] != '1'):
            raise ValueError('unexpected word %r' % w)
        out.append('%s_%s_%s' % (m[1], m[2], m[3]))
    return out


_TOK = re.compile(r'(a)([+-])$|b(\d+)([+-])$')


def _parse_realization_string(s, labels):
    """high-b02 format_realization strings -> [(Fraction, [words])]."""
    terms, cur = [], None
    for tok in s.split():
        if tok in ('+', '-'):
            if cur is not None and (cur['c'] is not None or cur['w']):
                terms.append(cur)
                cur = None
            if cur is None:
                cur = dict(sign=1, c=None, w=[])
            if tok == '-':
                cur['sign'] = -cur['sign']
            continue
        if cur is None:
            cur = dict(sign=1, c=None, w=[])
        m = _TOK.fullmatch(tok)
        if m:
            w = ('a_1_%s' % {'+': 'p', '-': 'm'}[m[2]]) if m[1] else ('b_%s_%s' % (m[3], {'+': 'p', '-': 'm'}[m[4]]))
            if w not in labels:
                raise ValueError('word %r (from %r) not an oscillator label' % (w, tok))
            cur['w'].append(w)
        else:
            if cur['c'] is not None or cur['w']:
                raise ValueError('number %r not at the start of a term in %r' % (tok, s))
            cur['c'] = F(tok)
    if cur is not None:
        if cur['c'] is None and not cur['w']:
            raise ValueError('dangling sign in %r' % s)
        terms.append(cur)
    return [(t['sign'] * (t['c'] if t['c'] is not None else F(1)), t['w']) for t in terms]


def load_structure(run, n):
    fam = _FAM[run]
    if fam not in ('gemini31p-b22', 'gemini31p-high-b02'):
        return _default_body(run, n)
    S = json.load(open(path(run, n, 'structure')))
    B = S['basis']
    basis = list(B['even']) + list(B['odd'])
    parity = {x: 0 for x in B['even']} | {x: 1 for x in B['odd']}
    og = S['oscillator_generators']
    labels = set(og['fermions']['labels']) | set(og['bosons']['labels'])
    sc = {}
    if fam == 'gemini31p-b22':
        R = S['generator_realization']['realizations']
        real = {g: [(num(t['coeff']), _words_b22(t['words'], labels)) for t in R[g]['standard_form']] for g in basis}
        for e in S.get('structure_constants', []):
            sc.setdefault((e['X'], e['Y']), {})[e['Z']] = num(e['coeff'])
    else:
        R = S['generator_realization']
        real = {g: _parse_realization_string(R[g], labels) for g in basis}
        bs = set(basis)
        for xy, zs in S['structure_constants'].items():
            X, Y = xy.split(',')
            for Z, c in zs.items():
                if X not in bs or Y not in bs or (Z not in bs and Z != 'K'):
                    raise ValueError('structure constant label not in basis: %r' % ((X, Y, Z),))
                sc.setdefault((X, Y), {})[Z] = _exact(c)
    return basis, parity, real, sc


def _default_body(run, n):
    """Same as loader.load_structure's default body (the loader's wrapper would dispatch back here)."""
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


# ---------- evaluated ----------

def evaluated_info(run, n):
    fam = _FAM[run]
    fn = path(run, n, 'evaluated')
    if fam == 'gemini31p-b24':   # only C_n_evaluated_all_ones.json is committed
        fn = os.path.join(FG_ROOT, run, 'data', 'C_%d_evaluated_all_ones.json' % n)
    d = json.load(open(fn))
    out = []
    if fam == 'gemini31p-high-b02':
        ev = d['evaluated_deformation']
        sc = ev['evaluated_gamma_structure_constants']
        out.append(dict(file=os.path.basename(fn), list_path='.evaluated_deformation.evaluated_gamma_structure_constants',
                        entries=sum(len(z) for z in sc.values()), keys=['"X,Y"', 'Z', 'coeff (float)'],
                        gb_assignment=ev.get('gb_assignment')))
        return out

    def walk(o, p=''):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + '.' + k)
        elif isinstance(o, list) and o and isinstance(o[0], dict) and 'X' in o[0] and 'Y' in o[0]:
            out.append(dict(file=os.path.basename(fn), list_path=p, entries=len(o),
                            keys=sorted({k for e in o for k in e})))
    walk(d)
    return out
