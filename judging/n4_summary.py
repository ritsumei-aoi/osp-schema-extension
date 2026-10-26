#!/usr/bin/env python3
"""n4_summary.py — one row per run from judging/n4/*.jsonl (the n = 4 reusability check,
spec n4_spec.md), with a normalized comparison class. Facts only.

Columns: run, model, condition, n4_method (unmodified / range-edit / needs-code-change /
no-code / excluded / ...), ran_ok (exit 0 and not timed out), timed_out, seconds,
vs_ref_class, vs_ref (the agent's text), needs, edit_summary, source_file;
gcheck_n4_* columns are added from gcheck n = 4 results when present
(results_n4_<run>.json in $G4, see timing of the n = 4 gcheck in README).
vs_ref_class (mechanical, from the agent's n4_vs_reference text):
  match            text starts with "match" and does not say "not comparable"
  partial-match    text starts with "match" but says ranks were not computed / not comparable
  mismatch         text starts with "mismatch"
  not-comparable   anything else (no numbers produced, timed out, no code, ...)

Usage: python3 judging/n4_summary.py [G4_DIR]   (writes judging/n4_summary.csv and .md)
"""
import csv
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def vclass(t):
    t = (t or '').strip().lower()
    if t.startswith('mismatch'):
        return 'mismatch'
    if t.startswith('match'):
        if re.search(r'not comparable|no rank|rank a not|not computed', t):
            return 'partial-match'
        return 'match'
    return 'not-comparable'


def gcheck_cols(g4, run):
    if not g4:
        return {}
    f = Path(g4) / ('results_n4_%s.json' % run)
    if not f.exists():
        return {}
    res = json.load(open(f))[0]
    if 'error' in res:
        return dict(gcheck_n4='error: ' + res['error'][:120])
    out = dict(gcheck_n4='ok')
    for k in ('cmp', 'ranks', 'rank'):
        pass
    txt = json.dumps(res, default=str)
    m = re.search(r'"worker_A__worker_G_nonK": \{[^}]*"A": (\d+)[^}]*"AG": (\d+)', txt)
    if m:
        out['gcheck_n4_own_rank_nonK'] = '%s->%s' % (m.group(1), m.group(2))
    return out


def main():
    g4 = sys.argv[1] if len(sys.argv) > 1 else None
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    rows = []
    for f in sorted(glob.glob(str(HERE / 'n4' / '*.jsonl'))):
        for line in open(f):
            if not line.strip():
                continue
            d = json.loads(line)
            run = d['run']
            ran = d.get('exit_code') == 0 and not d.get('timed_out')
            rows.append(dict(run=run, model=inv.get(run, {}).get('model', ''), condition=inv.get(run, {}).get('condition', d.get('condition', '')),
                             n4_method=d.get('n4_method', ''), ran_ok=int(bool(ran)) if d.get('command') else '',
                             timed_out=int(bool(d.get('timed_out'))), seconds=d.get('seconds', ''),
                             vs_ref_class=vclass(d.get('n4_vs_reference')) if d.get('n4_method') != 'excluded' else 'excluded',
                             vs_ref=' '.join(str(d.get('n4_vs_reference', '')).split())[:300],
                             needs=' '.join(str(d.get('needs', '')).split())[:200],
                             edit_summary=' '.join(str(d.get('edit_summary', '')).split())[:200],
                             source_file='n4/' + Path(f).name, **gcheck_cols(g4, run)))
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(HERE / 'n4_summary.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, restval='')
        w.writeheader()
        w.writerows(rows)
    # Markdown: counts by condition group
    grp = lambda c: 'May' if c.startswith('May') else c
    by = defaultdict(Counter)
    for r in rows:
        by[grp(r['condition'])][r['n4_method']] += 1
        by[grp(r['condition'])]['cls:' + r['vs_ref_class']] += 1
        by[grp(r['condition'])]['timed_out'] += int(r['timed_out'] or 0)
    methods = ['unmodified', 'range-edit', 'needs-code-change', 'no-code', 'excluded']
    classes = ['match', 'partial-match', 'mismatch', 'not-comparable']
    L = ['# n = 4 reusability (n4_summary.csv, generated)', '',
         '| condition | runs | ' + ' | '.join(methods) + ' | timed out | ' + ' | '.join(classes) + ' |',
         '|---|---:|' + '---:|' * (len(methods) + 1 + len(classes))]
    for c in sorted(by):
        n = sum(by[c][m] for m in methods) + sum(v for k, v in by[c].items() if k not in methods and not k.startswith('cls:') and k != 'timed_out')
        L.append('| %s | %d | %s | %d | %s |' % (c, n, ' | '.join(str(by[c][m]) for m in methods), by[c]['timed_out'],
                                               ' | '.join(str(by[c]['cls:' + k]) for k in classes)))
    (HERE / 'n4_summary.md').write_text('\n'.join(L) + '\n')
    print('wrote n4_summary.csv/.md', len(rows))


if __name__ == '__main__':
    main()
