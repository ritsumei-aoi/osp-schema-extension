#!/usr/bin/env python3
"""g_summary.py — one row per run (runs with generator realizations: G, A, F,
May-Iterative) from gcheck/results_n1.json and results_n2.json.

Facts only. Column meanings:
- sc_nN: Worker's undeformed structure constants vs those computed from its own
  realization (identical / different / worker empty).
- gamma_nN: relation of the Worker's gamma (entries with Z != K) to the two
  references: 'none' = kappa commutes (gb odd, no sign), 'super' = kappa
  supercommutes (gb even). "=none" identical, "-none" overall sign flipped,
  "~none m/r" closest reference with m of r reference entries matched.
- gammaK_nN: same for the K entries ("not recorded" if the Worker has none).
- rank_nonK_nN / rank_K_nN: rank A -> rank [A|G] with the independent coboundary
  A and the Worker's gamma, K rows dropped / kept, and how many gb directions are
  individually trivial. A == [A|G] means the Worker's gamma is a coboundary
  (deformation trivial for all gb) under that treatment of K.
- ownA_nN: the same ranks with the Worker's own coboundary matrix (if it has one).
- data_implies_nN: the conclusion the Worker's own gamma implies, for K dropped /
  K kept ("all gb trivial" if A == [A|G], "trivial iff gb=0" if every direction
  raises the rank, otherwise "partial").
The Worker's stated conclusion and reading are filled in separately.

Usage: python3 judging/g_summary.py   (writes judging/g_summary.csv and .md)
"""
import csv
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rel(cmp, tag):
    """Short relation of Worker gamma to reference 'tag' entries."""
    c = cmp.get(tag)
    if not c:
        return None
    t = c['total']
    rels = c['relations']
    if t['worker'] == 0:
        return ('empty', 0, t['ref'])
    if rels == ['identical']:
        return ('=', t['match'], t['ref'])
    if rels == ['negated']:
        return ('-', t['match'], t['ref'])
    return ('~', t['match'], t['ref'])


def gamma_cell(cmp, withK):
    k = 'K' if withK else 'nonK'
    best = None
    for ref in ('none', 'super'):
        r = rel(cmp, '%s_%s' % (ref, k))
        if r is None:
            continue
        if r[0] == 'empty':
            return 'not recorded'
        if r[0] in ('=', '-'):
            return '%s%s' % (r[0], ref)
        # negated relation per param may be reported as 'different' when mixed;
        # check full negation via counts
        tot = cmp['%s_%s' % (ref, k)]['total']
        if tot['differ'] == tot['differ_negated'] and tot['differ'] == tot['ref'] and not tot['missing'] and not tot['extra']:
            return '-%s' % ref
        score = r[1]
        if best is None or score > best[1]:
            best = (ref, score, r[2], tot)
    if best is None:
        return 'unreadable'
    ref, m, r, tot = best
    return '~%s %d/%d (miss %d, extra %d, diff %d of which neg %d)' % (
        ref, m, r, tot['missing'], tot['extra'], tot['differ'], tot['differ_negated'])


def rank_cell(rk):
    if not rk:
        return ''
    nd = len(rk['per_direction_increase'])
    return '%d->%d (%d/%d dirs trivial)' % (rk['rankA'], rk['rankAG'], rk['n_dirs_trivial'], nd)


def implies(rk):
    if not rk:
        return ''
    nd = len(rk['per_direction_increase'])
    if rk['rankAG'] == rk['rankA']:
        return 'all gb trivial'
    if rk['n_dirs_trivial'] == 0 and rk['rankAG'] - rk['rankA'] == nd:
        return 'trivial iff gb=0'
    return 'partial'


def main():
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    res = {n: {r['run']: r for r in json.load(open(HERE / 'gcheck' / ('results_n%d.json' % n)))} for n in (1, 2)}
    runs = [r for r in inv if r in res[1]]
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=HERE, capture_output=True, text=True).stdout.strip()
    rows = []
    for run in runs:
        i = inv[run]
        row = dict(run=run, group=i['group'], model=i['model'], condition=i['condition'],
                   status=i['status'], exclude=i['exclude'], commit=i['commit_final'])
        for n in (1, 2):
            r = res[n].get(run, {})
            if 'error' in r:
                row['error_n%d' % n] = r['error'][:200]
                continue
            row['sc_n%d' % n] = r['structure_constants_vs_realization']['rel']
            g = r.get('gamma_cmp') or {}
            if not g:
                gi = r.get('gamma_file')
                row['gamma_n%d' % n] = 'unreadable: %s' % (gi.get('reason', gi) if isinstance(gi, dict) else gi)
            else:
                row['gamma_n%d' % n] = gamma_cell(g, False)
                row['gammaK_n%d' % n] = gamma_cell(g, True)
            rk = r.get('rank', {})
            row['rank_nonK_n%d' % n] = rank_cell(rk.get('ref_A__worker_G_nonK'))
            row['rank_K_n%d' % n] = rank_cell(rk.get('ref_A__worker_G_K'))
            row['ownA_nonK_n%d' % n] = rank_cell(rk.get('worker_A__worker_G_nonK'))
            row['ownA_K_n%d' % n] = rank_cell(rk.get('worker_A__worker_G_K'))
            row['data_implies_n%d' % n] = '%s / %s' % (implies(rk.get('ref_A__worker_G_nonK')) or '-',
                                                       implies(rk.get('ref_A__worker_G_K')) or '-')
            row['antisym_conflicts_n%d' % n] = r.get('gamma_antisym_conflicts', '')
        row['script_commit'] = commit
        rows.append(row)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(HERE / 'g_summary.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    md = ['# G/A/F checks (generated by g_summary.py; facts only)', '',
          'See the docstring of g_summary.py for column meanings. Script version: %s.' % commit, '',
          '| run | cond | sc n1 | gamma n1 (nonK) | gamma n1 (K) | ranks n1 nonK / K | implies n1 (K dropped / kept) | gamma n2 | implies n2 |',
          '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        md.append('| %s | %s | %s | %s | %s | %s / %s | %s | %s | %s |' % (
            r['run'].replace('thm01-R-', ''), r['condition'], r.get('sc_n1', r.get('error_n1', '')),
            r.get('gamma_n1', ''), r.get('gammaK_n1', ''), r.get('rank_nonK_n1', ''), r.get('rank_K_n1', ''),
            r.get('data_implies_n1', ''), r.get('gamma_n2', r.get('error_n2', '')), r.get('data_implies_n2', '')))
    (HERE / 'g_summary.md').write_text('\n'.join(md) + '\n')
    print('wrote g_summary.csv/.md', len(rows), 'runs')


if __name__ == '__main__':
    main()
