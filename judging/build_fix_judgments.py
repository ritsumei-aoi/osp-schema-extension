#!/usr/bin/env python3
"""build_fix_judgments.py — creates fix_judgments.csv, the author's input file for the fixed versions of the
fix experiment (design §9.30, §9.52; author 2026-10-14, "k" to the recommended option A in the judging
session). One row per trial; the facts are the rows group = fix of verdict_basis.csv.

Columns: trial (1-8, the row order of runs/fix/results.tsv, as numbered in design §9.52), run,
  commit_checked ('fix final (<sha>)', as in verdict_basis.csv), base_commit (the commit the trial started
  from), original_predicted_verdict (frozen rules-v1 prediction of the original run's final commit, for
  reference; there is no prediction of the fixed version), then the author's columns as in judgments.csv:
  author_verdict, author_result, author_argument, author_interpretation, author_note (codes: author_codes.py).
The file is created once; later runs only append rows for trials not yet in it and never change existing
rows (the author's entries are never rewritten).

Usage: python3 judging/build_fix_judgments.py
"""
import csv
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent
AUTHOR = ['author_verdict', 'author_result', 'author_argument', 'author_interpretation', 'author_note']
COLS = ['trial', 'run', 'commit_checked', 'base_commit', 'original_predicted_verdict'] + AUTHOR


def main():
    # committed version only (runs/fix is written by the fix-experiment session)
    tsv = subprocess.run(['git', '-C', str(REV), 'show', 'HEAD:./runs/fix/results.tsv'],
                         capture_output=True, text=True, check=True).stdout
    trials = list(csv.DictReader(tsv.splitlines(), delimiter='\t'))
    vb = {r['run']: r['commit_checked'] for r in csv.DictReader(open(HERE / 'verdict_basis.csv'))
          if r['group'] == 'fix'}
    pred = {r['run']: r['predicted_verdict'] for r in csv.DictReader(open(HERE / 'judgments.csv'))
            if r['commit_checked'] == 'final'}
    out = HERE / 'fix_judgments.csv'
    rows = list(csv.DictReader(open(out))) if out.exists() else []
    have = {r['run'] for r in rows}
    added = 0
    for i, t in enumerate(trials, 1):
        if t['run'] in have:
            continue
        cc = vb.get(t['run'])
        if not cc or t['final'] not in cc:
            raise SystemExit('verdict_basis.csv has no fix row for %s at %s' % (t['run'], t['final']))
        rows.append(dict(trial=str(i), run=t['run'], commit_checked=cc, base_commit=t['base'],
                         original_predicted_verdict=pred.get(t['run'], ''), **{c: '' for c in AUTHOR}))
        added += 1
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows({k: r.get(k, '') for k in COLS} for r in rows)
    print('wrote fix_judgments.csv: %d rows (%d added)' % (len(rows), added))


if __name__ == '__main__':
    main()
