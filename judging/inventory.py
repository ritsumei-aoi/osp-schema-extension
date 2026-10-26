#!/usr/bin/env python3
"""inventory.py — list every thm01 run to be judged, with the facts that can be
read mechanically from its committed files (no Worker code is run).

Reads git objects only (git ls-tree / git show); it never writes to a Worker
workspace, a shadow repository or a Manager directory.

Usage:
    python3 judging/inventory.py [--out judging/inventory.csv]
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
HERE = Path(__file__).resolve().parent
REV = HERE.parent
PUBLIC = HOME / 'notebook/git/osp-schema-extension'
INTERACTIVE = HOME / 'notebook/git/thm01-R'
SHADOW = HOME / 'notebook/git/thm01-R-shadow'
BATCH_WS = HOME / 'notebook/git/thm01-R-batch'
BATCH_REC = REV / 'runs/batch'

LAYERS = ('structure', 'gamma', 'evaluated', 'coboundary')

# May runs (submitted paper). Iterative = condition A of the paper, X = one-shot.
MAY = {
    'thm01-01': ('Gemini 3.1 Pro', 'May-Iterative'),
    'thm01-02': ('Gemini 3 Flash', 'May-Iterative'),
    'thm01-03': ('Gemini 3.1 Flash-lite', 'May-Iterative'),
    'thm01-04': ('Claude Sonnet 4.6', 'May-Iterative'),
    'thm01-05': ('GPT-5.4', 'May-Iterative'),
    'thm01-X-01': ('Gemini 3.1 Pro', 'May-OneShot'),
    'thm01-X-02': ('Gemini 3 Flash', 'May-OneShot'),
    'thm01-X-03': ('Gemini 3.1 Flash-lite', 'May-OneShot'),
    'thm01-X-04': ('Claude Sonnet 4.6', 'May-OneShot'),
    'thm01-X-05': ('GPT-5.4', 'May-OneShot'),
    'thm01-X-06': ('Claude Opus 4.6', 'May-OneShot'),
}


# Runs whose run.json says completed but which the author decided to treat as a
# mechanism-caused stop and rerun under another tag (not counted). Added 2026-10-11.
DECISION_EXCLUDE = {
    'thm01-R-gemini31p-b09-C': 'rerun as gemini31p-b11-C (reflection turn denied, author 2026-10-05)',
    'thm01-R-haiku45-b09-C': 'rerun as haiku45-b11-C (API 400 in reflection turn, author 2026-10-05)',
    'thm01-R-sonnet46-b13-C': 'rerun as sonnet46-b22-C (API 400 in reflection turn, author 2026-10-09, design 9.33)',
}
# Runs whose run.json says stopped but which are counted (author 2026-10-09 08:18 JST:
# count, note "no reflection, 2 auto-compactions", no rerun; design 9.33). Judged at final_commit.
DECISION_INCLUDE = {'thm01-R-sonnet46-b12-G'}
# Interactive runs not counted (lead 2026-10-13, author's decisions; record kept). Added 2026-10-13.
INTERACTIVE_EXCLUDE = {
    'thm01-R-gemini38f-A1': 'decision: contamination by the scribe\'s git fetch in the workspace; not counted, record kept '
                            '(author 2026-10-12, runs/thm01-R-gemini38f-A1/run_log.md; rerun as gemini38f-r2-A1)',
}
# Interactive cells prepared but not run (status not_run, not counted, no commit surveyed).
INTERACTIVE_NOT_RUN = {
    'thm01-R-gemini38f-F': 'not run: Manager Gemini 3.1 Pro retired, could not be run (author 2026-10-13, design 9.54); '
                           'run instead as gemini38f-r2-F with the successor Manager Gemini 4 Argon (Low) (design 9.56, 2026-10-16)',
}

# Manager of each run (lead 2026-10-16: model and effort only in `manager`; the harness and its version in
# `manager_harness`, so that one Manager is one value; `manager_source` = the record). Empty = no Manager
# (C, G-, One-Shot, batch). Versions not written in the run's own log are 'agy (version not recorded)';
# '1.3.1' for luna-A2 / sonnet46-F is written in the logs of their r2 runs.
_P31 = 'Gemini 3.1 Pro (Low)'
MANAGER = {
    'thm01-R-luna-A': (_P31, 'agy (version not recorded)', 'runs/thm01-R-luna-A/run_log.md:8 '
                       '("Gemini 3.1 Pro (preview)", thinking level shown as Low)'),
    'thm01-R-luna-F': (_P31, 'agy (version not recorded)', 'runs/thm01-R-luna-F/run_log.md:5, :105 '
                       '(shown as "Gemini 3.1 Pro" without "(Low)"; setting same as luna-A per the human)'),
    'thm01-R-luna-A2': (_P31, 'agy 1.3.1', 'runs/thm01-R-luna-A2/run_log.md:7; version: runs/thm01-R-luna-r2-A1/run_log.md:8'),
    'thm01-R-luna-r2-A1': (_P31, 'agy 1.3.2', 'runs/thm01-R-luna-r2-A1/run_log.md:8'),
    'thm01-R-luna-r2-A2': (_P31, 'agy (version not recorded)', 'runs/thm01-R-luna-r2-A2/run_log.md:7'),
    'thm01-R-luna-r2-F': (_P31, 'agy (version not recorded)', 'runs/thm01-R-luna-r2-F/run_log.md:7'),
    'thm01-R-luna-r3-A1': (_P31, 'agy 1.3.3', 'runs/thm01-R-luna-r3-A1/run_log.md:8 and below'),
    'thm01-R-sonnet46-A': (_P31, 'agy (version not recorded)', 'runs/thm01-R-sonnet46-A/run_log.md:6'),
    'thm01-R-sonnet46-A1': (_P31, 'agy (version not recorded)', 'runs/thm01-R-sonnet46-A1/run_log.md:6'),
    'thm01-R-sonnet46-F': (_P31, 'agy 1.3.1', 'runs/thm01-R-sonnet46-F/run_log.md:6; version: runs/thm01-R-sonnet46-r2-F/run_log.md:7'),
    'thm01-R-sonnet46-r2-A1': (_P31, 'agy (version not recorded)', 'runs/thm01-R-sonnet46-r2-A1/run_log.md:7'),
    'thm01-R-sonnet46-r2-A2': (_P31, 'agy (version not recorded)', 'runs/thm01-R-sonnet46-r2-A2/run_log.md:7'),
    'thm01-R-sonnet46-r2-F': (_P31, 'agy 1.3.2', 'runs/thm01-R-sonnet46-r2-F/run_log.md:7'),
    'thm01-R-sonnet46-r3-A1': (_P31, 'agy 1.3.3', 'runs/thm01-R-sonnet46-r3-A1/run_log.md:7 and below'),
    'thm01-R-gemini38f-A1': (_P31, 'agy 1.3.3', 'runs/thm01-R-gemini38f-A1/run_log.md:7'),
    'thm01-R-gemini38f-r2-A1': (_P31, 'agy 1.3.3', 'runs/thm01-R-gemini38f-r2-A1/run_log.md:7'),
    'thm01-R-gemini38f-F': (_P31, 'agy 1.3.3', 'runs/thm01-R-gemini38f-F/run_log.md:7 (prepared; not run)'),
    # successor Manager (design 9.56, author 2026-10-16); rows appear when the runs exist
    'thm01-R-gemini38f-r2-F': ('Gemini 4 Argon (Low)', 'agy 1.4.0', 'runs/thm01-R-gemini38f-r2-F/run_log.md:5, :35 (agy updated itself at start), :93 '
                               '("Manager の agy 1.4.0 (9 セッションとも)"); design 9.56'),
    'thm01-R-gemini38f-r3-A1': ('Gemini 4 Argon (Low)', 'agy 1.4.0', 'runs/thm01-R-gemini38f-r3-A1/run_log.md:8, :30 '
                                '(both CLIs 1.4.0 at launch); design 9.56'),
}
# Counted runs whose Worker looked outside its workspace (isolation breach; counted by the author's decision,
# recorded here only). Column `run_note`, appended. Added 2026-10-17 (lead: r3-A1 decided before its results).
RUN_NOTE = {
    'thm01-R-gemini38f-r2-A1': 'isolation breach (counted): at I05 the Worker listed <home>/notebook/git/ and a '
                               'directory there; the next read was denied by the author; resumed with a fixed reply '
                               '(runs/thm01-R-gemini38f-r2-A1/run_log.md:47-49)',
    'thm01-R-gemini38f-r3-A1': 'isolation breach (counted; author before results, design 9.56): at I03 the Worker ran '
                               '`ls -la ..` (31 names: 30 other run workspaces and its own; the 33 in run_log is the link count) and listed ../thm01-R-gemini38f-r2-A1/src/ and tests/ '
                               '(names and sizes); the read of r2-A1 src/C_generators.py was denied by the author; resumed '
                               'with "Continue." (runs/thm01-R-gemini38f-r3-A1/run_log.md:42); and at I09 (06:28:20Z) the Worker '
                               'itself ran `git fetch origin` (remote branches incl. origin/study/thm01-R-gemini38f-r2-A1 '
                               'entered its repository), after its last content commit d43243b and before the marker commit '
                               'a420a13; no content of other branches was read (Worker transcript #923; author: counted, design 9.56)',
}
# Study 1 Iterative runs: the Manager memos state "Active Manager Model: gemini-3.1-pro-preview"
# (analysis/about_thm01.md, comparative_analysis.md); the evaluation repository README (686136d, 2026-05-16)
# says "Handled by the Manager Agent (Antigravity)". IDE or CLI is not recorded.
MAY_MANAGER = ('gemini-3.1-pro-preview', 'Antigravity CLI (May)',
               'evaluation repository README.md:7 (686136d, "Manager Agent (Antigravity)"); author confirmed '
               'Antigravity CLI (agy) 2026-10-16 (lead); model: analysis/about_thm01.md Manager memos')
# Worker harness of the May runs (lead 2026-10-16: was 'Copilot CLI (May)' for all 11). Records
# (case_studies/osp-schema-extension/t1-schema-extension/analysis/):
#   thm01-01/02/03: gemini-cli /stats with 'gemini --resume' and the model rows (stats_group1.md ## thm01-01..03)
#   thm01-04/05: Copilot CLI exit summary with 'copilot --resume' (memos_group2/stats_group2.md ## thm01-04, 05)
#   thm01-X-01/02/03: gemini-cli /stats with 'gemini --resume' (memos_group3/I_X01..03_memo.md)
#   thm01-X-04: 'claude-sonnet-4.6 (GitHub Copilot CLI)' and 'copilot --resume' (memos_group3/I_X04_memo.md:4, :225)
#   thm01-X-05: 'gpt-5.4 (GitHub Copilot CLI)', 'Interface: GitHub Copilot CLI' (memos_group3/I_X05_memo.md:4, :140)
#   thm01-X-06: 'claude-opus-4.6 (Antigravity)', 'Interface: Antigravity (Custom CLI)' (memos_group3/I_X06_memo.md:4, :127)
MAY_HARNESS = {'thm01-01': 'gemini-cli (May)', 'thm01-02': 'gemini-cli (May)', 'thm01-03': 'gemini-cli (May)',
               'thm01-04': 'Copilot CLI (May)', 'thm01-05': 'Copilot CLI (May)',
               'thm01-X-01': 'gemini-cli (May)', 'thm01-X-02': 'gemini-cli (May)', 'thm01-X-03': 'gemini-cli (May)',
               'thm01-X-04': 'Copilot CLI (May)', 'thm01-X-05': 'Copilot CLI (May)',
               'thm01-X-06': 'Antigravity (May; "Custom CLI" in the memo)'}


def git(gdir, *args):
    r = subprocess.run(['git', '--git-dir', str(gdir), *args],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def resolve(gdir, ref):
    out = git(gdir, 'rev-parse', '--verify', '-q', ref + '^{commit}')
    return out.strip()[:7] if out else ''


def survey(gdir, ref):
    """Facts read from the tree at ref."""
    res = {}
    names = (git(gdir, 'ls-tree', '-r', '--name-only', ref) or '').split('\n')
    names = [n for n in names if n]
    res['files'] = len(names)
    for n in (1, 2, 3):
        for L in LAYERS:
            pat = re.compile(r'(^|/)C_%d_%s[^/]*\.json$' % (n, L))
            hits = [x for x in names if pat.search(x)]
            res['n%d_%s' % (n, L)] = len(hits)
    res['py_src'] = sum(1 for x in names if x.endswith('.py') and not x.startswith('tests/')
                        and '/tests/' not in x and not x.startswith('handover/'))
    res['py_tests'] = sum(1 for x in names if x.endswith('.py') and ('tests/' in x or Path(x).name.startswith('test_')))
    # Layer 1 (n=1) and Layer 2/4 (n=1) shape
    def load(layer):
        pat = re.compile(r'(^|/)C_1_%s[^/]*\.json$' % layer)
        hits = sorted(x for x in names if pat.search(x))
        if not hits:
            return None, ''
        txt = git(gdir, 'show', '%s:%s' % (ref, hits[0]))
        try:
            return json.loads(txt), hits[0]
        except Exception:
            return 'unparsable', hits[0]
    s, _ = load('structure')
    if isinstance(s, dict):
        res['s1_keys'] = ' '.join(sorted(s.keys()))
        res['s1_realization'] = int(any('realiz' in k.lower() for k in s.keys()))
    else:
        res['s1_keys'] = s or ''
        res['s1_realization'] = ''
    g, gname = load('gamma')
    res['gamma_file'] = gname
    res['gamma_keys'] = ' '.join(sorted(g.keys())) if isinstance(g, dict) else (g or '')
    c, cname = load('coboundary')
    res['cob_file'] = cname
    if isinstance(c, dict):
        txt = json.dumps(c)
        res['cob_phi_labels'] = int(bool(re.search(r'phi|f_param|map_param', txt)))
        res['cob_keys'] = ' '.join(sorted(c.keys()))
    else:
        res['cob_phi_labels'] = ''
        res['cob_keys'] = c or ''
    return res


def rows():
    out = []
    # 1. May runs (public repository branches)
    pg = PUBLIC / '.git'
    for run, (model, cond) in MAY.items():
        ref = 'refs/remotes/origin/study/' + run
        out.append(dict(run=run, group='may', model=model, harness=MAY_HARNESS[run],
                        condition=cond, status='completed', exclude='',
                        source=str(PUBLIC), ref_final=ref, commit_final=resolve(pg, ref),
                        ref_first='', commit_first='', uncommitted=''))
    # 2. Interactive new runs
    for ws in sorted(INTERACTIVE.iterdir()):
        run = ws.name
        cond = run.rsplit('-', 1)[-1]
        cond = {'A': 'A2' if 'sonnet46-A' == run.split('R-')[1] else 'A1'}.get(cond, cond)
        if run.endswith('-F'):
            gdir = SHADOW / (run + '.git')
            src = str(gdir)
        else:
            gdir = ws / '.git'
            src = str(ws)
        if '-luna-' in run:
            model, harness = 'GPT-6 Luna', 'Copilot CLI'
        elif '-gemini38f-' in run:
            # Worker agy interactive mode (batch gemini38f: agy 1.2.16); Manager Gemini 3.1 Pro (Low).
            # r2-F (design 9.56): Worker agy 1.3.6 (runs/thm01-R-gemini38f-r2-F/run_log.md:6, :93)
            # r3-A1 (design 9.56): Worker agy 1.4.0 (runs/thm01-R-gemini38f-r3-A1/run_log.md:6, :30)
            model, harness = 'Gemini 3.8 Flash', ('agy 1.3.6' if run.endswith('-r2-F') else
                                                  'agy 1.4.0' if run.endswith('-r3-A1') else 'agy 1.3.3')
        else:
            model, harness = 'Claude Sonnet 4.6', 'Claude Code 2.1.288'
        if run in INTERACTIVE_NOT_RUN:
            out.append(dict(run=run, group='interactive', model=model, harness=harness,
                            condition=cond, status='not_run', exclude=INTERACTIVE_NOT_RUN[run], source='',
                            ref_final='', commit_final='', ref_first='', commit_first='', uncommitted=''))
            continue
        out.append(dict(run=run, group='interactive', model=model, harness=harness,
                        condition=cond, status='completed', exclude=INTERACTIVE_EXCLUDE.get(run, ''), source=src,
                        ref_final='HEAD', commit_final=resolve(gdir, 'HEAD'),
                        ref_first='', commit_first='', uncommitted=''))
    # 3. Batch runs
    for rj in sorted(BATCH_REC.glob('*/run.json')):
        d = json.load(open(rj))
        run = d['run']
        gdir = BATCH_WS / run / '.git'
        unc = d.get('uncommitted') or []
        out.append(dict(run=run, group='batch', model=d.get('model', ''),
                        harness=d.get('harness', ''), condition=d.get('condition', ''),
                        status=d.get('status', ''),
                        exclude=('decision: ' + DECISION_EXCLUDE[run] if run in DECISION_EXCLUDE
                                 else '' if d.get('status') == 'completed' or run in DECISION_INCLUDE else 'status=' + str(d.get('status'))),
                        source=str(BATCH_WS / run),
                        ref_final=d.get('final_commit') or 'HEAD',
                        commit_final=resolve(gdir, d.get('final_commit') or 'HEAD'),
                        ref_first=d.get('first_submission_commit') or '',
                        commit_first=resolve(gdir, d['first_submission_commit']) if d.get('first_submission_commit') else '',
                        uncommitted=len(unc)))
    return out


def gitdir_of(r):
    s = Path(r['source'])
    return s if s.name.endswith('.git') else s / '.git'


def main():
    outp = HERE / 'inventory.csv'
    if '--out' in sys.argv:
        outp = Path(sys.argv[sys.argv.index('--out') + 1])
    R = rows()
    for r in R:
        gd = gitdir_of(r)
        if r['commit_final']:
            r.update(survey(gd, r['ref_final']))
        if r['commit_first'] and r['commit_first'] != r['commit_final']:
            f = survey(gd, r['ref_first'])
            r['first_vs_final_same_layers'] = int(all(f['n%d_%s' % (n, L)] == r.get('n%d_%s' % (n, L))
                                                      for n in (1, 2, 3) for L in LAYERS))
        elif r['commit_first']:
            r['first_vs_final_same_layers'] = 'same commit'
    for r in R:   # appended columns (column order of earlier versions kept)
        m = MAY_MANAGER if r['condition'] == 'May-Iterative' else MANAGER.get(r['run'], ('', '', ''))
        r['manager'], r['manager_harness'], r['manager_source'] = m
        r['run_note'] = RUN_NOTE.get(r['run'], '')
    keys = []
    for r in R:
        for k in r:
            if k not in keys:
                keys.append(k)
    mk = ['manager', 'manager_harness', 'manager_source', 'run_note']
    keys = [k for k in keys if k not in mk] + mk
    with open(outp, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(R)
    print('wrote', outp, len(R), 'runs')


if __name__ == '__main__':
    main()
