#!/usr/bin/env python3
"""harness_items.py — facts for the harness-view evaluation (design §9.37, §9.40).
Facts only; it never judges. Writes two files:

harness_items.csv (one row per run of inventory.csv, May runs included but mostly blank):
  run, group, model, harness, condition, effort, exclude
  fixed_replies, denial_replies   batch run.json (A/F: blank, human-gated)
  outside_refs, uncommitted       batch run.json, number of entries
  permission_denials_logged       Claude Code batch: sum of len(permission_denials) in the
                                  'result' message of each turn (the Worker was refused a tool
                                  call and went on; run.json denial_replies counts only the
                                  harness's replies when a turn ended on a refusal). Others:
                                  'not recorded'
  auto_compactions                count of automatic context compactions, or
                                  'not recorded' when the log format has no marker:
                                  Claude Code: system/compact_boundary with trigger=auto
                                  (batch turn*.jsonl.gz, interactive runs/<run>/claude_session/*.jsonl);
                                  Copilot interactive: session.compaction_complete in
                                  runs/<run>/copilot_session/**/events.jsonl;
                                  agy interactive (gemini38f, 2026-10-13): conversation steps of
                                  type 23 in runs/<run>/agy_store_worker.tar.gz (inferred: the only
                                  one in gemini38f-r2-A1 coincides with the compaction in run_log);
                                  Copilot batch (-p stream) and agy batch: no marker -> 'not recorded'
  compaction_source               which log was counted
  reflection_committed            final copy has docs/issues/final_reflection.md (or any
                                  *reflection*.md) — 'yes' / 'no'
  kit_reference_edits, kit_template_edits, kit_config_edits   from kit_edits.csv (counts)
  reading_adopted, ambiguity_level, escalated_at_gate
                                  from readings/*.jsonl (readings_spec.md; subagent extraction,
                                  author confirms): '<gb_parity>/<kappa_sign>/<K_handling>',
                                  level 0-3, yes/no/mixed (A/F only)
  paper_reading                   reading_adopted mapped to the paper's two readings (design
                                  §9.40 3, author 2026-10-12, fixed before judging):
                                  odd/*/* -> odd-gb, even/supercommuting/dropped -> even-gb,
                                  anything else -> other
  procedure_notes, failure_attribution
                                  filled later (§9.37 4, 5, attribution); kept if already filled
  author_verdict                  copied from judgments.csv for viewing (first row of the run)
  script_commit                   evaluation-repository HEAD when the table was made

harness_items_groups.csv (one row per group x model_id x harness_family x effort x condition,
  counted runs only; harness_family = 'Claude Code <version>' (2.1.288 vs 2.1.293 is a design
  control, §9.32), 'agy' or 'Copilot CLI' (minor versions differ inside a series; see per-run rows);
  model_id maps the interactive display names to API ids):
  n_counted, n_judged, n_pass (author_verdict = code 1 or 'pass', read by author_codes),
  pass_k1, pass_k3, pass_k5 (unbiased C(c,k)/C(n,k), §9.40;
  blank until every counted run of the group has an author_verdict; blank when n < k),
  reading_distribution, top_reading_share, n_reading_types (blank until reading_adopted is filled),
  paper_reading_distribution (odd-gb / even-gb / other counts), manager (appended 2026-10-17: the Manager
  model of interactive gated runs splits cells, e.g. Gemini 3.1 Pro (Low) vs Gemini 4 Argon (Low))

Usage: JROOT=<jroot> python3 judging/harness_items.py
"""
import csv
import glob
import gzip
import json
import os
import subprocess
from collections import Counter, defaultdict
from math import comb
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import author_codes   # noqa: E402  (numeric codes of author_*, 2026-10-14)

HERE = Path(__file__).resolve().parent
REV = HERE.parent
JROOT = Path(os.environ['JROOT'])


def claude_compactions(lines):
    n = 0
    for ln in lines:
        if '"compact_boundary"' not in ln:
            continue
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        if d.get('subtype') == 'compact_boundary' and (d.get('compact_metadata') or {}).get('trigger') == 'auto':
            n += 1
    return n


def compactions(run, inv):
    rec = REV / 'runs' / 'batch' / run
    if (rec / 'run.json').exists():
        h = inv['harness']
        if 'Claude Code' in h:
            n = 0
            for f in sorted(rec.glob('turn*.jsonl.gz')):
                with gzip.open(f, 'rt', errors='replace') as fh:
                    n += claude_compactions(fh)
            return n, 'batch turn*.jsonl.gz compact_boundary'
        return 'not recorded', 'no compaction marker in %s batch log' % h.split()[0]
    d = REV / 'runs' / run
    cs = sorted(d.glob('claude_session/*.jsonl'))
    if cs:
        n = 0
        for f in cs:
            with open(f, errors='replace') as fh:
                n += claude_compactions(fh)
        return n, 'claude_session/*.jsonl compact_boundary'
    ev = sorted(glob.glob(str(d / 'copilot_session' / '**' / 'events.jsonl'), recursive=True))
    if ev:
        n = 0
        for f in ev:
            with open(f, errors='replace') as fh:
                n += sum(1 for ln in fh if '"type":"session.compaction_complete"' in ln)
        return n, 'copilot_session events.jsonl session.compaction_complete'
    tf = d / 'agy_store_worker.tar.gz'
    if tf.exists():   # agy interactive (gemini38f, added 2026-10-13)
        import sqlite3, tarfile, tempfile
        n, ok = 0, False
        with tarfile.open(tf) as t, tempfile.TemporaryDirectory() as tmp:
            for m in t.getmembers():
                if m.isfile() and '/conversations/' in m.name and m.name.endswith('.db') \
                        and not Path(m.name).name.startswith('._'):
                    fn = Path(tmp) / Path(m.name).name
                    fn.write_bytes(t.extractfile(m).read())
                    try:
                        n += sqlite3.connect(fn).execute('select count(*) from steps where step_type = 23').fetchone()[0]
                        ok = True
                    except sqlite3.DatabaseError:
                        pass
        if ok:
            return n, ('agy store conversation steps of type 23 (taken as compaction: the one such step in '
                       'gemini38f-r2-A1 is at the start of I06, where run_log records "Conversation compacted")')
        return 'not recorded', 'agy store conversation db unreadable'
    return 'not recorded', 'no saved Worker session'


def denials_logged(run, inv):
    rec = REV / 'runs' / 'batch' / run
    if not (rec / 'run.json').exists() or 'Claude Code' not in inv['harness']:
        return 'not recorded'
    n = 0
    for f in sorted(rec.glob('turn*.jsonl.gz')):
        with gzip.open(f, 'rt', errors='replace') as fh:
            for ln in fh:
                if '"permission_denials"' not in ln:
                    continue
                try:
                    d = json.loads(ln)
                except ValueError:
                    continue
                if d.get('type') == 'result':
                    n += len(d.get('permission_denials') or [])
    return n


def reflection(run):
    d = JROOT / 'final' / run
    if not d.exists():
        return ''
    if (d / 'docs/issues/final_reflection.md').exists():
        return 'yes'
    return 'yes' if any('reflection' in p.name.lower() for p in d.rglob('*.md')) else 'no'


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


def paper_reading(t):
    """Design §9.40 3 (author 2026-10-12, fixed before judging)."""
    if not t:
        return ''
    gb, kappa, K = (t.split('/') + ['', '', ''])[:3]
    if gb == 'odd':
        return 'odd-gb'
    if (gb, kappa, K) == ('even', 'supercommuting', 'dropped'):
        return 'even-gb'
    return 'other'


def main():
    inv = list(csv.DictReader(open(HERE / 'inventory.csv')))
    kit = {r['run']: r for r in csv.DictReader(open(HERE / 'kit_edits.csv'))}
    verdict = {}
    for r in csv.DictReader(open(HERE / 'judgments.csv')):
        verdict.setdefault(r['run'], r['author_verdict'])
    commit = subprocess.run(['git', '-C', str(REV), 'rev-parse', '--short', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    old = {}
    if (HERE / 'harness_items.csv').exists():
        old = {r['run']: r for r in csv.DictReader(open(HERE / 'harness_items.csv'))}
    LATER = ('procedure_notes', 'failure_attribution')
    readings = {}
    for f in sorted((HERE / 'readings').glob('*.jsonl')):
        for ln in open(f):
            if ln.strip():
                d = json.loads(ln)
                readings[d['run']] = d

    def label(d, k):
        v = d.get(k, '')
        if isinstance(v, dict):
            v = v.get('value', '')
        return '' if v is None else str(v).strip()
    rows = []
    for i in inv:
        run = i['run']
        rj = REV / 'runs' / 'batch' / run / 'run.json'
        d = json.load(open(rj)) if rj.exists() else {}
        comp, src = compactions(run, i) if i['group'] != 'may' else ('not recorded', 'May run')
        k = kit.get(run, {})
        row = dict(run=run, group=i['group'], model=i['model'], harness=i['harness'].split('\n')[0],
                   condition=i['condition'], effort=d.get('effort') or '', exclude=i['exclude'],
                   fixed_replies=d.get('fixed_replies', ''), denial_replies=d.get('denial_replies', ''),
                   outside_refs=len(d['outside_refs']) if 'outside_refs' in d else '',
                   uncommitted=len(d['uncommitted']) if 'uncommitted' in d else '',
                   permission_denials_logged=denials_logged(run, i),
                   auto_compactions=comp, compaction_source=src, reflection_committed=reflection(run),
                   kit_reference_edits=int(k.get('reference_modified') or 0) + int(k.get('reference_deleted') or 0) if k else '',
                   kit_template_edits=int(k.get('template_modified') or 0) + int(k.get('template_deleted') or 0) if k else '',
                   kit_config_edits=int(k.get('config_modified') or 0) + int(k.get('config_deleted') or 0) if k else '')
        rd = readings.get(run)
        row['reading_adopted'] = '/'.join(label(rd, k) for k in ('gb_parity', 'kappa_sign', 'K_handling')) if rd else ''
        row['paper_reading'] = paper_reading(row['reading_adopted'])
        row['ambiguity_level'] = label(rd, 'ambiguity_level') if rd else ''
        row['escalated_at_gate'] = label(rd, 'escalated_at_gate') if rd else ''
        for c in LATER:   # keep values filled in earlier
            row[c] = old.get(run, {}).get(c, '')
        row['author_verdict'] = verdict.get(run, '')
        row['script_commit'] = commit
        rows.append(row)
    with open(HERE / 'harness_items.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    groups = defaultdict(list)
    mgr = {i['run']: i.get('manager', '') for i in inv}   # Manager separates cells (lead 2026-10-16/17, design 9.56)
    for r in rows:
        if r['exclude'] or r['group'] == 'may':
            continue
        groups[(r['group'], MODEL_ID.get(r['model'], r['model']), family(r['harness']),
                r['effort'], r['condition'], mgr.get(r['run'], ''))].append(r)
    out = []
    for (grp, model, harness, effort, cond, manager), rs in sorted(groups.items()):
        n = len(rs)
        judged = [r for r in rs if r['author_verdict']]
        c = sum(1 for r in judged if author_codes.value('author_verdict', r['author_verdict']) == 'pass')
        g = dict(group=grp, model_id=model, harness_family=harness, effort=effort, condition=cond, n_counted=n,
                 n_judged=len(judged), n_pass=c if judged else '')
        for kk in (1, 3, 5):
            g['pass_k%d' % kk] = (round(comb(c, kk) / comb(n, kk), 4)
                                  if len(judged) == n and n >= kk else '')
        reads = Counter(r['reading_adopted'] for r in rs if r['reading_adopted'])
        g['reading_distribution'] = '; '.join('%s=%d' % kv for kv in reads.most_common())
        g['top_reading_share'] = round(reads.most_common(1)[0][1] / n, 3) if reads else ''
        g['n_reading_types'] = len(reads) if reads else ''
        pr = Counter(r['paper_reading'] for r in rs if r['paper_reading'])
        g['paper_reading_distribution'] = '; '.join('%s=%d' % (k, pr[k]) for k in ('odd-gb', 'even-gb', 'other') if pr[k])
        g['runs'] = ' '.join(r['run'] for r in rs)
        g['script_commit'] = commit
        g['manager'] = manager   # appended column (2026-10-17)
        out.append(g)
    with open(HERE / 'harness_items_groups.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print('wrote harness_items.csv', len(rows), 'harness_items_groups.csv', len(out))


if __name__ == '__main__':
    main()
