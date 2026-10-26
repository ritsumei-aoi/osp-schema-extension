#!/usr/bin/env python3
"""error_trace_summary.py — per-run and per-cell summary of judging/error_trace/*.jsonl
(error_trace_spec.md; errors = E1 γ-check mismatches and E2 facts2 contradictions,
author 2026-10-12). Facts only. The five group files were written by subagents with
slightly different extra fields; this script reads only the common ones and normalises
the stage names.
error_trace/adjustments.jsonl applies the author's rules of 2026-10-12 (judging P6) on top of the
subagent files (which are kept as written): 'reclassify' (reading remark -> not an error; empty
structure -> E1-missing) and 'add' (E1-missing for absent/placeholder data of a specified layer in
A/F/G; 'completeness' for data in a non-schema form, not an error).

error_trace_summary.csv (one row per Study 2 counted run):
  run, condition, model, n_E1, n_E1_sign_flip_only (global sign flip, see notes), n_E2,
  n_E2_reflection (errors written in the reflection / I09), n_E2_report (final chat report),
  n_intermediate (E1 seen only in an intermediate version and fixed later; bG_claude only),
  first_stage, stages (stage=count), corrected (yes/partially counts), detected_by (class=count),
  stage_identifiable
error_trace_summary.md: per condition x model cell, runs with >= 1 error (E1 / E2 / any),
  errors per run (median), E2 written in the reflection (share), corrected in run, detected_by.

Usage: python3 judging/error_trace_summary.py
"""
import csv
import json
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent


def stage(s):
    s = str(s or '')
    low = s.lower()
    m = re.match(r'(I0[1-8])', s)
    if 'reflection' in low or s.startswith('I09'):
        return 'reflection'
    if m:
        return m.group(1)
    if 'final message' in low or 'final chat' in low or 'final report' in low or '(session)' in low:
        return 'final report'
    if low.startswith('step'):
        return 'F step'
    if 'proof' in low or 'deliverable' in low or low.startswith('turn'):
        return 'one-shot turn'
    return s or 'unknown'


def detector(s):
    low = str(s or '').lower()
    if low.startswith('not detected'):
        return 'not detected'
    if low.startswith('human'):
        return 'human (gate)'
    if low.startswith("scribe"):
        return 'scribe check' + (' -> human' if 'hum' in low else '')
    if low.startswith('manager'):
        return 'Manager'
    if low.startswith('worker'):
        return 'Worker'
    return low or 'unknown'


ORDER = ['I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I07', 'I08', 'one-shot turn', 'F step', 'final report', 'reflection']


def main():
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    gs = {r['run']: r for r in csv.DictReader(open(HERE / 'g_summary.csv'))}
    adj = [json.loads(l) for l in open(HERE / 'error_trace' / 'adjustments.jsonl') if l.strip()]
    recl = {(a['run'], a['error_id']): a['new_kind'] for a in adj if a['action'] == 'reclassify'}
    per = defaultdict(lambda: dict(E1=0, miss=0, rem=0, comp=0, flip=0, E2=0, E2_refl=0, E2_rep=0, inter=0, stages=Counter(),
                                   corr=Counter(), det=Counter(), ident=''))
    for f in sorted(x for x in (HERE / 'error_trace').glob('*.jsonl') if x.name != 'adjustments.jsonl'):
        for ln in open(f):
            if not ln.strip():
                continue
            o = json.loads(ln)
            p = per[o['run']]
            if 'run_summary' in o:
                p['ident'] = str(o['run_summary'].get('stage_identifiable', ''))
            e = str(o.get('error_id', ''))
            kind = str(o.get('kind') or '')
            if e.startswith('X1') or kind == 'E1-intermediate':
                p['inter'] += 1
                continue
            if not e.startswith(('E1', 'E2')):
                continue
            new = recl.get((o['run'], e))
            if new == 'reading remark':
                p['rem'] += 1
                continue
            if new == 'E1-missing':
                p['miss'] += 1
            st = stage(o.get('introduced_issue'))
            p['stages'][st] += 1
            p['det'][detector(o.get('detected_by'))] += 1
            c = str(o.get('corrected_in_run') or 'no').split()[0].lower().strip(',;')
            p['corr'][c] += 1
            if e.startswith('E1'):
                p['E1'] += 1
                m = re.match(r'E1-(gamma|gammaK)-n(\d)', e)
                flip = o.get('sign_flip_only') is True
                if m and not flip:
                    col = ('gammaK_n' if 'K' in m.group(1) else 'gamma_n') + m.group(2)
                    flip = gs.get(o['run'], {}).get(col, '').startswith('-')
                p['flip'] += int(bool(flip))
            else:
                p['E2'] += 1
                p['E2_refl'] += int(st == 'reflection')
                p['E2_rep'] += int(st == 'final report')
    for a in adj:
        if a['action'] != 'add':
            continue
        p = per[a['run']]
        if a['kind'] == 'completeness':
            p['comp'] += 1
            continue
        p['E1'] += 1
        p['miss'] += 1
        p['stages'][stage(a['introduced_issue'])] += 1
        p['det'][detector(a['detected_by'])] += 1
        p['corr']['no'] += 1
    rows = []
    for run, p in sorted(per.items()):
        i = inv.get(run, {})
        sts = [s for s in ORDER if p['stages'][s]] + [s for s in p['stages'] if s not in ORDER]
        rows.append(dict(run=run, condition=i.get('condition', ''), model=i.get('model', ''),
                         n_E1=p['E1'], n_E1_missing=p['miss'], n_E1_sign_flip_only=p['flip'], n_E2=p['E2'],
                         n_reading_remarks=p['rem'], n_completeness=p['comp'], n_E2_reflection=p['E2_refl'],
                         n_E2_report=p['E2_rep'], n_intermediate=p['inter'], first_stage=sts[0] if sts else '',
                         stages='; '.join('%s=%d' % (s, p['stages'][s]) for s in sts),
                         corrected='yes=%d partially=%d' % (p['corr']['yes'], p['corr']['partially']),
                         detected_by='; '.join('%s=%d' % kv for kv in p['det'].most_common()),
                         stage_identifiable=p['ident']))
    with open(HERE / 'error_trace_summary.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    commit = subprocess.run(['git', '-C', str(REV), 'rev-parse', '--short', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    cells = defaultdict(list)
    for r in rows:
        cells[(r['condition'], r['model'])].append(r)
    co = {'A1': 0, 'A2': 1, 'F': 2, 'G': 3, 'C': 4}
    with open(HERE / 'error_trace_summary.md', 'w') as fh:
        fh.write('# Error trace summary (Study 2 counted runs)\n\nGenerated by error_trace_summary.py at %s from '
                 'error_trace/*.jsonl. E1 = γ-check mismatch (A/F/G only; C has no layer files), E2 = facts2 '
                 'contradiction. E1 includes missing data of a specified layer and global sign flips (both errors, author 2026-10-12; '
                 'counted in their own columns too). Reading remarks and non-schema forms are not errors (adjustments.jsonl). Descriptive only.\n\n' % commit)
        fh.write('| condition | model | n | runs with E1 | E1 missing | E1 sign flip | runs with E2 | errors/run (median) '
                 '| E2 in reflection | E2 in final report | corrected (yes/partly) | detected by | intermediate E1 fixed later |\n'
                 '|' + '---|' * 13 + '\n')
        for (cond, model), rs in sorted(cells.items(), key=lambda kv: (co.get(kv[0][0], 9), kv[0][1])):
            n = len(rs)
            det = Counter()
            for r in rs:
                for part in filter(None, r['detected_by'].split('; ')):
                    k, v = part.rsplit('=', 1)
                    det[k] += int(v)
            e2 = sum(r['n_E2'] for r in rs)
            fh.write('| %s | %s | %d | %d | %d | %d | %d | %s | %d/%d | %d/%d | %d/%d | %s | %d |\n' % (
                cond, model, n, sum(1 for r in rs if r['n_E1']), sum(r['n_E1_missing'] for r in rs),
                sum(r['n_E1_sign_flip_only'] for r in rs),
                sum(1 for r in rs if r['n_E2']), statistics.median(r['n_E1'] + r['n_E2'] for r in rs),
                sum(r['n_E2_reflection'] for r in rs), e2, sum(r['n_E2_report'] for r in rs), e2,
                sum(int(r['corrected'].split()[0].split('=')[1]) for r in rs),
                sum(int(r['corrected'].split()[1].split('=')[1]) for r in rs),
                ', '.join('%s %d' % kv for kv in det.most_common()), sum(r['n_intermediate'] for r in rs)))
    print('wrote error_trace_summary.csv/.md', len(rows))


if __name__ == '__main__':
    main()
