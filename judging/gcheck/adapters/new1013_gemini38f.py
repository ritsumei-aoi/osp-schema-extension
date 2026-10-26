"""Adapter for the interactive (human-gated A1) run thm01-R-gemini38f-r2-A1 (Worker Gemini 3.8 Flash,
agy 1.3.3; Manager Gemini 3.1 Pro), final commit b87a64d. Written 2026-10-13.
(thm01-R-gemini38f-A1, not counted, is NOT handled here.)

Only translates encodings and labels; Worker values are never changed. Every rule below was
read from the run's own data files and, where noted, its own source code (read, not run); the
cross-checks listed raise on mismatch. load_structure is NOT overridden: the default loader reads
basis / generator_realization.realizations[*].standard_form (words 'a_1_p', 'b_2_m') /
structure_constants of this run unchanged.

Common rules
- Every gamma / coboundary / evaluated file repeats the Schema 1 basis; it must equal
  .basis of C_n_structure.json (checked).
- K components: rows with Z == 'K' (.central_elements.K: 'Even central element associated with
  canonical identity scalar'; src/C_gamma.py solves on extended_basis = basis + ['K'] with K the
  word ()). No row of the lists used has X or Y outside the Worker basis or Z outside basis + K
  (checked: raises otherwise).
- Every row must have exactly the keys {X, Y, param, Z, coeff}; coeff is a rational string.
- Duplicate (X,Y,Z,param) rows would be summed (loader.add); their number is reported.

gamma (C_n_gamma.json)
- Rows: .inhomogeneous_deformation.gamma_constants, one row per (X,Y,Z,param,coeff).
- gb label -> reference tuple (sigma, j, s) of [b_j^s, a_1^sigma] = -gb kappa (refmodel /
  independent_triviality4). The file states this relation in
  .inhomogeneous_deformation.exchange_relations.formula
  ('[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa'; checked, normalized text, as in
  new1011_interactive). The label format is read from src/C_gamma.py: get_gb_params builds
  f"gb_{sig}_b{j}{s}" with sig in (a1p, a1m), and bracket_osc uses gb_name = f"gb_a1{sig}_b{j}{s}"
  for [b_j^s, a_1^sig] (coefficient -1) and [a_1^sig, b_j^s] (+1). So 'gb_a1<sigma>_b<j><s>'
  with p -> '+', m -> '-'.
- Checks: labels in .inhomogeneous_deformation.parameters.labels, count == 4n,
  matrix_shape == [2, 2n], every label matches the format, the table equals loader.gbparse(label),
  covers the 4n tuples exactly, and every row's param is declared.

coboundary (C_n_coboundary.json)
- Rows: .coboundary_structure.coboundary_constants, one row per (X,Y,Z,param,coeff).
- phi labels are used verbatim as column names (only their identity matters). Declared in
  .coboundary_structure.linear_map.parameter_labels; src/C_coboundary.py get_elementary_odd_maps:
  param_label = f"phi_{zi}__{zj}" for the elementary map f(zj) = zi with p(zi) = 1 - p(zj)
  (so phi_<output>__<input>). Checks: every declared label splits at '__' into two basis
  labels of opposite parity (no basis label contains '__'), declared count ==
  .linear_map.parameters_count == 2 * #even * #odd, every used label declared, and
  .statistics.total_coboundary_terms == number of rows.
- .triviality_analysis is the Worker's own conclusion, not delta f; not read.

evaluated (C_n_evaluated.json)
- evaluated_info: every list of X/Y rows in data/C_n_evaluated*.json (here one file:
  .evaluated_deformation.evaluated_gamma_constants, profile 'all_plus_one'); list_path is
  prefixed by the file name; .evaluated_deformation.statistics.total_evaluated_gamma_terms must
  equal the row count (checked). Values are not used by analyze.py.

n: data exist for n = 1, 2, 3 in the copy (no n = 4 files; a missing file raises
FileNotFoundError, reported by analyze.py as an error).
"""
import glob, json, os, re
from loader import num, add, entry_lists, gbparse, FG_ROOT

RUNS = ['thm01-R-gemini38f-r2-A1']

PM = {'p': '+', 'm': '-'}
ROW_KEYS = {'X', 'Y', 'param', 'Z', 'coeff'}
_GB = re.compile(r'gb_a1([pm])_b(\d+)([pm])')
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


def _structure_basis(run, n):
    return json.load(open(_one(run, n, 'structure')))['basis']


def _check_basis(run, n, d, kind):
    S = _structure_basis(run, n)
    if d['basis']['even'] != S['even'] or d['basis']['odd'] != S['odd']:
        raise ValueError('%s n=%d: %s file basis differs from structure file basis' % (run, n, kind))
    return {x: 0 for x in S['even']} | {x: 1 for x in S['odd']}


def _parse(run, n, rows, par, labelmap):
    D, seen, dup = {}, set(), 0
    for e in rows:
        if set(e) != ROW_KEYS:
            raise ValueError('%s n=%d: unexpected row keys %r' % (run, n, sorted(e)))
        X, Y, Z, lab = e['X'], e['Y'], e['Z'], e['param']
        if X not in par or Y not in par:
            raise ValueError('%s n=%d: row argument outside basis: %s %s' % (run, n, X, Y))
        if Z not in par and Z != 'K':
            raise ValueError('%s n=%d: Z label outside basis+K: %s' % (run, n, Z))
        key = (X, Y, Z, lab)
        dup += key in seen
        seen.add(key)
        add(D, labelmap(lab), (X, Y, Z), num(e['coeff']))
    return D, dup, {k[3] for k in seen}


def _gb_table(run, n, d):
    I = d['inhomogeneous_deformation']
    txt = I['exchange_relations']['formula'].replace(' ', '')
    if not _REL.search(txt):
        raise ValueError('%s: gamma file does not state [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa' % run)
    P = I['parameters']
    labels = P['labels']
    if P['count'] != 4 * n or len(labels) != 4 * n or list(P['matrix_shape']) != [2, 2 * n]:
        raise ValueError('%s n=%d: gb parameter declaration %r' % (run, n, P))
    tab = {}
    for lab in labels:
        m = _GB.fullmatch(lab)
        if not m:
            raise ValueError('%s: gb label %s does not match gb_a1<sigma>_b<j><s>' % (run, lab))
        t = (PM[m[1]], int(m[2]), PM[m[3]])
        if gbparse(lab) != t:
            raise ValueError('%s: gb label %s: gbparse %s != %s' % (run, lab, gbparse(lab), t))
        tab[lab] = t
    full = {(sg, k, sb) for sg in '+-' for k in range(1, n + 1) for sb in '+-'}
    if set(tab.values()) != full or len(tab) != len(full):
        raise ValueError('%s n=%d: gb table does not cover the 4n tuples exactly: %s' % (run, n, tab))
    return tab


def load_gamma(run, n):
    d = json.load(open(_one(run, n, 'gamma')))
    par = _check_basis(run, n, d, 'gamma')
    tab = _gb_table(run, n, d)
    rows = d['inhomogeneous_deformation']['gamma_constants']

    def lm(lab):
        if lab not in tab:
            raise KeyError('%s: gb label %s not declared' % (run, lab))
        return tab[lab]
    D, dup, used = _parse(run, n, rows, par, lm)
    return D, dict(list_path='.inhomogeneous_deformation.gamma_constants', entries=len(rows),
                   encoding='one row per (X,Y,Z,param,coeff)',
                   gb_rule="gb_a1<sigma>_b<j><s> (src/C_gamma.py)", gb_labels_used=len(used),
                   duplicate_rows=dup)


def load_coboundary(run, n):
    f = _one(run, n, 'coboundary')
    d = json.load(open(f))
    par = _check_basis(run, n, d, 'coboundary')
    C = d['coboundary_structure']
    L = C['linear_map']
    decl = list(L['parameter_labels'])
    if any('__' in x for x in par):
        raise ValueError('%s: a basis label contains "__"' % run)
    neven = sum(1 for v in par.values() if v == 0)
    nodd = len(par) - neven
    if len(decl) != len(set(decl)) or len(decl) != L['parameters_count'] or len(decl) != 2 * neven * nodd:
        raise ValueError('%s n=%d: phi declaration count %d / %r / %d'
                         % (run, n, len(decl), L['parameters_count'], 2 * neven * nodd))
    for lab in decl:
        m = re.fullmatch(r'phi_(.+)__(.+)', lab)
        if not m or m[1] not in par or m[2] not in par or par[m[1]] == par[m[2]]:
            raise ValueError('%s: declared phi label %r is not phi_<out>__<in> with opposite parity' % (run, lab))
    rows = C['coboundary_constants']
    if C['statistics']['total_coboundary_terms'] != len(rows):
        raise ValueError('%s n=%d: statistics.total_coboundary_terms %r != %d rows'
                         % (run, n, C['statistics']['total_coboundary_terms'], len(rows)))
    D, dup, used = _parse(run, n, rows, par, str)
    if not used <= set(decl):
        raise ValueError('%s: undeclared phi labels: %s' % (run, sorted(used - set(decl))[:5]))
    note = '%d declared phi labels, %d used' % (len(decl), len(used))
    return D, dict(file=os.path.basename(f), list_path='.coboundary_structure.coboundary_constants',
                   entries=len(rows), encoding='one row per (X,Y,Z,param,coeff)', phi_labels=note,
                   duplicate_rows=dup)


def evaluated_info(run, n):
    out = []
    for f in _data(run, n, 'C_%d_evaluated*.json'):
        d = json.load(open(f))
        _check_basis(run, n, d, 'evaluated')
        E = d.get('evaluated_deformation')
        if E is not None and E['statistics']['total_evaluated_gamma_terms'] != len(E['evaluated_gamma_constants']):
            raise ValueError('%s n=%d: evaluated statistics mismatch' % (run, n))
        for p, l in entry_lists(d):
            out.append(dict(list_path=os.path.basename(f) + ':' + p, entries=len(l),
                            keys=sorted({k for e in l for k in e})))
    return out
