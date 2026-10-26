#!/usr/bin/env python3
"""manager_review_summary.py — per-run summary of judging/manager_review/*.jsonl
(manager_review_spec.md, author 2026-10-12). Facts only; descriptive.

The six group files were written by subagents that drew the M1 / M2 line slightly differently
(some put "opened the file but did not check" under M1, others under M2 with true_by_sources = no),
so the comparable measure is `wrong` = M1-false + M2-unverified with true_by_sources = no.
Missed errors are counted once per run (distinct error_trace ids E1-*/E2-*; scribe observations
'scribe:*' / 'scribe-obs' / 'S-*' are counted apart, since some are reading remarks, not errors).

manager_review_summary.csv (one row per run):
  run, condition, worker_model, memos, memos_sent, claims, M1, M2, M2_false, M2_true, M2_undetermined,
  M3, wrong (M1 + M2_false), wrong_in_sent (claims of sent drafts or their summaries), errors_in_run
  (error_trace_summary n_E1 + n_E2 of the run; for fix trials, of the original run that was fixed), missed_distinct (error_trace ids not
  mentioned while approving), missed_opened (of those, the Manager opened the file), scribe_obs,
  read_source
  plus origin x direction counts of the wrong claims (second pass)
manager_review_summary.md: per-condition totals, origin x direction, and the wrong claims with quotes.

Second pass (author 2026-10-12, spec section "Second pass"): manager_review/adjustments_*.jsonl give
new_kind (M1 only when the claim contradicts what the Manager opened in that session), origin
(endorse-worker / manager-originated / from-human-facts) and direction (false-accept / false-reject /
other) for every M1, M2 (true_by_sources = no) and M3 claim. They are applied on top of the group
files (kept as written), matched by run, memo and the first 60 characters of the quote.

Usage: python3 judging/manager_review_summary.py
"""
import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent


def tbs(c):
    v = str(c.get('true_by_sources', '')).strip().lower()
    return v.split(':')[0].split()[0] if v else ''


def is_sent(o):
    return str(o.get('sent', '')).lower().startswith('yes')


def akey(run, memo, quote):
    return (run, str(memo).lstrip('0'), ' '.join(str(quote).split())[:60])


def main():
    adj = {}
    for f in sorted((HERE / 'manager_review').glob('adjustments_*.jsonl')):
        for ln in open(f):
            if ln.strip():
                a = json.loads(ln)
                adj[akey(a['run'], a['memo'], a['quote'])] = a
    used = set()
    od = defaultdict(lambda: defaultdict(int))
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    ets = {r['run']: r for r in csv.DictReader(open(HERE / 'error_trace_summary.csv'))}
    per = defaultdict(lambda: dict(memos=0, memos_sent=0, claims=0, M1=0, M2=0, M2_false=0, M2_true=0,
                                   M2_undetermined=0, M3=0, wrong_in_sent=0, missed=set(), missed_opened=set(),
                                   scribe=set(), read_source='', wrong=[]))
    for f in sorted((HERE / 'manager_review').glob('*.jsonl')):
        if f.name.startswith('adjustments_'):
            continue
        for ln in open(f):
            if not ln.strip():
                continue
            o = json.loads(ln)
            p = per[o['run']]
            p['fix'] = f.stem.startswith('fix')
            p['memos'] += 1
            p['memos_sent'] += int(is_sent(o))
            if o.get('run_summary'):
                p['read_source'] = str(o['run_summary'].get('read_source', ''))
            for c in o.get('claims') or []:
                p['claims'] += 1
                k = str(c.get('kind', ''))
                a = adj.get(akey(o['run'], o['memo'], c.get('quote', '')))
                if a:
                    used.add(akey(a['run'], a['memo'], a['quote']))
                    k = a['new_kind']
                    c = dict(c, true_by_sources=a['true_by_sources'])
                    cond = 'fix' if f.stem.startswith('fix') else inv.get(o['run'], {}).get('condition', '')
                    if k.startswith(('M1', 'M2')) or str(a['true_by_sources']).startswith(('no', 'partly')):
                        od[cond][(a['origin'], a['direction'])] += 1
                wrong = False
                if k.startswith('M1'):
                    p['M1'] += 1
                    wrong = True
                elif k.startswith('M2'):
                    p['M2'] += 1
                    t = tbs(c)
                    key = {'no': 'M2_false', 'yes': 'M2_true'}.get(t, 'M2_undetermined')
                    p[key] += 1
                    wrong = t == 'no'
                elif k.startswith('M3'):
                    p['M3'] += 1
                if wrong:
                    p['wrong_in_sent'] += int(is_sent(o))
                    p['wrong'].append((o['memo'], o.get('issue', ''), k.split('-')[0], is_sent(o),
                                       str(c.get('quote', ''))[:160], str(c.get('loc', ''))[:80]))
            for m in o.get('missed') or []:
                e = str(m.get('error_id', ''))
                if e.startswith(('E1', 'E2')):
                    eid = e.split()[0]
                    p['missed'].add(eid)
                    if str(m.get('opened_by_manager', '')).lower().startswith('yes'):
                        p['missed_opened'].add(eid)
                else:
                    p['scribe'].add(e[:60])
    unmatched = [k for k in adj if k not in used]
    if unmatched:
        print('WARNING: %d adjustments not matched:' % len(unmatched), unmatched[:5])
    rows = []
    for run, p in sorted(per.items()):
        i = inv.get(run, {})
        fix = p.get('fix', False)
        cond = ('fix-' + run.rsplit('-', 1)[1]) if fix else i.get('condition', '')
        e = ets.get(run)
        rows.append(dict(run=run, condition=cond, worker_model=i.get('model', ''), memos=p['memos'],
                         memos_sent=p['memos_sent'], claims=p['claims'], M1=p['M1'], M2=p['M2'],
                         M2_false=p['M2_false'], M2_true=p['M2_true'], M2_undetermined=p['M2_undetermined'],
                         M3=p['M3'], wrong=p['M1'] + p['M2_false'], wrong_in_sent=p['wrong_in_sent'],
                         errors_in_run=int(e['n_E1']) + int(e['n_E2']) if e else '',
                         missed_distinct=len(p['missed']), missed_opened=len(p['missed_opened']),
                         scribe_obs=len(p['scribe']), read_source=p['read_source']))
    with open(HERE / 'manager_review_summary.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    commit = subprocess.run(['git', '-C', str(REV), 'rev-parse', '--short', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    order = {'A1': 0, 'A2': 1, 'F': 2, 'fix-C': 3, 'fix-G': 4, 'fix': 5}
    cols = ['memos', 'memos_sent', 'claims', 'M1', 'M2', 'M2_false', 'M2_true', 'M2_undetermined', 'M3',
            'wrong', 'wrong_in_sent', 'missed_distinct', 'missed_opened']
    with open(HERE / 'manager_review_summary.md', 'w') as fh:
        fh.write('# Manager review summary\n\nGenerated by manager_review_summary.py at %s from manager_review/*.jsonl '
                 '(spec: manager_review_spec.md). wrong = M1-false + M2-unverified with true_by_sources = no '
                 '(comparable across the group files). missed = distinct error_trace ids not mentioned while '
                 'approving. Descriptive only.\n\n' % commit)
        fh.write('| run | condition | worker | errors_in_run | ' + ' | '.join(cols) + ' |\n|' + '---|' * (len(cols) + 4) + '\n')
        for r in sorted(rows, key=lambda r: (order.get(r['condition'], 9), r['run'])):
            fh.write('| %s | %s | %s | %s | ' % (r['run'].replace('thm01-R-', ''), r['condition'], r['worker_model'],
                                                 r['errors_in_run']) + ' | '.join(str(r[c]) for c in cols) + ' |\n')
        tot = defaultdict(lambda: defaultdict(int))
        for r in rows:
            for c in cols:
                tot[r['condition']][c] += r[c]
        fh.write('\n## Totals by condition\n\n| condition | ' + ' | '.join(cols) + ' |\n|' + '---|' * (len(cols) + 1) + '\n')
        for cond in sorted(tot, key=lambda c: order.get(c, 9)):
            fh.write('| %s | ' % cond + ' | '.join(str(tot[cond][c]) for c in cols) + ' |\n')
        fh.write('\n## Origin x direction of the wrong claims (second pass)\n\nM1 + M2 (true_by_sources = no) + M3 that a '
                 'source contradicts (no / partly).\n\n| condition | origin | direction | n |\n|---|---|---|---|\n')
        for cond in sorted(od, key=lambda c: order.get(c, 9)):
            for (o_, d_), n in sorted(od[cond].items(), key=lambda kv: -kv[1]):
                fh.write('| %s | %s | %s | %d |\n' % (cond, o_, d_, n))
        fh.write('\n## Wrong claims (M1, and M2 with true_by_sources = no)\n\n')
        for run, p in sorted(per.items()):
            if not p['wrong']:
                continue
            fh.write('### %s\n\n' % run)
            for memo, issue, k, s, q, loc in p['wrong']:
                fh.write('- memo %s (%s, %s, %s): "%s" — %s\n' % (memo, issue, k, 'sent' if s else 'not sent', q, loc))
            fh.write('\n')
    print('wrote manager_review_summary.csv/.md', len(rows))


if __name__ == '__main__':
    main()
