"""Adapter for the interactive (human-gated A1) run thm01-R-gemini38f-r3-A1 (Worker Gemini 3.8 Flash
(Medium), agy 1.4.0; successor Manager Gemini 4 Argon (Low), agy 1.4.0), final commit a420a13.
Written 2026-10-17.

Only translates encodings and labels; Worker values are never changed. Every rule below was read
from the run's own data files and, where noted, its own source code (read, not run); the
cross-checks listed raise on mismatch. load_structure is NOT overridden: the default loader reads
basis / generator_realization.realizations[*].standard_form (words 'a_1_p', 'b_2_m') /
structure_constants of this run unchanged.

Common rules
- Every gamma / coboundary / evaluated file repeats .algebra, .central_elements, .basis and
  .parity of C_n_structure.json; all four must be equal (checked); .parity must agree with
  .basis.even / .basis.odd (checked).
- K: .central_elements.K ('Even central identity element (identified with scalar 1; excluded from
  PBW basis)'). src/C_gamma.py compute_gamma_cocycles builds gamma only from the Schema 1
  structure constants and the basis (no K column); Schema 1 has no row with Z == 'K'. Facts kept as
  is: no row of any list used has Z == 'K'. A row with Z == 'K' would be passed through as K;
  X, Y outside the basis or Z outside basis + K raise.
- Rows must have exactly the keys {X, Y, Z, coeff, sign_rule} (+ param for gamma) with
  sign_rule == 'graded'; coeff is a rational string.
- Duplicate (X,Y,Z,param) rows would be summed (loader.add); their number is reported.

gamma (C_n_gamma.json)
- Rows: .inhomogeneous_deformation (a list), one row per (X,Y,Z,param,coeff).
- gb label -> reference tuple (sigma, j, s) of [b_j^s, a_1^sigma] = -gb kappa (refmodel /
  independent_triviality4). The file states this relation in
  .deformation_parameters.exchange_relations ('[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa';
  checked, normalized text, as in new1013_gemini38f / new1017_gemini38f_F).
  Mapping from the file's own declaration: .deformation_parameters.labels is the row-major
  flattening of the [2, 2n] matrix with .rows[r] = 'a_1_<sigma>' and .columns[c] = 'b_<j>_<s>'
  (p -> '+', m -> '-'), i.e. labels[r * 2n + c]; src/C_gamma.py build_schema2_json builds the
  labels in exactly this order (for sigma in (p, m): for k in 1..n: for s in (p, m):
  f"gb_a1{sigma}_b{k}{s}") with rows ['a_1_p', 'a_1_m'] and columns [b_k_p, b_k_m for k].
  Cross-checks: count == 4n == len(labels), matrix_shape == [2, 2n], each label equals
  'gb_a1<sigma>_b<j><s>' for its matrix position, loader.gbparse(label) equals the position, the
  table covers the 4n tuples exactly, and every row's param is declared.
- What gamma IS (fact, not used as a rule): after the I08 correction (8e682ad) src/C_gamma.py
  defines gamma(gb) = delta f_Theta with f_Theta(W) = [W, Theta(gb)] and, per label (get_theta_mapping),
  gb_a1p_bjp -> 1/2 E_eps1_delj_mm, gb_a1p_bjm -> -1/2 E_eps1_delj_mp, gb_a1m_bjp -> 1/2 E_eps1_delj_pm,
  gb_a1m_bjm -> -1/2 E_eps1_delj_pp; the parameter label of each row is the label of the term it
  came from, which is all this adapter uses.

coboundary (C_n_coboundary.json; C_n_coboundary_all_plus.json is a byte-identical alias written by
src/compute_C_coboundary.py, checked equal and not read separately)
- The file holds delta f of ONE fixed map (.map_f, configuration 'inner_odd_generator_sum',
  f(X) = [X, Theta] with Theta = scaling * sum of all 4n odd basis elements, scaling '1';
  src/compute_C_coboundary.py) as rows .coboundary_structure (X,Y,Z,coeff,sign_rule) without phi
  labels -> no phi structure: returns None + info (as r2-F in new1017_gemini38f_F). Checks: row
  keys / labels as above; every .map_f.non_zero_components entry has source and target in the basis
  with opposite parity. (The Worker's general-map analysis is in src/compare_C_triviality.py, not in
  a data file; not read.)

evaluated (C_n_evaluated.json and C_n_evaluated_all_plus.json, byte-identical; both listed)
- evaluated_info: every list of X/Y rows in data/C_n_evaluated*.json (.evaluated_deformation and
  .deformed_structure_constants, profile 'all_plus'); list_path is prefixed by the file name.
  Checks: .evaluation_profile.parameters covers exactly the declared gb labels;
  .evaluated_deformation equals the gamma rows summed with those values, and the nonzero
  .deformed_structure_constants coeff_base / coeff_kappa equal the Schema 1 structure constants /
  .evaluated_deformation (the definitions in src/evaluate_C_structure.py build_schema3_json).
  Values are not used by analyze.py.

n: data exist for n = 1, 2, 3 in the copy (no n = 4 files; a missing file raises
FileNotFoundError, reported by analyze.py as an error).

Scribe's records (run_log.md, scribe_checks/chk_gamma.py; cross-check only, not rules): final gamma
rows 68 / 576 / 1788 (n = 1, 2, 3), no Z == 'K' row; matches neither reference for any gb.
"""
import filecmp, glob, json, os, re
from loader import num, add, entry_lists, gbparse, FG_ROOT

RUNS = ['thm01-R-gemini38f-r3-A1']

PM = {'p': '+', 'm': '-'}
ROW_KEYS = {'X', 'Y', 'Z', 'coeff', 'sign_rule'}
_REL = re.compile(r'\[b_j\^s,a_1\^(σ|sigma)\]=-gb_\{(σ|sigma),j,s\}')
_SHARED = ('algebra', 'central_elements', 'basis', 'parity')


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
    for k in _SHARED:
        if d[k] != S[k]:
            raise ValueError('%s n=%d: %s file .%s differs from structure file' % (run, n, kind, k))
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
    P = d['deformation_parameters']
    if not _REL.search(P['exchange_relations'].replace(' ', '')):
        raise ValueError('%s: gamma file does not state [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa' % run)
    rows, cols, labels = P['rows'], P['columns'], P['labels']
    if (P['count'] != 4 * n or len(labels) != 4 * n or list(P['matrix_shape']) != [2, 2 * n]
            or len(rows) != 2 or len(cols) != 2 * n):
        raise ValueError('%s n=%d: gb parameter declaration %r' % (run, n, P))
    tab = {}
    for i, rl in enumerate(rows):
        mr = re.fullmatch(r'a_1_([pm])', rl)
        if not mr:
            raise ValueError('%s: unexpected gb row label %r' % (run, rl))
        for k, cl in enumerate(cols):
            mc = re.fullmatch(r'b_(\d+)_([pm])', cl)
            if not mc:
                raise ValueError('%s: unexpected gb column label %r' % (run, cl))
            lab = labels[i * 2 * n + k]
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
    rows = d['inhomogeneous_deformation']
    if not isinstance(rows, list):
        raise ValueError('%s n=%d: .inhomogeneous_deformation is not a list' % (run, n))
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
    return D, dict(list_path='.inhomogeneous_deformation', entries=len(rows),
                   encoding='one row per (X,Y,Z,param,coeff); gb from deformation_parameters rows x columns',
                   gb_rule='gb_a1<sigma>_b<j><s> (deformation_parameters position; src/C_gamma.py)',
                   gb_labels_used=len({k[3] for k in seen}), duplicate_rows=dup,
                   K_rows=sum(1 for e in rows if e['Z'] == 'K'))


def load_coboundary(run, n):
    f = _one(run, n, 'coboundary')
    alias = os.path.join(os.path.dirname(f), 'C_%d_coboundary_all_plus.json' % n)
    if os.path.exists(alias) and not filecmp.cmp(f, alias, shallow=False):
        raise ValueError('%s n=%d: coboundary alias file differs from C_%d_coboundary.json' % (run, n, n))
    d = json.load(open(f))
    par = _check_basis(run, n, d, 'coboundary')
    M = d['map_f']
    for m in M['non_zero_components']:
        if m['source'] not in par or m['target'] not in par or par[m['source']] == par[m['target']]:
            raise ValueError('%s n=%d: map_f entry %r is not an odd map between basis labels' % (run, n, m))
    rows = d['coboundary_structure']
    for e in rows:
        _check_row(run, n, e, ROW_KEYS, par)
    info = ('.coboundary_structure: %d rows (X,Y,Z,coeff,sign_rule) without phi labels; '
            'map_f configuration=%r definition=%r scaling=%r with %d nonzero components (delta f of one fixed map)'
            % (len(rows), M['configuration'], M['definition'], M['scaling'], len(M['non_zero_components'])))
    return None, dict(file=os.path.basename(f), list_path=None, entries=0, encoding=info)


def evaluated_info(run, n):
    grows, tab = _gamma_rows(run, n)
    sc = {}
    for e in _structure(run, n)['structure_constants']:
        add(sc, 0, (e['X'], e['Y'], e['Z']), num(e['coeff']))
    sc = sc.get(0, {})
    out = []
    for f in _data(run, n, 'C_%d_evaluated*.json'):
        d = json.load(open(f))
        par = _check_basis(run, n, d, 'evaluated')
        vals = d['evaluation_profile']['parameters']
        if set(vals) != set(tab):
            raise ValueError('%s n=%d: evaluation_profile.parameters labels differ from gb labels' % (run, n))
        exp = {}
        for e in grows:
            add(exp, 0, (e['X'], e['Y'], e['Z']), num(e['coeff']) * num(vals[e['param']]))
        exp = exp.get(0, {})
        got = {}
        for e in d['evaluated_deformation']:
            _check_row(run, n, e, ROW_KEYS, par)
            add(got, 0, (e['X'], e['Y'], e['Z']), num(e['coeff']))
        if got.get(0, {}) != exp:
            raise ValueError('%s n=%d: evaluated_deformation != gamma rows at evaluation_profile.parameters'
                             % (run, n))
        base, kap = {}, {}
        for e in d['deformed_structure_constants']:
            _check_row(run, n, e, ROW_KEYS - {'coeff'} | {'coeff_base', 'coeff_kappa'}, par)
            add(base, 0, (e['X'], e['Y'], e['Z']), num(e['coeff_base']))
            add(kap, 0, (e['X'], e['Y'], e['Z']), num(e['coeff_kappa']))
        if base.get(0, {}) != sc or kap.get(0, {}) != exp:
            raise ValueError('%s n=%d: deformed_structure_constants != (structure constants, evaluated_deformation)'
                             % (run, n))
        for p, l in entry_lists(d):
            out.append(dict(list_path=os.path.basename(f) + ':' + p, entries=len(l),
                            keys=sorted({k for e in l for k in e}),
                            profile=d['evaluation_profile'].get('name')))
    return out
