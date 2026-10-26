#!/usr/bin/env python3
"""post_verdict.py — tables made after the author's judging (design §9.29, §9.53 (4); PROPOSALS P9 item 4,
P10, P14). Reads the author's files through author_codes (codes -> values); never writes them.

Outputs (judging/):
  verdict_cells.csv            one row per Study 2 cell (group x model_id x harness_family x effort x condition x
                               manager, counted runs, final commit) and per May condition: n_counted, n_judged,
                               n_pass / n_insufficient / n_fail / n_excluded, pass_k ('k/n' of pass among judged).
  fix_verdicts.csv             the fix experiment: trial, run, author's values (decoded) for the fixed version and
                               for the original run's final commit.
  manager_check_summary.csv    manager_review_check.csv per run x set: n rows, n with author_agree, yes / no / unsure,
                               and for agree = no the author's kind; plus a total row. 'checked' = rows with author_agree
                               (the number to report if the ok sample is cut, P14).
  verdict_vs_prediction.csv    ONLY with --reveal (after judging; predictions stay hidden while judging, P10): one row
                               per judged row of judgments.csv: author's verdict (decoded) vs the frozen prediction
                               (rules-v1) and prior verdict, agree flags, predicted_reason, and an empty
                               disagreement_reason column for the reasons (e.g. 'K rule made concrete (design 9.31)').
                               Existing disagreement_reason values are kept (matched by run and commit_checked).
                               author_verdict_at_reveal = the author's verdict in judgments.csv at REVEAL_COMMIT
                               (before the author saw the predictions; changes after that are recorded in P16).

Usage: python3 judging/post_verdict.py [--reveal]
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import author_codes   # noqa: E402

V = author_codes.value
# Last author commit of judgments.csv before the predictions were first revealed (2026-10-23, P16).
REVEAL_COMMIT = '43578c8'
# same cell definition as harness_items_groups.csv (MODEL_ID and family copied from harness_items.py)
MODEL_ID = {'Claude Sonnet 4.6': 'claude-sonnet-4-6', 'GPT-6 Luna': 'gpt-6-luna'}


def family(h):
    if 'Claude Code' in h:
        v = [t for t in h.replace('(', ' ').split() if t[:1].isdigit()]
        return 'Claude Code ' + (v[0] if v else '')
    if h.startswith('agy'):
        return 'agy'
    if 'Copilot' in h:
        return 'Copilot CLI'
    return h


def read(name):
    with open(HERE / name, newline='') as fh:
        return list(csv.DictReader(fh))


def write(name, rows, cols=None):
    cols = cols or (list(rows[0]) if rows else ['empty'])
    with open(HERE / name, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print('wrote', name, len(rows))


def main():
    reveal = '--reveal' in sys.argv
    inv = {r['run']: r for r in read('inventory.csv')}
    hi = {r['run']: r for r in read('harness_items.csv')}
    j = read('judgments.csv')
    jf = {r['run']: r for r in j if r['commit_checked'] == 'final'}

    # verdict_cells.csv
    cells = defaultdict(list)
    for run, i in inv.items():
        if i['exclude'] or i['status'] == 'not_run':
            continue
        if i['group'] == 'may':
            key = ('may', i['model'], family(i['harness']), '', i['condition'], i.get('manager', ''))
        else:
            key = (i['group'], MODEL_ID.get(i['model'], i['model']), family(i['harness']),
                   hi.get(run, {}).get('effort', ''), i['condition'], i.get('manager', ''))
        cells[key].append(run)
    out = []
    for (grp, model, harness, effort, cond, manager), runs in sorted(cells.items()):
        vs = [V('author_verdict', jf.get(r, {}).get('author_verdict', '')) for r in runs]
        judged = [v for v in vs if v]
        c = Counter(judged)
        out.append(dict(group=grp, model_id=model, harness_family=harness, effort=effort, condition=cond,
                        manager=manager, n_counted=len(runs), n_judged=len(judged), n_pass=c['pass'],
                        n_insufficient=c['insufficient'], n_fail=c['fail'], n_excluded=c['excluded'],
                        pass_k='%d/%d' % (c['pass'], len(judged)) if judged else '', runs=' '.join(runs)))
    write('verdict_cells.csv', out)

    # fix_verdicts.csv
    fx = read('fix_judgments.csv')
    out = []
    for f in fx:
        o = jf.get(f['run'], {})
        row = dict(trial=f['trial'], run=f['run'], commit_checked=f['commit_checked'])
        for col in author_codes.JUDGMENT_COLS:
            row['fixed_' + col.replace('author_', '')] = V(col, f.get(col, ''))
            row['original_' + col.replace('author_', '')] = V(col, o.get(col, ''))
        row['fixed_note'] = f.get('author_note', '')
        out.append(row)
    write('fix_verdicts.csv', out)

    # manager_check_summary.csv
    m = read('manager_review_check.csv')
    g = defaultdict(list)
    for r in m:
        g[(r['run'], r['set'])].append(r)
    out = []
    tot = Counter()
    for (run, st), rs in sorted(g.items()):
        ag = Counter(V('author_agree', r['author_agree']) for r in rs if r['author_agree'].strip())
        kinds = Counter(V('author_kind', r['author_kind']) for r in rs
                        if V('author_agree', r['author_agree']) == 'no' and r['author_kind'].strip())
        row = dict(run=run, set=st, n=len(rs), checked=sum(ag.values()), yes=ag['yes'], no=ag['no'], unsure=ag['unsure'],
                   no_as_M1=kinds['M1-false'], no_as_M2=kinds['M2-unverified'], no_as_M3=kinds['M3-added'],
                   no_as_ok=kinds['ok'])
        for k in ('n', 'checked', 'yes', 'no', 'unsure', 'no_as_M1', 'no_as_M2', 'no_as_M3', 'no_as_ok'):
            tot[(st, k)] += row[k]
        out.append(row)
    for st in ('wrong', 'm3_contradicted', 'ok_sample', 'm2_undetermined'):
        out.append(dict(run='TOTAL', set=st, **{k: tot[(st, k)] for k in ('n', 'checked', 'yes', 'no', 'unsure', 'no_as_M1',
                                                                          'no_as_M2', 'no_as_M3', 'no_as_ok')}))
    write('manager_check_summary.csv', out)

    if not reveal:
        print('verdict_vs_prediction.csv not written (predictions stay hidden while judging; use --reveal after judging)')
        return
    # the author's verdicts when the predictions were first revealed (P16): judgments.csv at REVEAL_COMMIT
    import io
    import subprocess
    at = subprocess.run(['git', '-C', str(HERE), 'show', '%s:./judgments.csv' % REVEAL_COMMIT],
                        capture_output=True, text=True).stdout
    at_reveal = {(r['run'], r['commit_checked']): V('author_verdict', r['author_verdict'])
                 for r in csv.DictReader(io.StringIO(at))} if at else {}
    old = {}
    p = HERE / 'verdict_vs_prediction.csv'
    if p.exists():
        old = {(r['run'], r['commit_checked']): r.get('disagreement_reason', '') for r in read(p.name)}
    out = []
    for r in j:
        a = V('author_verdict', r['author_verdict'])
        if not a:
            continue
        i = inv.get(r['run'], {})
        pv, pr = r['predicted_verdict'], r['prior_verdict']
        out.append(dict(run=r['run'], commit_checked=r['commit_checked'], group=i.get('group', ''),
                        condition=i.get('condition', ''), model=i.get('model', ''), manager=i.get('manager', ''),
                        author_verdict=a, predicted_verdict=pv, agree_predicted='yes' if a == pv else 'no',
                        prior_verdict=pr, agree_prior=('yes' if a == (pr.split(';')[0].split() or [''])[0] else 'no') if pr else '',
                        predicted_reason=r['predicted_reason'],
                        author_verdict_at_reveal=at_reveal.get((r['run'], r['commit_checked']), ''),
                        disagreement_reason=old.get((r['run'], r['commit_checked']), '')))
    write('verdict_vs_prediction.csv', out)


if __name__ == '__main__':
    main()
