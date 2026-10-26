"""Adapter for the interactive (human-gated A1/A2/F) thm01-R runs finished 2026-10-09..11:
luna-r2-A1, luna-r2-A2, luna-r2-F, luna-r3-A1, sonnet46-r2-A1, sonnet46-r2-A2, sonnet46-r2-F,
sonnet46-r3-A1.

Only translates encodings and labels; Worker values are never changed. Every rule below was
read from the run's own data files (and, where noted, its own source code); the cross-checks
listed raise on mismatch. load_structure is NOT overridden: the default loader reads
basis / generator_realization.realizations[*].standard_form (words 'a_1_p', 'b_2_m') /
structure_constants of every run here unchanged.

Common rules
- K components: rows with Z == 'K' (every run documents K as the even central identity;
  no other non-basis Z label occurs in the lists used). No row of the lists used has X or Y
  outside the Worker basis (checked: raises otherwise).
- gb label -> reference tuple (sigma, j, s) of [b_j^s, a_1^sigma] = -gb kappa (refmodel /
  independent_triviality4). Each gamma file states this same relation for its labels
  (checked: the normalized text '[b_j^s,a_1^sigma]=-gb_{sigma,j,s}' must occur in the file).
- phi labels are used verbatim as column names (only their identity matters); every label
  used must be declared in the file's own odd-linear-map declaration (checked).
- Duplicate (X,Y,Z,label) rows would be summed (loader.add); their number is reported.
- evaluated_info: every data/C_n_evaluated*.json (sonnet46-r2-A1 '_uniform_plus',
  sonnet46-r2-A2 '_allplus', sonnet46-r3-A1 '_all1'); list_path is prefixed by the file name.

Per-run rules (_CFG)
luna-r2-A1   gamma .inhomogeneous_deformation.gamma_coefficients: (X,Y,Z,coeff='linear expr in gb').
             gb from .inhomogeneous_deformation.gb_matrix rows (a_1_sigma) x columns (b_j_s) ->
             entries[r][c]; cross-check loader.gbparse(label) == matrix position.
             coboundary .coboundary.delta_f_coefficients: (X,Y,Z,coeff='linear expr in phi');
             phi declared in .coboundary.odd_linear_map.entries[].parameter.
             (.coboundary.comparison.unmatched_central_components is the Worker's comparison
             output, not delta f; not read.)
luna-r2-A2   gamma .gamma_constants: (X,Y,Z,coeff=[{parameter,scalar}]); gb from
             .inhomogeneous_deformation.gb_matrix row_labels x column_labels -> entries.
             coboundary .coboundary_constants: (X,Y,Z,coeff=[{parameter,scalar}]). Labels are
             declared in .odd_linear_map.coefficients[].parameter with fields source / target and
             the file's own parameterization 'f(e_a) = sum_mu phi__o_mu__from__e_a * o_mu;
             f(o_mu) = sum_a psi__e_a__from__o_mu * e_a' (phi__ for even source, psi__ for odd
             source). Check: every declared label equals '<phi|psi>__<target>__from__<source>'
             with that family rule.
luna-r2-F    gamma .inhomogeneous_deformation.gamma_coefficients: linear expr in gb; gb from
             .inhomogeneous_deformation.gb_matrix (row_labels/column_labels/entries); extra
             cross-check against .inhomogeneous_deformation.mixed_oscillator_relations.relations
             (X=b_j_s, Y=a_1_sigma, parameter, rhs='-<parameter> * kappa').
             coboundary .coboundary_coefficients: linear expr in phi; declared in
             .odd_linear_map.parameters[].symbol.
luna-r3-A1   gamma .inhomogeneous_deformation.gamma_structure: linear expr in gb; gb from top-level
             .gb_matrix row_labels x column_labels -> parameters. coboundary
             .coboundary_structure: linear expr in phi; declared in .odd_linear_map.coefficients[].symbol.
sonnet46-r2-A1  gamma .gamma_structure: (X,Y,Z,gb,coeff). gb from .gb_matrix.parameters[label]
             fields sigma ('+'/'-'), j, s; cross-check with the file's stated label format
             'gb_{sigma_str}{s_str}_{j}' (= loader.gbparse second pattern).
             coboundary .coboundary: (X,Y,Z,phi,coeff); declared in .phi_parameters.labels.
sonnet46-r2-A2  gamma .gamma_structure: (X,Y,gamma_terms=[{gb_label,Z,coeff}]). gb from
             .gb_matrix.entries[label] fields fermionic (a_1_sigma) / bosonic (b_j_s); cross-check
             loader.gbparse(label). The file records no Z == 'K' rows (fact, kept as is).
             coboundary .coboundary_structure: (X,Y,delta_f_terms=[{phi_label,Z,coeff}]);
             declared in .map_f.phi_parameters.{odd_to_even,even_to_odd}.labels.
sonnet46-r2-F   gamma .inhomogeneous_deformation: (X,Y,Z,gb,coeff). gb label 'gb_{sigma}_{j}_{s}'
             as stated in .gb_parameters.gb_matrix.label_format (checked verbatim) and in the run's
             src/build_C_gamma.py _gb_label (f'gb_{sigma}_{k}_{s}', read, not run); labels must
             be in .gb_parameters.labels and cover all 4n tuples.
             coboundary: the file holds delta f of ONE fixed map (f_map, phi = 1) as rows
             (X,Y,Z,coeff) without phi labels -> no phi structure (returns None + info, like
             may_interactive for such files).
sonnet46-r3-A1  gamma .gamma: (X,Y,Z,gb_label,coeff). gb from .gb_matrix.parameters[] fields
             sigma/k/s ('p'/'m'); cross-check fermionic_oscillator / bosonic_oscillator and
             loader.gbparse(label). coboundary .coboundary: (X,Y,Z,phi_label,coeff); declared
             in .phi_matrix.parameters[].label.
"""
import glob, json, os, re
import sympy as sp
from loader import num, add, entry_lists, gbparse, FG_ROOT

RUNS = ['thm01-R-luna-r2-A1', 'thm01-R-luna-r2-A2', 'thm01-R-luna-r2-F', 'thm01-R-luna-r3-A1',
        'thm01-R-sonnet46-r2-A1', 'thm01-R-sonnet46-r2-A2', 'thm01-R-sonnet46-r2-F',
        'thm01-R-sonnet46-r3-A1']

# run: dict(gamma list path, gamma row kind, gb rule, coboundary list path, coboundary row kind, phi rule)
_CFG = {
    'thm01-R-luna-r2-A1': dict(g='inhomogeneous_deformation.gamma_coefficients', gk='expr', gb='matrix',
                               gbm='inhomogeneous_deformation.gb_matrix',
                               c='coboundary.delta_f_coefficients', ck='expr',
                               phi=('list', 'coboundary.odd_linear_map.entries', 'parameter')),
    'thm01-R-luna-r2-A2': dict(g='gamma_constants', gk='termlist', gb='matrix',
                               gbm='inhomogeneous_deformation.gb_matrix',
                               c='coboundary_constants', ck='termlist',
                               phi=('list', 'odd_linear_map.coefficients', 'parameter')),
    'thm01-R-luna-r2-F': dict(g='inhomogeneous_deformation.gamma_coefficients', gk='expr', gb='matrix',
                              gbm='inhomogeneous_deformation.gb_matrix',
                              c='coboundary_coefficients', ck='expr',
                              phi=('list', 'odd_linear_map.parameters', 'symbol')),
    'thm01-R-luna-r3-A1': dict(g='inhomogeneous_deformation.gamma_structure', gk='expr', gb='matrix',
                               gbm='gb_matrix', c='coboundary_structure', ck='expr',
                               phi=('list', 'odd_linear_map.coefficients', 'symbol')),
    'thm01-R-sonnet46-r2-A1': dict(g='gamma_structure', gk=('col', 'gb'), gb='s46r2a1',
                                   c='coboundary', ck=('col', 'phi'), phi=('strlist', 'phi_parameters.labels')),
    'thm01-R-sonnet46-r2-A2': dict(g='gamma_structure', gk=('nested', 'gamma_terms', 'gb_label'), gb='s46r2a2',
                                   c='coboundary_structure', ck=('nested', 'delta_f_terms', 'phi_label'),
                                   phi=('s46r2a2',)),
    'thm01-R-sonnet46-r2-F': dict(g='inhomogeneous_deformation', gk=('col', 'gb'), gb='s46r2f',
                                  c=None, ck=None, phi=None),
    'thm01-R-sonnet46-r3-A1': dict(g='gamma', gk=('col', 'gb_label'), gb='s46r3a1',
                                   c='coboundary', ck=('col', 'phi_label'), phi=('list', 'phi_matrix.parameters', 'label')),
}

PM = {'p': '+', 'm': '-', '+': '+', '-': '-'}


def _data(run, n, pattern):
    fs = sorted(glob.glob(os.path.join(FG_ROOT, run, 'data', pattern % n)))
    if not fs:
        raise FileNotFoundError('%s: no data/%s' % (run, pattern % n))
    return fs


def _one(run, n, kind):
    f = _data(run, n, 'C_%d_' + kind + '.json')
    if len(f) != 1:
        raise ValueError('%s: expected one %s file, got %s' % (run, kind, f))
    return f[0]


def _get(d, p):
    for k in p.split('.'):
        d = d[k]
    return d


def _basis(run, n):
    S = json.load(open(_one(run, n, 'structure')))
    B = S['basis']
    return {x: 0 for x in B['even']} | {x: 1 for x in B['odd']}


_IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


def _linexpr(s):
    """'-2*gb_x + gb_y/2' -> {'gb_x': F(-2), 'gb_y': F(1,2)}; must be homogeneous linear
    (a pure '0' gives {}; any other constant raises)."""
    names = set(_IDENT.findall(s))
    if not names:
        if num(s) != 0:
            raise ValueError('constant term %r without label' % s)
        return {}
    syms = {nm: sp.Symbol(nm) for nm in names}
    e = sp.expand(sp.sympify(s, locals=syms))
    if e == 0:
        return {}
    order = sorted(names)
    P = sp.Poly(e, *[syms[nm] for nm in order])
    out = {}
    for mon, c in P.terms():
        if sum(mon) != 1:
            raise ValueError('non-linear or constant term in %r' % s)
        c = sp.Rational(c)
        out[order[mon.index(1)]] = num('%d/%d' % (c.p, c.q))
    return out


def _rows(rows, kind):
    """Yield (X, Y, Z, label, Fraction) for each term; kind from _CFG."""
    for e in rows:
        if kind == 'expr':
            if not isinstance(e['coeff'], str):
                raise ValueError('expected string coeff: %r' % (e,))
            for lab, c in _linexpr(e['coeff']).items():
                yield e['X'], e['Y'], e['Z'], lab, c
        elif kind == 'termlist':
            for t in e['coeff']:
                if set(t) != {'parameter', 'scalar'}:
                    raise ValueError('unexpected term %r' % (t,))
                yield e['X'], e['Y'], e['Z'], t['parameter'], num(t['scalar'])
        elif kind[0] == 'col':
            yield e['X'], e['Y'], e['Z'], e[kind[1]], num(e['coeff'])
        elif kind[0] == 'nested':
            for t in e[kind[1]]:
                yield e['X'], e['Y'], t['Z'], t[kind[2]], num(t['coeff'])
        else:
            raise KeyError(kind)


def _kind_str(kind, what):
    if kind == 'expr':
        return "(X,Y,Z,coeff='linear expression in %s labels')" % what
    if kind == 'termlist':
        return '(X,Y,Z,coeff=[{parameter,scalar}])'
    if kind[0] == 'col':
        return '(X,Y,Z,%s,coeff)' % kind[1]
    return '(X,Y,%s=[{%s,Z,coeff}])' % (kind[1], kind[2])


def _parse(run, n, rows, kind, labelmap):
    par = _basis(run, n)
    D, seen, dup = {}, set(), 0
    for X, Y, Z, lab, c in _rows(rows, kind):
        if X not in par or Y not in par:
            raise ValueError('%s n=%d: row argument outside basis: %s %s' % (run, n, X, Y))
        if Z not in par and Z != 'K':
            raise ValueError('%s n=%d: Z label outside basis+K: %s' % (run, n, Z))
        key = (X, Y, Z, lab)
        dup += key in seen
        seen.add(key)
        add(D, labelmap(lab), (X, Y, Z), c)
    return D, dup, {lab for (_x, _y, _z, lab) in seen}


# ---------------- gb rules ----------------

_REL = re.compile(r'\[b_j\^s,a_1\^(σ|sigma)\]=-gb_\{(σ|sigma),j,s\}')


def _check_relation(run, d):
    txt = json.dumps(d, ensure_ascii=False).replace(' ', '')
    if not _REL.search(txt):
        raise ValueError('%s: gamma file does not state [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa' % run)


def _row_sigma(lab):
    m = re.fullmatch(r'a_1_([pm])', lab)
    if not m:
        raise ValueError('unexpected gb row label %r' % lab)
    return PM[m[1]]


def _col_js(lab):
    m = re.fullmatch(r'b_(\d+)_([pm])', lab)
    if not m:
        raise ValueError('unexpected gb column label %r' % lab)
    return int(m[1]), PM[m[2]]


def _gb_table(run, n, d):
    cfg = _CFG[run]
    rule = cfg['gb']
    tab = {}
    if rule == 'matrix':
        M = _get(d, cfg['gbm'])
        rows = M.get('rows', M.get('row_labels'))
        cols = M.get('columns', M.get('column_labels', M.get('cols')))
        ent = M.get('entries', M.get('parameters'))
        for i, rl in enumerate(rows):
            for k, cl in enumerate(cols):
                j, s = _col_js(cl)
                tab[ent[i][k]] = (_row_sigma(rl), j, s)
        for lab, t in tab.items():
            if gbparse(lab) != t:
                raise ValueError('%s: gb label %s: gbparse %s != matrix position %s' % (run, lab, gbparse(lab), t))
        if run == 'thm01-R-luna-r2-F':
            for r in d['inhomogeneous_deformation']['mixed_oscillator_relations']['relations']:
                j, s = _col_js(r['X'])
                t = (_row_sigma(r['Y']), j, s)
                if tab[r['parameter']] != t or r['rhs'].replace(' ', '') != '-%s*κ' % r['parameter']:
                    raise ValueError('%s: mixed_oscillator_relations mismatch %r' % (run, r))
    elif rule == 's46r2a1':
        P = d['gb_matrix']['parameters']
        if 'gb_{sigma_str}{s_str}_{j}' not in d['gb_matrix']['gram_matrix_convention']:
            raise ValueError('%s: label format statement not found' % run)
        for lab, v in P.items():
            t = (PM[v['sigma']], int(v['j']), PM[v['s']])
            m = re.fullmatch(r'gb_([pm])([pm])_(\d+)', lab)
            if not m or (PM[m[1]], int(m[3]), PM[m[2]]) != t or gbparse(lab) != t:
                raise ValueError('%s: gb label %s vs fields %s' % (run, lab, t))
            tab[lab] = t
    elif rule == 's46r2a2':
        for lab, v in d['gb_matrix']['entries'].items():
            j, s = _col_js(v['bosonic'])
            t = (_row_sigma(v['fermionic']), j, s)
            if gbparse(lab) != t:
                raise ValueError('%s: gb label %s vs fields %s' % (run, lab, t))
            tab[lab] = t
    elif rule == 's46r2f':
        G = d['gb_parameters']
        fmt = G['gb_matrix']['label_format']
        if not fmt.startswith('gb_{σ}_{j}_{s}'):
            raise ValueError('%s: unexpected label_format %r' % (run, fmt))
        for lab in G['labels']:
            m = re.fullmatch(r'gb_([pm])_(\d+)_([pm])', lab)
            if not m:
                raise ValueError('%s: label %s does not match label_format' % (run, lab))
            tab[lab] = (PM[m[1]], int(m[2]), PM[m[3]])
    elif rule == 's46r3a1':
        for v in d['gb_matrix']['parameters']:
            t = (PM[v['sigma']], int(v['k']), PM[v['s']])
            j, s = _col_js(v['bosonic_oscillator'])
            if (_row_sigma(v['fermionic_oscillator']), j, s) != t or gbparse(v['label']) != t:
                raise ValueError('%s: gb label %s inconsistent' % (run, v['label']))
            tab[v['label']] = t
    else:
        raise KeyError(rule)
    full = {(sg, k, sb) for sg in '+-' for k in range(1, n + 1) for sb in '+-'}
    if set(tab.values()) != full or len(tab) != len(full):
        raise ValueError('%s n=%d: gb table does not cover the 4n tuples exactly: %s' % (run, n, tab))
    return tab


def load_gamma(run, n):
    cfg = _CFG[run]
    d = json.load(open(_one(run, n, 'gamma')))
    _check_relation(run, d)
    tab = _gb_table(run, n, d)
    rows = _get(d, cfg['g'])

    def lm(lab):
        if lab not in tab:
            raise KeyError('%s: gb label %s not declared' % (run, lab))
        return tab[lab]
    D, dup, used = _parse(run, n, rows, cfg['gk'], lm)
    return D, dict(list_path='.' + cfg['g'], entries=len(rows),
                   encoding='one row per ' + _kind_str(cfg['gk'], 'gb'),
                   gb_rule=cfg['gb'], gb_labels_used=len(used), duplicate_rows=dup)


def _declared_phi(run, n, d):
    rule = _CFG[run]['phi']
    if rule[0] == 'list':
        return {e[rule[2]] for e in _get(d, rule[1])}
    if rule[0] == 'strlist':
        return set(_get(d, rule[1]))
    if rule[0] == 's46r2a2':
        P = d['map_f']['phi_parameters']
        return set(P['odd_to_even']['labels']) | set(P['even_to_odd']['labels'])
    raise KeyError(rule)


def load_coboundary(run, n):
    cfg = _CFG[run]
    f = _one(run, n, 'coboundary')
    d = json.load(open(f))
    if cfg['c'] is None:
        lists = list(entry_lists(d))
        info = '; '.join('%s: %d rows (X,Y,Z,coeff) without phi labels: keys=%s'
                         % (lp, len(l), sorted({k for e in l for k in e})) for lp, l in lists)
        info += '; f_map.phi=%r (delta f of one fixed map)' % d.get('f_map', {}).get('phi')
        return None, dict(file=os.path.basename(f), list_path=None, entries=0, encoding=info)
    rows = _get(d, cfg['c'])
    D, dup, used = _parse(run, n, rows, cfg['ck'], str)
    decl = _declared_phi(run, n, d)
    if run == 'thm01-R-luna-r2-A2':
        par = _basis(run, n)
        for e in _get(d, cfg['phi'][1]):
            fam = 'phi' if par[e['source']] == 0 else 'psi'
            if e['parameter'] != '%s__%s__from__%s' % (fam, e['target'], e['source']) or par[e['source']] == par[e['target']]:
                raise ValueError('%s: declared label %r inconsistent with source/target' % (run, e))
    if not used <= decl:
        raise ValueError('%s: undeclared phi labels: %s' % (run, sorted(used - decl)[:5]))
    note = '%d declared phi labels, %d used' % (len(decl), len(used))
    return D, dict(file=os.path.basename(f), list_path='.' + cfg['c'], entries=len(rows),
                   encoding='one row per ' + _kind_str(cfg['ck'], 'phi'), phi_labels=note,
                   duplicate_rows=dup)


def evaluated_info(run, n):
    out = []
    for f in _data(run, n, 'C_%d_evaluated*.json'):
        d = json.load(open(f))
        for p, l in entry_lists(d):
            out.append(dict(list_path=os.path.basename(f) + ':' + p, entries=len(l),
                            keys=sorted({k for e in l for k in e})))
    return out
