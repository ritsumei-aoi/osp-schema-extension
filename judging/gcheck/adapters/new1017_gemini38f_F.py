"""Adapter for the interactive (human-gated F-) run thm01-R-gemini38f-r2-F (Worker Gemini 3.8 Flash,
agy 1.3.6; Manager Gemini 4 Argon (Low)); shadow repository HEAD 12313a5 (no issue files, Worker
does not use git). Written 2026-10-17.

Only translates encodings and labels; Worker values are never changed. Every rule below was read
from the run's own data files and, where noted, its own source code (read, not run); the
cross-checks listed raise on mismatch. load_structure is NOT overridden: the default loader reads
basis / generator_realization.realizations[*].standard_form (words 'a_1_p', 'b_2_m') /
structure_constants of this run unchanged.

Common rules
- Every gamma / coboundary / evaluated file repeats .basis and .parity of C_n_structure.json; both
  must be equal (checked); the gamma file also repeats .generator_realization (checked equal).
- K: .central_elements.K ('Central identity element; identified with scalar 1 and excluded from
  PBW basis'). src/C_gamma.py decompose_mod_K solves on basis + a constant column and keeps only
  the basis coordinates, so K components are dropped ('modulo K'). Facts kept as is: no row of any
  list used has Z == 'K' (also none in the structure constants). A row with Z == 'K' would be
  passed through as K; X, Y outside the basis or Z outside basis + K raise.
- Rows must have exactly the keys {X, Y, Z, coeff, sign_rule} (+ param for gamma) with
  sign_rule == 'graded'; coeff is a rational string.
- Duplicate (X,Y,Z,param) rows would be summed (loader.add); their number is reported.

gamma (C_n_gamma.json)
- Rows: .gamma_structure_constants, one row per (X,Y,Z,param,coeff). The file holds the same list
  again at .inhomogeneous_deformation.gamma_structure_constants (checked identical) and the gb
  matrix twice (.deformation_parameters.gb_matrix == .inhomogeneous_deformation.gb_matrix, checked).
- gb label -> reference tuple (sigma, j, s) of [b_j^s, a_1^sigma] = -gb kappa (refmodel /
  independent_triviality4). The file states this relation in gb_matrix.exchange_relations
  ('[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa'; checked, normalized text, as in
  new1013_gemini38f). Mapping from the file's own matrix: gb_matrix.parameter_names[r][c] with
  row_labels[r] = 'a_1_<sigma>' and col_labels[c] = 'b_<j>_<s>' (p -> '+', m -> '-');
  dimensions == [2, 2n]. Cross-checks: every label equals 'gb_a1<sigma>_b<j><s>' for its matrix
  position (src/C_gamma.py get_gb_matrix_info builds f"gb_a1{row}_b{j}{col}" for row in (p, m);
  normal_order_word_ua attaches gb_param = f"gb_a1{sigma}_b{j}{s}" with coefficient -1 (times
  sign_choice = 1 and its Koszul sign) to the reordering b_j^s a_1^sigma -> a_1^sigma b_j^s),
  loader.gbparse(label) equals the matrix position, the table covers the 4n tuples exactly, and
  every row's param is declared.

coboundary (C_n_coboundary.json)
- The file holds delta f of ONE fixed map (.map_f, configuration 'mode_paired_exchange',
  scaling '1'; src/C_coboundary.py build_mode_paired_exchange_map / compute_coboundary) as rows
  .coboundary_structure_constants (X,Y,Z,coeff,sign_rule) without phi labels -> no phi structure:
  returns None + info (as sonnet46-r2-F in new1011_interactive). Checks: row keys / labels as
  above; every .map_f.mapping entry has source and target in the basis with opposite parity.
  (The Worker's general-map analysis is in src/C_triviality_analysis.py, not in a data file; not
  read.)

evaluated (C_n_evaluated.json)
- evaluated_info: every list of X/Y rows in data/C_n_evaluated*.json (here one file:
  .evaluated_gamma_structure_constants and .total_evaluated_bracket, profile 'all_plus_one');
  list_path is prefixed by the file name. Check: .evaluated_parameters.parameter_values covers
  exactly the declared gb labels, and .evaluated_gamma_structure_constants equals the gamma rows
  summed with those values (the definition in src/C_evaluated.py evaluate_gamma_constants).
  Values are not used by analyze.py.

n: data exist for n = 1, 2, 3 in the copy (no n = 4 files; a missing file raises
FileNotFoundError, reported by analyze.py as an error).
"""
import glob, json, os, re
from fractions import Fraction as F
from loader import num, add, entry_lists, gbparse, FG_ROOT

RUNS = ['thm01-R-gemini38f-r2-F']

PM = {'p': '+', 'm': '-'}
ROW_KEYS = {'X', 'Y', 'Z', 'coeff', 'sign_rule'}
_REL = re.compile(r'\[b_j\^s,a_1\^(σ|sigma)\]=-gb_\{(σ|sigma),j,s\}')


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


def _structure(run, n):
    return json.load(open(_one(run, n, 'structure')))


def _check_basis(run, n, d, kind):
    S = _structure(run, n)
    if d['basis']['even'] != S['basis']['even'] or d['basis']['odd'] != S['basis']['odd']:
        raise ValueError('%s n=%d: %s file basis differs from structure file basis' % (run, n, kind))
    if d['parity'] != S['parity']:
        raise ValueError('%s n=%d: %s file parity differs from structure file parity' % (run, n, kind))
    if 'generator_realization' in d and d['generator_realization'] != S['generator_realization']:
        raise ValueError('%s n=%d: %s file generator_realization differs from structure file' % (run, n, kind))
    par = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    if par != S['parity']:
        raise ValueError('%s n=%d: structure .parity inconsistent with .basis' % (run, n))
    return par


def _check_row(run, n, e, keys, par):
    if set(e) != keys:
        raise ValueError('%s n=%d: unexpected row keys %r' % (run, n, sorted(e)))
    if e['sign_rule'] != 'graded':
        raise ValueError('%s n=%d: sign_rule %r' % (run, n, e['sign_rule']))
    if e['X'] not in par or e['Y'] not in par:
        raise ValueError('%s n=%d: row argument outside basis: %s %s' % (run, n, e['X'], e['Y']))
    if e['Z'] not in par and e['Z'] != 'K':
        raise ValueError('%s n=%d: Z label outside basis+K: %s' % (run, n, e['Z']))


def _gb_table(run, n, d):
    M = d['inhomogeneous_deformation']['gb_matrix']
    if d['deformation_parameters']['gb_matrix'] != M:
        raise ValueError('%s n=%d: the two gb_matrix copies differ' % (run, n))
    if not _REL.search(M['exchange_relations'].replace(' ', '')):
        raise ValueError('%s: gamma file does not state [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa' % run)
    if list(M['dimensions']) != [2, 2 * n] or len(M['row_labels']) != 2 or len(M['col_labels']) != 2 * n:
        raise ValueError('%s n=%d: gb_matrix dimensions %r' % (run, n, M['dimensions']))
    tab = {}
    for i, rl in enumerate(M['row_labels']):
        mr = re.fullmatch(r'a_1_([pm])', rl)
        if not mr:
            raise ValueError('%s: unexpected gb row label %r' % (run, rl))
        for k, cl in enumerate(M['col_labels']):
            mc = re.fullmatch(r'b_(\d+)_([pm])', cl)
            if not mc:
                raise ValueError('%s: unexpected gb column label %r' % (run, cl))
            lab = M['parameter_names'][i][k]
            t = (PM[mr[1]], int(mc[1]), PM[mc[2]])
            if lab != 'gb_a1%s_b%s%s' % (mr[1], mc[1], mc[2]):
                raise ValueError('%s: gb label %s at (%s, %s) is not gb_a1<sigma>_b<j><s>' % (run, lab, rl, cl))
            if gbparse(lab) != t:
                raise ValueError('%s: gb label %s: gbparse %s != matrix position %s' % (run, lab, gbparse(lab), t))
            if lab in tab:
                raise ValueError('%s: gb label %s repeated' % (run, lab))
            tab[lab] = t
    full = {(sg, k, sb) for sg in '+-' for k in range(1, n + 1) for sb in '+-'}
    if set(tab.values()) != full or len(tab) != len(full):
        raise ValueError('%s n=%d: gb table does not cover the 4n tuples exactly: %s' % (run, n, tab))
    return tab


def _gamma_rows(run, n):
    d = json.load(open(_one(run, n, 'gamma')))
    par = _check_basis(run, n, d, 'gamma')
    tab = _gb_table(run, n, d)
    rows = d['gamma_structure_constants']
    if d['inhomogeneous_deformation']['gamma_structure_constants'] != rows:
        raise ValueError('%s n=%d: the two gamma_structure_constants copies differ' % (run, n))
    for e in rows:
        _check_row(run, n, e, ROW_KEYS | {'param'}, par)
        if e['param'] not in tab:
            raise KeyError('%s: gb label %s not declared' % (run, e['param']))
    return rows, tab


def load_gamma(run, n):
    rows, tab = _gamma_rows(run, n)
    D, seen, dup = {}, set(), 0
    for e in rows:
        key = (e['X'], e['Y'], e['Z'], e['param'])
        dup += key in seen
        seen.add(key)
        add(D, tab[e['param']], (e['X'], e['Y'], e['Z']), num(e['coeff']))
    return D, dict(list_path='.gamma_structure_constants', entries=len(rows),
                   encoding='one row per (X,Y,Z,param,coeff); gb from gb_matrix.parameter_names',
                   gb_rule='gb_a1<sigma>_b<j><s> (gb_matrix position; src/C_gamma.py)',
                   gb_labels_used=len({k[3] for k in seen}), duplicate_rows=dup,
                   K_rows=sum(1 for e in rows if e['Z'] == 'K'))


def load_coboundary(run, n):
    f = _one(run, n, 'coboundary')
    d = json.load(open(f))
    par = _check_basis(run, n, d, 'coboundary')
    for m in d['map_f']['mapping']:
        if m['source'] not in par or m['target'] not in par or par[m['source']] == par[m['target']]:
            raise ValueError('%s n=%d: map_f entry %r is not an odd map between basis labels' % (run, n, m))
    rows = d['coboundary_structure_constants']
    for e in rows:
        _check_row(run, n, e, ROW_KEYS, par)
    info = ('.coboundary_structure_constants: %d rows (X,Y,Z,coeff,sign_rule) without phi labels; '
            'map_f configuration=%r scaling=%r with %d mapping entries (delta f of one fixed map)'
            % (len(rows), d['map_f']['configuration'], d['map_f']['scaling'], len(d['map_f']['mapping'])))
    return None, dict(file=os.path.basename(f), list_path=None, entries=0, encoding=info)


def evaluated_info(run, n):
    grows, tab = _gamma_rows(run, n)
    out = []
    for f in _data(run, n, 'C_%d_evaluated*.json'):
        d = json.load(open(f))
        par = _check_basis(run, n, d, 'evaluated')
        vals = d['evaluated_parameters']['parameter_values']
        if set(vals) != set(tab):
            raise ValueError('%s n=%d: evaluated parameter_values labels differ from gb labels' % (run, n))
        exp = {}
        for e in grows:
            add(exp, 0, (e['X'], e['Y'], e['Z']), num(e['coeff']) * num(vals[e['param']]))
        exp = exp.get(0, {})
        got = {}
        for e in d['evaluated_gamma_structure_constants']:
            _check_row(run, n, e, ROW_KEYS, par)
            add(got, 0, (e['X'], e['Y'], e['Z']), num(e['coeff']))
        if got.get(0, {}) != exp:
            raise ValueError('%s n=%d: evaluated_gamma_structure_constants != gamma rows at parameter_values'
                             % (run, n))
        for p, l in entry_lists(d):
            out.append(dict(list_path=os.path.basename(f) + ':' + p, entries=len(l),
                            keys=sorted({k for e in l for k in e}),
                            profile=d['evaluated_parameters'].get('profile_name')))
    return out
