#!/usr/bin/env python3
"""build_sheet.py — merge inventory.csv, g_summary.csv and facts/*.jsonl into
the author's judging sheet (facts only; the author fills the author_* columns).

Outputs
- judging/judgments.csv : the ONLY file the author edits (author_* columns). It
  also holds the frozen reference columns prior_verdict / prior_source (earlier
  judgments, from prior.csv) and predicted_* (rules-based prediction, from
  predictions.csv, frozen 2026-10-07 before the author started). Created once;
  later builds only append rows for new keys and never rewrite existing rows.
- judging/sheet.csv : one row per (run, commit_checked), generated; author_*
  columns are copied from judgments.csv for viewing. Do not edit.
- judging/sheet.md  : a short view for reading (no long text).

Columns (objective, from the extraction or the checks)
- stated_class / stated_conclusion: the run's own final conclusion.
- reading_declared: what the run says about gb parity, kappa sign, K.
- gamma_vs_ref_n1, data_implies_n1/_n2 (K dropped / kept): from g_summary (G/A/F runs).
- k_dependence: as extracted (only when the extractor reported it).
- test_range, computation, rerun, reported_numbers.
- interp_*: inputs for "can it be judged correct under an admissible reading"
  (two admissible readings: odd gb -> trivial iff gb=0; even gb, kappa
  supercommuting, K dropped -> all gb trivial). Facts, not a verdict.
- arg_issue_count / argument_issues: stage-1 candidates (kept for reference).
- remark_readings: whether the run states more than one reading (a REMARK only;
  not used for correctness; design §9.27).
- theory_items / work_items (+ *_contradictions, *_unsupported counts): "items that
  may be contrary to fact", split into statements of mathematical content (theory)
  and statements about the work done to support it (computation, verification,
  artifacts, self-reports). Each item: [kind; evidence] "quote" (loc) vs fact.
  Whether and how to penalize is the author's decision. Evidence "agent_unvalidated"
  means an agent computation NOT checked against the reference: do not rely on it alone.
- gamma_data_items: items that only restate that the deliverable γ data differ from
  the reference; the facts are in gamma_vs_ref_n1 (criterion 1), not statements of the run.
Author columns: author_result (1: deliverables/computation), author_argument (2),
author_interpretation, author_verdict, author_note.
"""
import csv
import glob
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import author_codes   # noqa: E402  (numeric codes of author_*, 2026-10-14)

HERE = Path(__file__).resolve().parent
AUTHOR = ['author_verdict', 'author_result', 'author_argument', 'author_interpretation', 'author_note']
REF_COLS = ['prior_verdict', 'predicted_verdict', 'prior_source', 'predicted_reason', 'predicted_rules']


def s(v):
    if v is None:
        return ''
    if isinstance(v, str):
        return v
    return json.dumps(v, ensure_ascii=False)


def short(v, n=160):
    t = ' '.join(s(v).split())
    return t if len(t) <= n else t[:n - 1] + '…'


def main():
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    gs = {r['run']: r for r in csv.DictReader(open(HERE / 'g_summary.csv'))}
    facts = []
    for f in sorted(glob.glob(str(HERE / 'facts' / '*.jsonl'))):
        for line in open(f):
            if line.strip():
                d = json.loads(line)
                d['_group'] = Path(f).stem
                facts.append(d)
    f2 = {}
    for f in sorted(glob.glob(str(HERE / 'facts2' / '*.jsonl'))):
        for line in open(f):
            if line.strip():
                d2 = json.loads(line)
                ck = 'first' if s(d2.get('commit_checked')).strip().lower().startswith('first') else 'final'
                f2[(d2['run'], ck)] = d2
    # The author's entries live only in judgments.csv (the author edits that file;
    # this script never rewrites existing rows there, it only appends new keys).
    jpath = HERE / 'judgments.csv'
    prior = {(r['run'], r['commit_checked']): r for r in csv.DictReader(open(HERE / 'prior.csv', newline=''))}
    pred = {}
    if (HERE / 'predictions.csv').exists():
        pred = {(r['run'], r['commit_checked']): r for r in csv.DictReader(open(HERE / 'predictions.csv', newline=''))}
    old = {}
    if jpath.exists():
        for r in csv.DictReader(open(jpath, newline='')):
            old[(r['run'], r['commit_checked'])] = r
    elif (HERE / 'sheet.csv').exists():   # one-time migration from the earlier layout
        for r in csv.DictReader(open(HERE / 'sheet.csv')):
            old[(r['run'], r['commit_checked'])] = r
    rows = []
    order = {r: i for i, r in enumerate(inv)}
    facts.sort(key=lambda d: (order.get(d['run'], 9999), s(d.get('commit_checked'))))
    for d in facts:
        run = d['run']
        i, g = inv[run], gs.get(run, {})
        args = d.get('argument_issues') or []
        if isinstance(args, str):
            args = [args]
        row = dict(
            run=run, group=i['group'], model=i['model'], condition=i['condition'],
            status=d.get('status') or i['status'], exclude=i['exclude'],
            commit_checked='first' if s(d.get('commit_checked')).strip().lower().startswith('first') else 'final',
            commit=i['commit_first'] if s(d.get('commit_checked')).strip().lower().startswith('first') else i['commit_final'],
            commit_note=s(d.get('commit_checked')),
            stated_class=s(d.get('stated_conclusion_class')),
            stated_conclusion=s(d.get('stated_conclusion')),
            scope=s(d.get('scope')),
            reading_declared=s(d.get('declared_reading')),
            gamma_vs_ref_n1=g.get('gamma_n1', ''), gammaK_vs_ref_n1=g.get('gammaK_n1', ''),
            data_implies_n1=g.get('data_implies_n1', ''), data_implies_n2=g.get('data_implies_n2', ''),
            rank_nonK_n1=g.get('rank_nonK_n1', ''), rank_K_n1=g.get('rank_K_n1', ''),
            k_dependence=s(d.get('k_dependence')),
            consistency_with_data=s(d.get('consistency_with_data')),
            test_range=s(d.get('test_range')),
            computation=s(d.get('computation')),
            rerun=s(d.get('rerun')),
            reported_numbers=s(d.get('reported_numbers')),
            changes_first_to_final=s(d.get('changes_since_first') or d.get('changes_first_to_final')
                                     or d.get('deliverable_changes_first_to_final')),
            arg_issue_count=len(args),
            argument_issues=s(args),
            notes=s(d.get('notes')),
            extraction_group=d['_group'],
        )
        d2 = f2.get((run, row['commit_checked']), {})
        row['remark_readings'] = s(d2.get('remark_readings'))
        data_items = []
        for col in ('theory_items', 'work_items'):
            items = d2.get(col) or []
            if col == 'work_items':
                # Differences of the deliverable γ data from the reference are facts about
                # deliverables (column gamma_vs_ref_n1, i.e. criterion 1), not statements of the run.
                keep = []
                for it in items:
                    q = s(it.get('quote'))
                    if it.get('evidence') == 'validated_reference' and 'C_n_gamma.json' in q and len(q) < 80:
                        data_items.append(it)
                    else:
                        keep.append(it)
                items = keep
            row[col.replace('_items', '_contradictions')] = sum(1 for it in items if it.get('kind') == 'contradiction')
            row[col.replace('_items', '_unsupported')] = sum(1 for it in items if it.get('kind') == 'unsupported')
            row[col] = '\n'.join('[%s; %s]%s "%s" (%s)%s' % (
                it.get('kind', ''), it.get('evidence', ''),
                ' [quote may not be verbatim]' if len(s(it.get('quote'))) > 300 else '',
                it.get('quote', ''), it.get('loc', ''),
                (' vs ' + s(it.get('contradicts'))) if it.get('contradicts') else '') for it in items)
        row['gamma_data_items'] = '\n'.join('%s vs %s' % (s(it.get('quote')), s(it.get('contradicts'))) for it in data_items)
        row['dropped_items'] = s(d2.get('dropped'))
        prev = old.get((run, row['commit_checked']), {})
        for k in AUTHOR:
            row[k] = prev.get(k, '')
        rows.append(row)
    # judgments.csv: author columns plus the frozen prior / predicted columns (design §9.29).
    jkeys = ['run', 'commit_checked'] + REF_COLS[:2] + AUTHOR + REF_COLS[2:]
    def ref_values(key):
        q, p = prior.get(key, {}), pred.get(key, {})
        return dict(prior_verdict=q.get('prior_verdict', ''), prior_source=q.get('prior_source', ''),
                    predicted_verdict=p.get('predicted_verdict', ''), predicted_reason=p.get('predicted_reason', ''),
                    predicted_rules=p.get('predicted_rules', ''))
    if not jpath.exists():
        with open(jpath, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=jkeys)
            w.writeheader()
            for r in rows:
                w.writerow({**{k: r.get(k, '') for k in jkeys}, **ref_values((r['run'], r['commit_checked']))})
    else:
        with open(jpath, newline='') as fh:
            hdr = next(csv.reader(fh))
        new_rows = [r for r in rows if (r['run'], r['commit_checked']) not in old]
        if new_rows:   # new runs only; existing rows (incl. frozen predictions) are never rewritten
            with open(jpath, 'a', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=hdr, extrasaction='ignore')
                for r in new_rows:
                    w.writerow({**{k: '' for k in hdr}, 'run': r['run'], 'commit_checked': r['commit_checked'],
                                **ref_values((r['run'], r['commit_checked']))})
    for r in rows:   # copy reference columns into the view
        j = old.get((r['run'], r['commit_checked'])) or ref_values((r['run'], r['commit_checked']))
        for k in REF_COLS:
            r[k] = j.get(k, '')
    keys = list(rows[0].keys())
    with open(HERE / 'sheet.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    md = ['# Judging sheet (view; generated by build_sheet.py from sheet.csv)', '',
          'Facts only. Full text is in sheet.csv. "implies" = conclusion implied by the run\'s own γ with the independent coboundary (K dropped / K kept).', '',
          'The frozen prediction (predicted_verdict) is not shown here while judging (author 2026-10-16); see judgments.csv after judging.', '',
          '| run | cond | commit | stated | γ vs ref (n=1) | implies n=1 | test range | theory contra/unsup | work contra/unsup | prior | author verdict |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        md.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['run'].replace('thm01-R-', ''), r['condition'], short(r['commit_checked'], 12),
            short(r['stated_class'], 40), short(r['gamma_vs_ref_n1'], 30), short(r['data_implies_n1'], 40),
            short(r['test_range'], 50), '%s/%s' % (r.get('theory_contradictions', ''), r.get('theory_unsupported', '')),
            '%s/%s' % (r.get('work_contradictions', ''), r.get('work_unsupported', '')),
            r.get('prior_verdict', ''),
            author_codes.display('author_verdict', r['author_verdict'])))
    (HERE / 'sheet.md').write_text('\n'.join(md) + '\n')
    print('wrote sheet.csv/.md', len(rows), 'rows,', len({r['run'] for r in rows}), 'runs')


if __name__ == '__main__':
    main()
