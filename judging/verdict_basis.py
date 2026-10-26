#!/usr/bin/env python3
"""verdict_basis.py — the three items the author's final verdict starts from
(author 2026-10-12): the final conclusion, the 'up to scalar' interpretation
(K = 1, i.e. K components dropped) and the parity of gb. Facts only; it never judges.
The γ check is a separate material (g_summary.csv, g4_summary.csv) and is not used here.

One row per judgments.csv row (run, commit_checked):
  run, commit_checked, group, model, condition, exclude
  conclusion        gb=0 only / always trivial / other / unstated   (from sheet.csv stated_class;
                    May runs without a stated_class: readings headline_conclusion)
  conclusion_reading_dependent   yes when the run states its conclusion under several readings
                    (stated_class 'reading-dependent' or readings_stated not empty)
  K_equals_1        yes (K dropped: 'up to scalar' / modulo scalars / projected out) /
                    no (K kept) / extended (f may take values in g+CK) / not used / unstated
  gb_parity         1 (gb odd) / 0 (gb even, scalar) / unstated
  kappa_sign        commuting / supercommuting / unstated   (reference: the even-gb reading
                    'all gb trivial' also needs κ supercommuting, reevaluation.md §1)
  paper_reading     odd-gb / even-gb / other   (design §9.40 3)
  conclusion_text, K_evidence, gb_evidence, readings_stated, source
  script_commit

Fix experiment (design §9.30, §9.52; ① 10-12): one extra row per trial for the Worker's final commit
after the fix (commit_checked = 'fix final (<sha>)', group = 'fix'), from readings_fix/rd_fix.jsonl.
These rows are not in judgments.csv; the original run keeps its own row.

Readings are taken at the final commit; for C runs the first commit differs from the final
only in reflection files (diff -rq, 2026-10-12), so the first row repeats the final values.

Usage: python3 judging/verdict_basis.py
"""
import csv
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent

PARITY = {'odd': '1', 'even': '0'}
KMAP = {'dropped': 'yes', 'kept': 'no'}


def val(d, k):
    v = d.get(k, '')
    if isinstance(v, dict):
        v = v.get('value', '')
    return '' if v is None else str(v).strip()


def conclusion(text):
    t = text.strip()
    low = t.lower()
    if not t:
        return 'unstated', 'no'
    dep = 'yes' if 'reading-dependent' in low else 'no'
    if low.startswith('trivial iff gb=0'):
        return 'gb=0 only', dep
    if low.startswith('all gb trivial'):
        return 'always trivial', dep
    if dep == 'yes':
        if "headline = all gb trivial" in low or "headline 'all gb trivial'" in low:
            return 'always trivial', dep
        if "headline = trivial iff gb=0" in low:
            return 'gb=0 only', dep
    return 'other', dep


def paper_reading(gb, kappa, K):
    if not gb:
        return ''
    if gb == 'odd':
        return 'odd-gb'
    if (gb, kappa, K) == ('even', 'supercommuting', 'dropped'):
        return 'even-gb'
    return 'other'


def main():
    inv = {r['run']: r for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    sheet = {(r['run'], r['commit_checked']): r for r in csv.DictReader(open(HERE / 'sheet.csv'))}
    readings = {}
    for f in sorted((HERE / 'readings').glob('*.jsonl')):
        for ln in open(f):
            if ln.strip():
                d = json.loads(ln)
                readings[d['run']] = (d, f.name)
    commit = subprocess.run(['git', '-C', str(REV), 'rev-parse', '--short', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    rows = []
    keys = [(j['run'], j['commit_checked'], None) for j in csv.DictReader(open(HERE / 'judgments.csv'))]
    fixf = HERE / 'readings_fix' / 'rd_fix.jsonl'
    if fixf.exists():
        for ln in open(fixf):
            if ln.strip():
                d = json.loads(ln)
                keys.append((d['run'], d['commit_checked'], d))
    for run, cc, fixrd in keys:
        i = inv.get(run, {})
        s = sheet.get((run, cc), {}) if fixrd is None else {}
        rd, src = (fixrd, '../readings_fix/rd_fix.jsonl') if fixrd is not None else readings.get(run, ({}, ''))
        text = s.get('stated_class', '') or val(rd, 'headline_conclusion')
        concl, dep = conclusion(text)
        rs = rd.get('readings_stated') if rd else None
        if isinstance(rs, str):
            rs = rs.strip()
            rs = '' if rs in ('', '[]') else rs
        elif rs:
            rs = json.dumps(rs, ensure_ascii=False)
        else:
            rs = ''
        if rs:
            dep = 'yes'
        gb, kappa, K = val(rd, 'gb_parity'), val(rd, 'kappa_sign'), val(rd, 'K_handling')
        rows.append(dict(
            run=run, commit_checked=cc, group='fix' if fixrd is not None else i.get('group', ''), model=i.get('model', ''),
            condition=i.get('condition', ''), exclude=i.get('exclude', ''),
            conclusion=concl, conclusion_reading_dependent=dep,
            K_equals_1=(KMAP.get(K, K) or 'unstated') if rd else '',
            gb_parity=(PARITY.get(gb, gb) or 'unstated') if rd else '',
            kappa_sign=(kappa or 'unstated') if rd else '',
            paper_reading=paper_reading(gb, kappa, K) if rd else '',
            conclusion_text=text,
            K_evidence=val(rd, 'K_handling_evidence')[:400],
            gb_evidence=val(rd, 'gb_parity_evidence')[:400],
            readings_stated=rs[:600],
            source=('readings/%s (final commit)' % src) if rd else 'no readings (not extracted)',
            script_commit=commit))
    with open(HERE / 'verdict_basis.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print('wrote verdict_basis.csv', len(rows))


if __name__ == '__main__':
    main()
