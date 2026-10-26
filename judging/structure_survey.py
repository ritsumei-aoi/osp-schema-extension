#!/usr/bin/env python3
"""structure_survey.py — how structured (machine-readable) are the data each run
left? Mechanical survey of the JSON files in the final copy, split into
(1) ordinary Lie superalgebra information and (2) deformation information.
Facts / heuristics only; no judgment.

Lie superalgebra part (per run):
  lie_basis        basis list given (key 'basis' or 'generators' with names)
  lie_parity       parity of each generator given (dict or field)
  lie_realization  oscillator realization of the generators given
  lie_sc           structure constants as machine-readable rows/dict
                   (X, Y -> Z, coefficient), not prose
  lie_sc_n         for which n structure constants are present (from file names)
Deformation part:
  def_params       gb parameters declared as data (list / matrix of labels)
  def_kappa_K      kappa and/or K declared as data (key names)
  def_gamma        γ as machine-readable rows/dict symbolic in gb (one entry per
                   (X,Y,Z) with gb labels)
  def_gamma_numeric_only  γ only for numeric profiles (evaluated), no symbolic gb
  def_coboundary   δf as rows/dict with labelled map parameters (phi / f_...)
  def_result       triviality result as data (rank / trivial / conclusion keys)
  def_n            for which n deformation data are present
Common:
  json_files, exact_strings (coefficients stored as strings such as "-1/2"),
  floats (coefficients stored as floats), same_keys_across_n (the n = 1, 2, 3
  files of the same kind have the same top-level keys), schema_doc (a document
  in the run, outside the kit, that specifies the JSON format)

Usage: JROOT=<scratchpad>/jroot python3 judging/structure_survey.py
"""
import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
JROOT = Path(os.environ['JROOT'])
KIT = ('handover/', 'docs/math/', '.github/')
GB = re.compile(r'\bgb[_a-zA-Z0-9]*|\bgb\{')                 # case-sensitive: gb labels
PHI = re.compile(r'\bphi|\bf_\d|\bf\[|map_param|\bpsi')        # lower-case: map parameters (F_ = generators)


def keyed(d, words, exclude=()):
    """True if some key contains one of `words` (and none of `exclude`) and holds a non-empty dict/list."""
    for pth, v in walk(d):
        if isinstance(v, dict):
            for k, w in v.items():
                kl = str(k).lower()
                if any(x in kl for x in words) and not any(x in kl for x in exclude) \
                        and isinstance(w, (dict, list)) and len(w) >= 3:
                    return True
    return False
NFILE = re.compile(r'(?:^|[_/-])(?:C_?|n_?|n=)?([1-4])(?:_|\.json|$)', re.I)


def walk(o, path=''):
    yield path, o
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + '.' + str(k))
    elif isinstance(o, list):
        for v in o[:2000]:
            yield from walk(v, path + '[]')


def row_lists(o):
    """lists of dicts that look like bracket rows (two operands + target/coefficient)."""
    out = []
    for p, v in walk(o):
        if isinstance(v, list) and v and isinstance(v[0], dict):
            keys = {k.lower() for k in v[0]}
            ops = keys & {'x', 'y', 'a', 'b', 'left', 'right', 'generators', 'pair', 'g1', 'g2', 'x1', 'x2'}
            tgt = keys & {'z', 'c', 'target', 'result', 'coeff', 'coefficient', 'value', 'terms', 'bracket',
                          'linear_combination', 'gamma', 'gamma_value', 'delta_f_value', 'coeff_gb', 'coeff_phi'}
            if ops and tgt:
                out.append((p, v))
    return out


def dict_brackets(o):
    """dicts keyed like '[X,Y]' or 'X,Y' with values -> bracket tables."""
    n = 0
    for p, v in walk(o):
        if isinstance(v, dict) and len(v) >= 3:
            ks = list(v)[:20]
            if sum(1 for k in ks if re.match(r'^\[?[A-Za-z][\w{}^+-]*\s*,\s*[A-Za-z][\w{}^+-]*\]?$', str(k))) >= len(ks) * 0.6:
                n += 1
    return n


def coeff_kinds(o):
    s = f = 0
    for p, v in walk(o):
        last = p.rsplit('.', 1)[-1].lower()
        if 'coeff' in last or last in ('value', 'c', 'coefficient'):
            if isinstance(v, str) and re.match(r'^-?\d+(/\d+)?$', v.strip()):
                s += 1
            elif isinstance(v, float):
                f += 1
    return s, f


def n_of(path, d=None):
    """n of a data file: the JSON's own top-level n if given, else the last n-like token of the file name."""
    if isinstance(d, dict):
        v = d.get('n') or (d.get('algebra') or {}).get('n') if isinstance(d.get('algebra', {}), dict) else d.get('n')
        if isinstance(v, int) and 1 <= v <= 9:
            return str(v)
    name = path.rsplit('/', 1)[-1]
    hits = re.findall(r'(?:C_|_n|^n|C\(|_)(\d)(?=[_.)]|$)', name)
    return hits[-1] if hits else None


def survey(root):
    res = defaultdict(int)
    lie_n, def_n = set(), set()
    keys_by_kind_n = defaultdict(dict)
    files = [p for p in sorted(root.rglob('*.json'))
             if not p.relative_to(root).as_posix().startswith(KIT) and 'node_modules' not in str(p)]
    res['json_files'] = len(files)
    for p in files:
        rel = p.relative_to(root).as_posix()
        try:
            d = json.loads(p.read_text(errors='replace'))
        except Exception:
            res['unparsable'] += 1
            continue
        txt = json.dumps(d)[:2_000_000]
        keys = {str(k).lower() for pth, v in walk(d) if isinstance(v, dict) for k in v}
        n = n_of(rel, d)
        if 'basis' in keys or 'generators' in keys or 'even' in keys and 'odd' in keys:
            res['lie_basis'] += 1
        if 'parity' in keys or any('parity' in k for k in keys):
            res['lie_parity'] += 1
        if any('realiz' in k for k in keys) or re.search(r'"a_1_[pm]"|"b_\d_[pm]"|a\^\+|b_1\^', txt):
            res['lie_realization'] += 1
        rows = row_lists(d)
        dbr = dict_brackets(d)
        has_gb = bool(GB.search(txt))
        has_phi = bool(PHI.search(txt))
        sc_rows = [r for pth, r in rows if not GB.search(json.dumps(r[:50])) and not PHI.search(json.dumps(r[:50]))]
        gamma_rows = [r for pth, r in rows if GB.search(json.dumps(r[:50]))]
        cob_rows = [r for pth, r in rows if PHI.search(json.dumps(r[:50])) and not GB.search(json.dumps(r[:50]))]
        kind = None
        sc_key = keyed(d, ('structure_const', 'brackets', 'bracket_table', 'commutator'), ('gamma', 'deform', 'evaluat', 'scalar'))
        gamma_key = keyed(d, ('gamma',), ('evaluat',))
        cob_key = keyed(d, ('coboundary', 'delta_f', 'deltaf'), ())
        if sc_key and not ('evaluat' in rel.lower()):
            res['lie_sc'] += 1
            kind = 'structure'
            if n:
                lie_n.add(n)
            sc_rows = []
        if gamma_key and not gamma_rows:
            gamma_rows = [1]
        if cob_key and not cob_rows:
            cob_rows = [1]
        if sc_rows or (dbr and not has_gb and not has_phi and kind is None):
            if 'evaluat' in rel.lower() or 'profile' in txt.lower() and 'gb' in rel.lower():
                res['def_gamma_numeric_only'] += 1
                kind = 'evaluated'
            else:
                res['lie_sc'] += 1
                kind = 'structure'
                if n:
                    lie_n.add(n)
        if gamma_rows or (dbr and has_gb and not has_phi):
            res['def_gamma'] += 1
            kind = 'gamma'
            if n:
                def_n.add(n)
        if cob_rows or (dbr and has_phi):
            res['def_coboundary'] += 1
            kind = kind or 'coboundary'
            if n:
                def_n.add(n)
        if re.search(r'"gb[_a-z0-9]*"\s*:|gb_matrix|gb_params|deformation_parameters|"parameters"', txt, re.I):
            res['def_params'] += 1
        if re.search(r'"kappa"|"k"\s*:|central_elements|"K"', txt):
            res['def_kappa_K'] += 1
        if re.search(r'"rank[\w_]*"\s*:\s*\d|"(is_)?trivial[\w_]*"\s*:|"conclusion"\s*:|"triviality', txt, re.I):
            res['def_result'] += 1
        s, f = coeff_kinds(d)
        res['exact_strings'] += s
        res['floats'] += f
        if kind and n:
            keys_by_kind_n[kind][n] = tuple(sorted(d.keys())) if isinstance(d, dict) else ('<list>',)
    same = [len(set(v.values())) == 1 for k, v in keys_by_kind_n.items() if len(v) >= 2]
    res['same_keys_across_n'] = '' if not same else int(all(same))
    res['lie_sc_n'] = ''.join(sorted(lie_n))
    res['def_n'] = ''.join(sorted(def_n))
    doc = 0
    for p in root.rglob('*.md'):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(KIT) or 'template' in rel:
            continue
        t = p.read_text(errors='replace')
        if re.search(r'schema', t, re.I) and re.search(r'"\w+"\s*:', t) and re.search(r'json', t, re.I):
            doc = 1
            break
    res['schema_doc'] = doc
    return res


def main():
    inv = list(csv.DictReader(open(HERE / 'inventory.csv')))
    rows = []
    for r in inv:
        root = JROOT / 'final' / r['run']
        if not root.exists():
            continue
        s = survey(root)
        rows.append(dict(run=r['run'], model=r['model'], condition=r['condition'], exclude=r['exclude'], **s))
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(HERE / 'structure_survey.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, restval=0)
        w.writeheader()
        w.writerows(rows)
    print('wrote structure_survey.csv', len(rows))


if __name__ == '__main__':
    main()
