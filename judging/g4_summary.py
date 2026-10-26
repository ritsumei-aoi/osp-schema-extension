#!/usr/bin/env python3
"""g4_summary.py — γ / rank check at n = 4 on the C_4 data the runs' own code produced
in the n = 4 reusability check (judging/n4/, copies in the scratchpad n4work/).
Facts only. Same columns and cell formats as g_summary.py (n = 1, 2), for n = 4,
plus the n <= 3 data_implies from g_summary.csv for comparison.

Input: gcheck/results_n4/results_n4_<run>.json (one per run; produced by
  FG_ROOT=<scratchpad>/n4work RESULTS_TAG=<run> python3 gcheck/analyze.py 4 --runs <run>,
  timeout 1800 s per run, 2026-10-08).
Reference at n = 4 (independent_triviality4.py): rank A 1168; [A|G] 1168 (κ supercommuting,
K dropped) or 1184 (otherwise).
A run whose C_4 files were missing or unreadable has an error cell.

Usage: python3 judging/g4_summary.py   (writes judging/g4_summary.csv and .md)
"""
import csv
import json
import subprocess
from pathlib import Path

from g_summary import gamma_cell, rank_cell, implies

HERE = Path(__file__).resolve().parent
R4 = HERE / 'gcheck' / 'results_n4'


def main():
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    g123 = {r['run']: r for r in csv.DictReader(open(HERE / 'g_summary.csv'))}
    n4 = {r['run']: r for r in csv.DictReader(open(HERE / 'n4_summary.csv'))}
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=HERE, capture_output=True, text=True).stdout.strip()
    rows = []
    for f in sorted(R4.glob('results_n4_*.json')):
        r = json.load(open(f))[0]
        run = r['run']
        i = inv.get(run, {})
        row = dict(run=run, model=i.get('model', ''), condition=i.get('condition', ''), exclude=i.get('exclude', ''),
                   n4_method=n4.get(run, {}).get('n4_method', ''), n4_agent_vs_ref=n4.get(run, {}).get('vs_ref_class', ''))
        if 'error' in r:
            row['error_n4'] = r['error'][:200]
        else:
            row['sc_n4'] = r['structure_constants_vs_realization']['rel']
            g = r.get('gamma_cmp') or {}
            if not g:
                gi = r.get('gamma_file')
                row['gamma_n4'] = 'unreadable: %s' % (gi.get('reason', gi) if isinstance(gi, dict) else gi)
            else:
                row['gamma_n4'] = gamma_cell(g, False)
                row['gammaK_n4'] = gamma_cell(g, True)
            rk = r.get('rank', {})
            row['rank_nonK_n4'] = rank_cell(rk.get('ref_A__worker_G_nonK'))
            row['rank_K_n4'] = rank_cell(rk.get('ref_A__worker_G_K'))
            row['ownA_nonK_n4'] = rank_cell(rk.get('worker_A__worker_G_nonK'))
            row['ownA_K_n4'] = rank_cell(rk.get('worker_A__worker_G_K'))
            row['data_implies_n4'] = '%s / %s' % (implies(rk.get('ref_A__worker_G_nonK')) or '-',
                                                  implies(rk.get('ref_A__worker_G_K')) or '-')
            row['coboundary_phi_columns_n4'] = r.get('coboundary_phi_columns', '')
        row['data_implies_n1'] = g123.get(run, {}).get('data_implies_n1', '')
        row['data_implies_n2'] = g123.get(run, {}).get('data_implies_n2', '')
        row['same_as_n12'] = ('' if 'data_implies_n4' not in row or not row['data_implies_n1'] else
                              int(row['data_implies_n4'] == row['data_implies_n1'] == row['data_implies_n2']))
        row['script_commit'] = commit
        rows.append(row)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(HERE / 'g4_summary.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, restval='')
        w.writeheader()
        w.writerows(rows)
    md = ['# γ / rank at n = 4 on the runs\' own C_4 data (g4_summary.py; facts only)', '',
          'Reference n = 4: rank A 1168; [A|G] 1168 (κ supercommuting, K dropped) or 1184 (otherwise). Script version %s.' % commit, '',
          '| run | cond | n4 method | sc n4 | gamma n4 (nonK) | gamma n4 (K) | ranks n4 (ref A) nonK / K | own A nonK | implies n4 (K dropped / kept) | same as n=1,2 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        md.append('| %s | %s | %s | %s | %s | %s | %s / %s | %s | %s | %s |' % (
            r['run'].replace('thm01-R-', ''), r['condition'], r['n4_method'], r.get('sc_n4', r.get('error_n4', '')),
            r.get('gamma_n4', ''), r.get('gammaK_n4', ''), r.get('rank_nonK_n4', ''), r.get('rank_K_n4', ''),
            r.get('ownA_nonK_n4', ''), r.get('data_implies_n4', ''), r.get('same_as_n12', '')))
    (HERE / 'g4_summary.md').write_text('\n'.join(md) + '\n')
    print('wrote g4_summary.csv/.md', len(rows))


if __name__ == '__main__':
    main()
