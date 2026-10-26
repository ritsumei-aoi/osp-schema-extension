#!/usr/bin/env python3
"""resources.py — AI resource use per run (Worker and Manager), facts only.

Sources
- batch runs: runs/batch/<run>/run.json, summed over turns
  (Claude Code: usage tokens and cost_usd_list_price; agy: usage tokens;
  Copilot: premiumRequests, model_calls; seconds per turn).
- interactive Claude Code Workers: `ccusage claude session` with
  CLAUDE_CONFIG_DIR=<home>/notebook/git/thm01-R-claude-config/<name> (all sessions there,
  incl. -retry dirs of the same run).
- Managers with a run-specific HOME (sonnet46-A, -A1, -F): `ccusage antigravity session`.
- interactive agy Workers (gemini38f-r2-A1, added 2026-10-13): `ccusage antigravity session` with
  HOME=<home>/notebook/git/thm01-R-agy-home/worker-<run> (read only); Manager as above.
- Human interventions: count of "## Human memo" in the Manager memo.
Not available: May runs; luna interactive runs (shared Copilot / agy HOME).

Token columns: input (non-cache), cache_write, cache_read, output, total. Costs are
API list-price equivalents (Claude: Claude Code's own figure for batch, ccusage
otherwise; agy: ccusage) — NOT what was paid (subscriptions / quotas).

Usage: python3 judging/resources.py   (writes judging/resources.csv)
"""
import csv
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent
HOMEDIR = Path.home()
CFG = HOMEDIR / 'notebook/git/thm01-R-claude-config'
AGY = HOMEDIR / 'notebook/git/thm01-R-agy-home'
MGR = HOMEDIR / 'notebook/git/thm01-R-managers'


def ccusage(kind, env):
    e = dict(os.environ, **env)
    r = subprocess.run(['ccusage', kind, 'session', '--offline', '--json'], capture_output=True, text=True, env=e)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def tot_from_ccusage(d):
    if not d:
        return None
    t = d.get('totals') or {}
    ss = d.get('sessions', [])
    return dict(input=t.get('inputTokens', 0), cache_write=t.get('cacheCreationTokens', 0),
                cache_read=t.get('cacheReadTokens', 0), output=t.get('outputTokens', 0),
                total=t.get('totalTokens', 0), cost_usd=round(t.get('totalCost', 0), 2), sessions=len(ss))


def batch_row(d):
    s = dict(input=0, cache_write=0, cache_read=0, output=0, total=0, cost_usd=0.0, seconds=0,
             premium_requests='', model_calls='')
    pr = mc = 0
    for t in d.get('turns', []):
        u = t.get('usage') or {}
        s['seconds'] += t.get('seconds') or 0
        if 'premiumRequests' in u:          # Copilot
            pr += u.get('premiumRequests') or 0
            mc += t.get('model_calls') or 0
            continue
        if 'cache_read_input_tokens' in u:  # Claude Code
            s['input'] += u.get('input_tokens', 0)
            s['cache_write'] += u.get('cache_creation_input_tokens', 0)
            s['cache_read'] += u.get('cache_read_input_tokens', 0)
            s['output'] += u.get('output_tokens', 0)
            s['cost_usd'] += t.get('cost_usd_list_price') or 0
        else:                               # agy
            s['input'] += u.get('input_tokens', 0)
            s['cache_read'] += u.get('cache_read_tokens', 0)
            s['output'] += u.get('output_tokens', 0) + u.get('thinking_tokens', 0)
    s['total'] = s['input'] + s['cache_write'] + s['cache_read'] + s['output']
    s['cost_usd'] = round(s['cost_usd'], 2) if s['cost_usd'] else ''
    if pr or mc:
        s['premium_requests'], s['model_calls'] = pr, mc
        for k in ('input', 'cache_write', 'cache_read', 'output', 'total'):
            s[k] = ''
    return s


def human_memos(run):
    for p in (REV / 'runs' / run / 'manager_memo.md',
              MGR / run / 'memos' / run / 'manager_memo.md'):
        if p.exists():
            return p.read_text().count('## Human memo')
    return ''


def main():
    inv = list(csv.DictReader(open(HERE / 'inventory.csv')))
    rows = []
    for r in inv:
        run = r['run']
        row = dict(run=run, group=r['group'], model=r['model'], condition=r['condition'], exclude=r['exclude'])
        w = m = None
        note = []
        if r['group'] == 'batch':
            d = json.load(open(REV / 'runs/batch' / run / 'run.json'))
            w = batch_row(d)
            if d.get('home') and 'agy-home' in d['home']:
                note.append('agy totals from run.json (thinking counted as output)')
        elif r['group'] == 'interactive' and '-sonnet46-' in run:
            name = run.replace('thm01-R-', '')
            dirs = [p for p in CFG.glob(name + '*') if p.name == name or p.name.startswith(name + '-retry')]
            acc = None
            for p in dirs:
                t = tot_from_ccusage(ccusage('claude', {'CLAUDE_CONFIG_DIR': str(p)}))
                if t:
                    acc = t if acc is None else {k: acc[k] + t[k] for k in acc}
            w = acc
            if len(dirs) > 1:
                note.append('incl. %s' % ', '.join(p.name for p in dirs if p.name != name))
            h = AGY / ('manager-' + run)
            if h.exists():
                m = tot_from_ccusage(ccusage('antigravity', {'HOME': str(h)}))
        elif r['group'] == 'interactive' and '-gemini38f-' in run and r['status'] != 'not_run' \
                and (AGY / ('worker-' + run)).exists():
            w = tot_from_ccusage(ccusage('antigravity', {'HOME': str(AGY / ('worker-' + run))}))
            h = AGY / ('manager-' + run)
            if h.exists():
                m = tot_from_ccusage(ccusage('antigravity', {'HOME': str(h)}))
            note.append('agy interactive Worker (run-specific HOME)')
        elif r['group'] == 'interactive' and (REV / 'runs' / run / 'copilot_session').exists() \
                and (AGY / ('manager-' + run)).exists():
            # run-specific COPILOT_HOME (luna-A2 onward): every Worker session saved
            w = dict(input=0, cache_write=0, cache_read=0, output=0, total=0, sessions=0,
                     premium_requests=0, model_calls='')
            aiu = 0.0
            for f in sorted((REV / 'runs' / run / 'copilot_session').glob('*/events.jsonl')):
                sh = None
                for line in open(f):
                    e = json.loads(line)
                    if e.get('type') == 'session.shutdown':
                        sh = e.get('data') or {}
                if not sh:
                    continue
                w['premium_requests'] += sh.get('totalPremiumRequests') or 0
                aiu += (sh.get('totalNanoAiu') or 0) / 1e9
                for mm in (sh.get('modelMetrics') or {}).values():
                    u = mm.get('usage', mm)
                    if u.get('inputTokens'):
                        w['sessions'] += 1
                    w['input'] += (u.get('inputTokens') or 0) - (u.get('cacheReadTokens') or 0) - (u.get('cacheWriteTokens') or 0)
                    w['cache_write'] += u.get('cacheWriteTokens') or 0
                    w['cache_read'] += u.get('cacheReadTokens') or 0
                    w['output'] += u.get('outputTokens') or 0
            w['total'] = w['input'] + w['cache_write'] + w['cache_read'] + w['output']
            note.append('Copilot run-specific home: AIU %.2f; Copilot inputTokens include cache (split here)' % aiu)
            m = tot_from_ccusage(ccusage('antigravity', {'HOME': str(AGY / ('manager-' + run))}))
        elif r['status'] == 'not_run':
            note.append('not run')
        else:
            note.append('usage not separable (May run or shared Copilot/agy home)')
        for prefix, v in (('worker_', w), ('manager_', m)):
            for k in ('input', 'cache_write', 'cache_read', 'output', 'total', 'cost_usd', 'sessions',
                      'seconds', 'premium_requests', 'model_calls'):
                if v and k in v:
                    row[prefix + k] = v[k]
        row['human_memos'] = human_memos(run) if r['condition'] in ('A1', 'A2', 'F') else ''
        row['note'] = '; '.join(note)
        rows.append(row)
    keys = []
    if (HERE / 'resources.csv').exists():   # keep the existing column order
        keys = [k for k in next(csv.reader(open(HERE / 'resources.csv'))) if any(k in r for r in rows)]
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(HERE / 'resources.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, restval='')
        w.writeheader()
        w.writerows(rows)
    print('wrote resources.csv', len(rows), datetime.now().isoformat(timespec='minutes'))


if __name__ == '__main__':
    main()
