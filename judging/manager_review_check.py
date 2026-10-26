#!/usr/bin/env python3
"""manager_review_check.py — the list of Manager claims the author checks before the counts are
used in the paper (design §9.53 (4), author 2026-10-12): every wrong claim of the gated runs
(M1, and M2 with true_by_sources = no, after the second pass) and a random sample of the claims
classed 'ok'. Facts only; the author fills the author_* columns (never written by scripts).

Sample of 'ok' claims: stratified by run (A1 / A2 / F− runs), ceil(OK_SHARE x ok claims of the run),
at least 2 per run, drawn with random.Random(SEED). The seed and share are fixed here so the
sample can be redrawn identically; the sample is drawn before the author sees any result of it.
Runs added later (not in FIRST_RUNS, e.g. thm01-R-gemini38f-r2-A1, lead request 2026-10-13) are drawn
after the first 14, each with its own random.Random('<SEED>:<run>'), so the sample of the first 14
runs stays exactly as drawn on 2026-10-12.
Also listed: set = 'm3_contradicted', additions (M3) that a source contradicts in part or whole (4 of the
7 false rejections counted in notes §4 are of this kind); set = 'm2_undetermined': M2 claims whose truth the sources could not settle, for
the author to decide if wanted.

Output manager_review_check.csv: check_id, set (wrong / m3_contradicted / ok_sample / m2_undetermined), run,
  condition, worker_model, memo, issue, draft_type, sent, kind, true_by_sources, origin,
  direction, quote, loc, evidence, note, group_file, author_agree (yes / no / unsure),
  author_kind, author_note
The file is created once; on later runs existing author_* values and check_id are kept (matched by
run, memo and the first 60 characters of the quote); claims new to the file get the next check_id.

Usage: python3 judging/manager_review_check.py
"""
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20261012
OK_SHARE = 0.10
GATED = ('A1', 'A2', 'F')
AUTHOR = ['author_agree', 'author_kind', 'author_note']
# The 14 gated runs of the first draw (2026-10-12); their sample uses one shared random.Random(SEED)
# in sorted order, as then.
FIRST_RUNS = ('thm01-R-luna-A', 'thm01-R-luna-A2', 'thm01-R-luna-F', 'thm01-R-luna-r2-A1', 'thm01-R-luna-r2-A2',
              'thm01-R-luna-r2-F', 'thm01-R-luna-r3-A1', 'thm01-R-sonnet46-A', 'thm01-R-sonnet46-A1',
              'thm01-R-sonnet46-F', 'thm01-R-sonnet46-r2-A1', 'thm01-R-sonnet46-r2-A2', 'thm01-R-sonnet46-r2-F',
              'thm01-R-sonnet46-r3-A1')


def akey(run, memo, quote):
    return (run, str(memo).lstrip('0'), ' '.join(str(quote).split())[:60])


def main():
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    adj = {}
    for f in sorted((HERE / 'manager_review').glob('adjustments_*.jsonl')):
        for ln in open(f):
            if ln.strip():
                a = json.loads(ln)
                adj[akey(a['run'], a['memo'], a['quote'])] = a
    rows, ok = [], defaultdict(list)
    for f in sorted((HERE / 'manager_review').glob('*.jsonl')):
        if f.name.startswith(('adjustments_', 'fix')):
            continue
        for ln in open(f):
            if not ln.strip():
                continue
            o = json.loads(ln)
            i = inv.get(o['run'], {})
            if i.get('condition') not in GATED:
                continue
            for c in o.get('claims') or []:
                a = adj.get(akey(o['run'], o['memo'], c.get('quote', '')))
                kind = a['new_kind'] if a else str(c.get('kind', ''))
                tbs = str(a['true_by_sources'] if a else c.get('true_by_sources', '')).strip().lower()
                base = dict(run=o['run'], condition=i.get('condition', ''), worker_model=i.get('model', ''),
                            memo=o['memo'], issue=o.get('issue', ''), draft_type=o.get('draft_type', ''),
                            sent=str(o.get('sent', ''))[:60], kind=kind, true_by_sources=tbs,
                            origin=a['origin'] if a else '', direction=a['direction'] if a else '',
                            quote=str(c.get('quote', '')), loc=str(c.get('loc', '')),
                            evidence=str(a.get('evidence', '') if a else c.get('contradicting')
                                         or c.get('contradicting_loc') or c.get('contradicts') or c.get('basis') or '')[:500],
                            note=str((a or {}).get('note', '') or c.get('note', ''))[:500], group_file=f.name)
                if kind.startswith('M1') or (kind.startswith('M2') and tbs.startswith('no')):
                    rows.append(dict(base, set='wrong'))
                elif kind.startswith('M3') and tbs.startswith(('no', 'partly')):
                    rows.append(dict(base, set='m3_contradicted'))
                elif kind.startswith('M2') and tbs.startswith('undetermined'):
                    rows.append(dict(base, set='m2_undetermined'))
                elif kind == 'ok':
                    ok[o['run']].append(dict(base, set='ok_sample'))
    rng = random.Random(SEED)
    for run in sorted(ok, key=lambda r: (r not in FIRST_RUNS, r)):
        pool = ok[run]
        k = min(len(pool), max(2, math.ceil(OK_SHARE * len(pool))))
        rows.extend((rng if run in FIRST_RUNS else random.Random('%d:%s' % (SEED, run))).sample(pool, k))
    order = {'wrong': 0, 'm3_contradicted': 1, 'ok_sample': 2, 'm2_undetermined': 3}
    rows.sort(key=lambda r: (order[r['set']], r['run'], int(str(r['memo']).lstrip('0') or 0)))
    out = HERE / 'manager_review_check.csv'
    keep, ids = {}, {}
    if out.exists():
        for r in csv.DictReader(open(out)):
            keep[akey(r['run'], r['memo'], r['quote'])] = {k: r.get(k, '') for k in AUTHOR}
            ids[akey(r['run'], r['memo'], r['quote'])] = r['check_id']
    # check_id stays with its claim; claims new to the file get the next numbers (in row order).
    nxt = max([int(v[2:]) for v in ids.values()] or [0]) + 1
    for r in rows:
        k = akey(r['run'], r['memo'], r['quote'])
        if k in ids:
            r['check_id'] = ids[k]
        else:
            r['check_id'] = 'MC%03d' % nxt
            nxt += 1
        r.update(keep.get(k, {c: '' for c in AUTHOR}))
    cols = ['check_id', 'set', 'run', 'condition', 'worker_model', 'memo', 'issue', 'draft_type', 'sent', 'kind',
            'true_by_sources', 'origin', 'direction', 'quote', 'loc', 'evidence', 'note', 'group_file'] + AUTHOR
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    cnt = defaultdict(int)
    for r in rows:
        cnt[r['set']] += 1
    print('wrote manager_review_check.csv', dict(cnt), 'ok pool', sum(len(v) for v in ok.values()))


if __name__ == '__main__':
    main()
