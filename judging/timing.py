#!/usr/bin/env python3
"""timing.py — wall-clock time per run (facts only), for batch and interactive R runs.
May runs are in timing_may.csv (extracted separately from git and Copilot statistics).

Batch runs (runs/batch/<run>/run.json): start = 'started', end = 'finished',
  worker_busy = sum of turn 'seconds' (the harness waits for nothing else, so
  span - busy is only harness overhead between turns).
Interactive R runs: events from the saved Worker sessions (Claude Code jsonl in
  runs/<run>/claude_session/**, Copilot events.jsonl in runs/<run>/copilot_session/
  or ~/.copilot/session-state/<id>/ found by workspace cwd; agy interactive (gemini38f-r2-A1,
  added 2026-10-13): runs/<run>/agy_store_worker.tar.gz, human inputs = history.jsonl entries
  (timestamp, display), Worker events = creation time of every step in conversations/*.db
  except the user-input steps (step_type 14) and any step stamped in the same second as a
  human input (agy creates them at submission)
  (protobuf metadata field 1.1, seconds)), the Worker's git
  commits (<home>/notebook/git/thm01-R/<run>), and the Manager directory's git
  snapshots (<home>/notebook/git/thm01-R-managers/<run>, or the shared
  <home>/notebook/git/thm01-R-manager for luna-A / luna-F, commits whose subject
  starts with the run's short name).
  start = first human message to the Worker; end = last event of any kind
  (Worker, Worker commit, Manager snapshot).
  span = end - start (includes every wait and pause).
  active = span minus every gap > GAP_MIN minutes between consecutive events
  (overnight pauses, quota waits, breaks); the gaps are listed.
  worker_busy = sum over human messages of (last Worker event before the next
  human message - the human message); waiting = span - worker_busy (time spent
  by the Manager, the human and the scribe, plus pauses).
  human_inputs = messages typed into the Worker (incl. answers to selection
  prompts); sessions = Worker sessions with at least one human message.
Per-issue rows for condition A (timing_issues.csv): an issue starts at the human
  message that begins with the fixed start prompt ("You are an execution agent",
  or "Congratulations" for I09) and ends at the next one (or the run end).

Usage: python3 judging/timing.py   (writes judging/timing.csv, judging/timing_issues.csv)
"""
import csv
import json
import re
import sqlite3
import subprocess
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent
HOME = Path.home()
WS = HOME / 'notebook/git/thm01-R'
MGRS = HOME / 'notebook/git/thm01-R-managers'
MGR_SHARED = HOME / 'notebook/git/thm01-R-manager'
COPILOT = HOME / '.copilot/session-state'
GAP_MIN = 30
JST = timezone(timedelta(hours=9))


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def claude_events(run):
    """[(t, kind, text)] kind: human / worker"""
    out = []
    for f in sorted((REV / 'runs' / run / 'claude_session').rglob('*.jsonl')):
        for line in open(f):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get('type') not in ('user', 'assistant') or not e.get('timestamp'):
                continue
            t = ts(e['timestamp'])
            c = e['message'].get('content')
            if e['type'] == 'assistant':
                out.append((t, 'worker', ''))
            elif isinstance(c, str):
                if not c.startswith('<'):
                    out.append((t, 'human', c))
            elif isinstance(c, list):
                if any(x.get('type') == 'tool_result' for x in c):
                    out.append((t, 'worker', ''))
                else:
                    txt = ' '.join(x.get('text', '') for x in c if x.get('type') == 'text')
                    if txt and not txt.startswith('<') and not txt.startswith('[Request interrupted'):
                        out.append((t, 'human', txt))
    return out


def copilot_files(run):
    saved = REV / 'runs' / run / 'copilot_session'
    files = sorted(saved.glob('*/events.jsonl')) if saved.exists() else []
    if not files and COPILOT.exists():
        for w in COPILOT.glob('*/workspace.yaml'):
            m = re.search(r'^cwd: (.*)$', w.read_text(), re.M)
            if m and m.group(1).strip() == str(WS / run):
                files.append(w.parent / 'events.jsonl')
    return files


def copilot_events(run):
    out = []
    for f in copilot_files(run):
        if not f.exists():
            continue
        ask = set()
        for line in open(f):
            e = json.loads(line)
            t = ts(e['timestamp'])
            ty, d = e['type'], e.get('data') or {}
            if ty == 'user.message':
                out.append((t, 'human', d.get('content', '')))
            elif ty == 'tool.execution_start' and d.get('toolName') == 'ask_user':
                ask.add(d.get('toolCallId'))
                out.append((t, 'worker', ''))
            elif ty == 'tool.execution_complete' and d.get('toolCallId') in ask:
                out.append((t, 'human', 'ask_user answer'))
            elif ty.startswith('assistant.') or ty.startswith('tool.'):
                out.append((t, 'worker', ''))
    return out


def _varint(b, i):
    r = sh = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7f) << sh
        sh += 7
        if c < 0x80:
            return r, i


def _pb_created(b):
    """Seconds in field 1 -> field 1 of an agy step's metadata (protobuf Timestamp), or None."""
    i = 0
    while i < len(b):
        k, i = _varint(b, i)
        f, t = k >> 3, k & 7
        if t == 0:
            _, i = _varint(b, i)
        elif t == 2:
            n, i = _varint(b, i)
            if f == 1:
                sub, j = b[i:i + n], 0
                while j < len(sub):
                    k2, j = _varint(sub, j)
                    if k2 >> 3 == 1 and k2 & 7 == 0:
                        return _varint(sub, j)[0]
                    return None
            i += n
        elif t == 1:
            i += 8
        elif t == 5:
            i += 4
        else:
            return None
    return None


def agy_events(run):
    """Worker in agy interactive mode (saved store runs/<run>/agy_store_worker.tar.gz)."""
    tf = REV / 'runs' / run / 'agy_store_worker.tar.gz'
    if not tf.exists():
        return [], 0
    out, convs = [], set()
    with tarfile.open(tf) as t, tempfile.TemporaryDirectory() as tmp:
        for m in t.getmembers():
            if m.isfile() and m.name.endswith('antigravity-cli/history.jsonl'):
                for line in t.extractfile(m).read().decode().splitlines():
                    e = json.loads(line)
                    out.append((datetime.fromtimestamp(e['timestamp'] / 1000, timezone.utc), 'human', e.get('display', '')))
            elif m.isfile() and '/conversations/' in m.name and m.name.endswith('.db'):
                fn = Path(tmp) / Path(m.name).name
                fn.write_bytes(t.extractfile(m).read())
                convs.add(fn.stem)
                try:
                    steps = list(sqlite3.connect(fn).execute('select metadata from steps where step_type != 14'))
                except sqlite3.DatabaseError:   # unreadable saved db (gemini38f-A1): human inputs only
                    steps = []
                for (md,) in steps:
                    sec = _pb_created(md or b'')
                    if sec:
                        out.append((datetime.fromtimestamp(sec, timezone.utc), 'worker', ''))
    # Steps stamped in the same second as a human input belong to that input (agy records the
    # input with step types 14 / 101 / 15 at submission; second resolution), not to the work before it.
    hsec = {int(e[0].timestamp()) for e in out if e[1] == 'human'}
    out = [e for e in out if e[1] == 'human' or int(e[0].timestamp()) not in hsec]
    return out, len(convs)


def git_times(repo, prefix=None):
    if not (repo / '.git').exists():
        return []
    r = subprocess.run(['git', '-C', str(repo), 'log', '--all', '--format=%cI %s'], capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        t, _, s = line.partition(' ')
        if prefix is None or s.startswith(prefix):
            out.append(ts(t))
    return out


def analyse(run, ev, extra):
    ev = sorted(ev, key=lambda x: x[0])
    humans = [e for e in ev if e[1] == 'human']
    if not humans:
        return None, []
    start = humans[0][0]
    alltimes = sorted([e[0] for e in ev] + [t for t in extra if t >= start])
    end = alltimes[-1]
    gaps = []
    for a, b in zip(alltimes, alltimes[1:]):
        if (b - a).total_seconds() > GAP_MIN * 60:
            gaps.append((a, b))
    busy = 0.0
    for i, h in enumerate(humans):
        nxt = humans[i + 1][0] if i + 1 < len(humans) else end + timedelta(seconds=1)
        w = [e[0] for e in ev if e[1] == 'worker' and h[0] <= e[0] < nxt]
        if w:
            busy += (max(w) - h[0]).total_seconds()
    span = (end - start).total_seconds()
    gap_s = sum((b - a).total_seconds() for a, b in gaps)
    row = dict(start=start.astimezone(JST).isoformat(timespec='minutes'),
               end=end.astimezone(JST).isoformat(timespec='minutes'),
               span_min=round(span / 60, 1), active_min=round((span - gap_s) / 60, 1),
               worker_busy_min=round(busy / 60, 1), waiting_min=round((span - busy) / 60, 1),
               human_inputs=len(humans),
               gaps_over_30min=' ; '.join('%s→%s (%dm)' % (a.astimezone(JST).strftime('%m-%d %H:%M'),
                                                           b.astimezone(JST).strftime('%m-%d %H:%M'),
                                                           (b - a).total_seconds() // 60) for a, b in gaps))
    issues = []
    starts = [h for h in humans if h[2].startswith('You are an execution agent') or h[2].startswith('Congratulations on completing')]
    for k, h in enumerate(starts):
        e2 = starts[k + 1][0] if k + 1 < len(starts) else end
        m = re.search(r'Issue (I0\d)', h[2])
        iss = m.group(1) if m else ('I09' if h[2].startswith('Congratulations') else '?')
        hs = [x for x in humans if h[0] <= x[0] < e2]
        issues.append(dict(run=run, issue=iss, start=h[0].astimezone(JST).isoformat(timespec='minutes'),
                           end=e2.astimezone(JST).isoformat(timespec='minutes'),
                           span_min=round((e2 - h[0]).total_seconds() / 60, 1), human_inputs=len(hs)))
    return row, issues


def main():
    inv = list(csv.DictReader(open(HERE / 'inventory.csv')))
    rows, issue_rows = [], []
    for r in inv:
        run = r['run']
        base = dict(run=run, group=r['group'], model=r['model'], condition=r['condition'], exclude=r['exclude'])
        if r['group'] == 'batch':
            d = json.load(open(REV / 'runs/batch' / run / 'run.json'))
            st, fi = ts(d['started']), ts(d.get('finished') or d['started'])
            busy = sum(t.get('seconds') or 0 for t in d.get('turns', []))
            rows.append(dict(base, start=st.astimezone(JST).isoformat(timespec='minutes'),
                             end=fi.astimezone(JST).isoformat(timespec='minutes'),
                             span_min=round((fi - st).total_seconds() / 60, 1),
                             active_min=round((fi - st).total_seconds() / 60, 1),
                             worker_busy_min=round(busy / 60, 1),
                             waiting_min=round(((fi - st).total_seconds() - busy) / 60, 1),
                             human_inputs=0, sessions=1, turns=len(d.get('turns', [])),
                             source='run.json', note='automatic; waiting = harness overhead between turns'))
            continue
        if r['group'] != 'interactive':
            continue
        cfiles = copilot_files(run)
        aev, aconv = agy_events(run)
        ev = claude_events(run) + copilot_events(run) + aev
        short = run.replace('thm01-R-', '')
        extra = git_times(WS / run)
        if (MGRS / run).exists():
            extra += git_times(MGRS / run)
            mgr = 'thm01-R-managers/%s' % run
        elif r['condition'] in ('A1', 'A2', 'F'):
            extra += git_times(MGR_SHARED, short + ' ') + git_times(MGR_SHARED, short + ':')
            mgr = 'thm01-R-manager (shared, subject prefix %s)' % short
        else:
            mgr = ''
        row, iss = analyse(run, ev, extra)
        if row is None:
            rows.append(dict(base, note='no Worker session record found'))
            continue
        nsess = len({f.parent.name for f in cfiles}) if cfiles else aconv or len(list((REV / 'runs' / run / 'claude_session').rglob('*.jsonl')))
        src = 'copilot events (%d files)' % len(cfiles) if cfiles else 'agy store (history.jsonl, conversation steps)' if aconv else 'claude_session jsonl'
        rows.append(dict(base, **row, sessions=nsess, source='; '.join(x for x in (src, 'worker git', mgr) if x),
                         note='interactive; span includes all waits and pauses'))
        if r['condition'] in ('A1', 'A2'):
            issue_rows += iss
    keys = []
    for x in rows:
        keys += [k for k in x if k not in keys]
    with open(HERE / 'timing.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, restval='')
        w.writeheader()
        w.writerows(rows)
    with open(HERE / 'timing_issues.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(issue_rows[0]))
        w.writeheader()
        w.writerows(issue_rows)
    print('wrote timing.csv (%d rows), timing_issues.csv (%d rows)' % (len(rows), len(issue_rows)))


if __name__ == '__main__':
    main()
