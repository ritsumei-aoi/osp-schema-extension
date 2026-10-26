#!/usr/bin/env python3
"""compare_pre_verdict.py — quantities that can be compared before the author's verdict
(author 2026-10-12: compare everything except mathematical correctness on objective data).
Facts only; descriptive (design §3, §7: no statistical claims).

One row per Study 2 cell: condition x model_id x harness_family x effort x mode x manager (counted runs only;
manager = the Manager model of gated interactive runs, appended column since 2026-10-17;
mode = interactive (human-relayed runs, effort = tool default) or batch).
Columns (each 'k/n' or a median; blank when no run of the cell has the material):
  n
  conclusion: gb0_only, always_trivial, other            verdict_basis.csv (three items, author 2026-10-12)
  reading_dependent                                       conclusion stated under several readings
  K_equals_1_yes / no / extended / unstated               verdict_basis.csv
  gb_odd / gb_even / gb_unstated                          verdict_basis.csv
  paper_odd_gb / paper_even_gb / paper_other              design §9.40 3
  ambiguity_ge2                                           readings: level 2 or 3 (names another reading)
  gamma_checked, gamma_match_n1                           g_summary.csv: γ (non-K) equals the reference
                                                          built from the run's own realization (=none/=super)
  n4_unmodified, n4_range_edit, n4_needs_change, n4_no_code   n4 summary (generality, §9.35 view 2;
                                                          definition: author 2026-10-12)
  n4_match                                                n4 output matches the reference (vs_ref_class match)
  same_keys_across_n                                      structure_survey.csv (layers keep one structure over n)
  kit_edited                                              kit_edits.csv: any reference/template/config file changed
  auto_compactions_runs                                   runs with >= 1 automatic compaction ('not recorded' excluded)
  worker_minutes_median          resources.csv worker_seconds; interactive runs: timing.csv worker_busy_min
  worker_cost_usd_median, worker_output_tokens_median   resources.csv (blank where not recorded)
  The γ check exists only for runs with the layer files (A/F/G); C has no schema, so it is blank there.
Plus compare_pre_verdict.md (same table, readable).

Usage: python3 judging/compare_pre_verdict.py
"""
import csv
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent
MODEL_ID = {'Claude Sonnet 4.6': 'claude-sonnet-4-6', 'GPT-6 Luna': 'gpt-6-luna'}
COND_ORDER = {'A1': 0, 'A2': 1, 'F': 2, 'G': 3, 'C': 4}


def family(h):
    if 'Claude Code' in h:
        v = [t for t in h.replace('(', ' ').split() if t[:1].isdigit()]
        return 'Claude Code ' + (v[0] if v else '')
    if h.startswith('agy'):
        return 'agy'
    if 'Copilot' in h:
        return 'Copilot CLI'
    return h


def load(name, key='run'):
    p = HERE / name
    if not p.exists():
        return {}
    out = {}
    for r in csv.DictReader(open(p)):
        out.setdefault(r[key], r)
    return out


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    hi = load('harness_items.csv')
    vb = {}
    for r in csv.DictReader(open(HERE / 'verdict_basis.csv')):
        if r['run'] not in vb or r['commit_checked'] == 'final':
            vb[r['run']] = r
    gs = load('g_summary.csv')
    n4 = load('n4_summary.csv')
    st = load('structure_survey.csv')
    ke = load('kit_edits.csv')
    rs = load('resources.csv')
    tm = load('timing.csv')
    rd = {}
    import json
    for f in sorted((HERE / 'readings').glob('*.jsonl')):
        for ln in open(f):
            if ln.strip():
                d = json.loads(ln)
                rd[d['run']] = d
    cells = defaultdict(list)
    mgr = {r['run']: r.get('manager', '') for r in csv.DictReader(open(HERE / 'inventory.csv'))}
    for run, h in hi.items():
        if h['exclude'] or h['group'] == 'may':
            continue
        # Manager separates cells (lead 2026-10-16/17, design 9.56): appended to the key
        cells[(h['condition'], MODEL_ID.get(h['model'], h['model']), family(h['harness']), h['effort'], h['group'],
               mgr.get(run, ''))].append(run)
    commit = subprocess.run(['git', '-C', str(REV), 'rev-parse', '--short', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    out = []
    for (cond, model, harness, effort, mode, manager), runs in sorted(cells.items(), key=lambda kv: (COND_ORDER.get(kv[0][0], 9), kv[0][1:])):
        n = len(runs)

        def frac(pred, pool=runs):
            have = [r for r in pool if pred(r) is not None]
            if not have:
                return ''
            return '%d/%d' % (sum(1 for r in have if pred(r)), len(have))

        def cnt(src, col, value):
            return frac(lambda r: (src[r][col] == value) if r in src and src[r][col] != '' else None)

        def med(vals):
            v = [x for x in vals if x is not None]
            return round(statistics.median(v), 2) if v else ''
        lvl = lambda r: (int(str(rd[r].get('ambiguity_level', '')).strip()) >= 2) if r in rd and str(rd[r].get('ambiguity_level', '')).strip().isdigit() else None
        gm = lambda r: (gs[r]['gamma_n1'].startswith('=')) if r in gs and gs[r]['gamma_n1'] and not gs[r].get('error_n1') else None
        n4m = lambda m: (lambda r: (n4[r]['n4_method'] == m) if r in n4 and n4[r]['n4_method'] not in ('', 'excluded') else None)
        kit = lambda r: (sum(int(ke[r].get(c) or 0) for c in ('reference_modified', 'reference_deleted', 'template_modified',
                                                              'template_deleted', 'config_modified', 'config_deleted')) > 0) if r in ke else None
        comp = lambda r: (int(hi[r]['auto_compactions']) > 0) if hi[r]['auto_compactions'].isdigit() else None
        row = dict(condition=cond, model_id=model, harness_family=harness, effort=effort, mode=mode, n=n,
                   gb0_only=cnt(vb, 'conclusion', 'gb=0 only'), always_trivial=cnt(vb, 'conclusion', 'always trivial'),
                   other=cnt(vb, 'conclusion', 'other'), reading_dependent=cnt(vb, 'conclusion_reading_dependent', 'yes'),
                   K_equals_1_yes=cnt(vb, 'K_equals_1', 'yes'), K_equals_1_no=cnt(vb, 'K_equals_1', 'no'),
                   K_equals_1_extended=cnt(vb, 'K_equals_1', 'extended'), K_equals_1_unstated=cnt(vb, 'K_equals_1', 'unstated'),
                   gb_odd=cnt(vb, 'gb_parity', '1'), gb_even=cnt(vb, 'gb_parity', '0'), gb_unstated=cnt(vb, 'gb_parity', 'unstated'),
                   paper_odd_gb=cnt(vb, 'paper_reading', 'odd-gb'), paper_even_gb=cnt(vb, 'paper_reading', 'even-gb'),
                   paper_other=cnt(vb, 'paper_reading', 'other'), ambiguity_ge2=frac(lvl),
                   gamma_match_n1=frac(gm),
                   n4_unmodified=frac(n4m('unmodified')), n4_range_edit=frac(n4m('range-edit')),
                   n4_needs_change=frac(n4m('needs-code-change')), n4_no_code=frac(n4m('no-code')),
                   n4_match=frac(lambda r: (n4[r]['vs_ref_class'] == 'match') if r in n4 and n4[r]['vs_ref_class'] else None),
                   same_keys_across_n=frac(lambda r: (st[r]['same_keys_across_n'] == '1') if r in st and st[r]['same_keys_across_n'] != '' else None),
                   kit_edited=frac(kit), auto_compactions_runs=frac(comp),
                   worker_minutes_median=med([num(rs[r]['worker_seconds']) / 60 if r in rs and num(rs[r]['worker_seconds'])
                                              else num(tm.get(r, {}).get('worker_busy_min')) for r in runs]),
                   worker_cost_usd_median=med([num(rs[r]['worker_cost_usd']) if r in rs else None for r in runs]),
                   worker_output_tokens_median=med([num(rs[r]['worker_output']) if r in rs else None for r in runs]),
                   runs=' '.join(runs), script_commit=commit)
        row['manager'] = manager   # appended column (2026-10-17)
        out.append(row)
    with open(HERE / 'compare_pre_verdict.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    cols = [c for c in out[0] if c not in ('runs', 'script_commit')]
    with open(HERE / 'compare_pre_verdict.md', 'w') as fh:
        fh.write('# Pre-verdict comparison (Study 2 counted runs)\n\nGenerated by compare_pre_verdict.py at %s. '
                 'Fractions are k/(runs with the material). Descriptive only. Column definitions: script docstring.\n\n' % commit)
        fh.write('| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
        for r in out:
            fh.write('| ' + ' | '.join(str(r[c]) for c in cols) + ' |\n')
    print('wrote compare_pre_verdict.csv/.md', len(out), 'cells')


if __name__ == '__main__':
    main()
