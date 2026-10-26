#!/usr/bin/env python3
"""kit_edits.py — did the Worker modify or delete files it was given (the kit)?
Facts only (mechanical comparison); no judgment.

Distributed files of a run:
  - R runs (batch, interactive, F): experiment/manifests/<run>.txt (sha256 of every
    file placed at build time). Compared with the final copy $JROOT/final/<run>/
    (git archive of the final commit; for F the shadow repository's last snapshot).
  - May runs: the files of the last "init:"/"setup:" commit before the Worker's
    first commit on the run branch (public repository), compared with the final
    commit of the branch.
Each distributed file is classed:
  reference  — definitions and workflow rules / scripts (docs/math/*, handover/*
               except the two below): not meant to be edited by the Worker;
  template   — final_reflection_template.md, supplementary_metrics_template.md,
               docs/issues/template_issue_open.md (edited = filled in place instead
               of copied);
  config     — pytest.ini, .gitignore, requirements.txt;
  working    — files the workflow asks the Worker to edit (handover/notation.md,
               handover/handover_memo_latest.md, docs/issues/*, .gitkeep).
Output per run: counts and the lists of modified / deleted files of each class.
For modified reference files the size of the change (lines added/removed, by diff)
is given.

Usage: JROOT=<scratchpad>/jroot python3 judging/kit_edits.py   (writes judging/kit_edits.csv)
"""
import csv
import difflib
import hashlib
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = HERE.parent
JROOT = Path(os.environ['JROOT'])
MAN = REV / 'experiment/manifests'
WORKING_PREFIX = ('docs/issues/',)
WORKING_FILES = {'handover/notation.md', 'handover/handover_memo_latest.md'}


TEMPLATES = {'final_reflection_template.md', 'supplementary_metrics_template.md', 'docs/issues/template_issue_open.md'}
CONFIG = {'pytest.ini', '.gitignore', 'requirements.txt'}


def klass(path):
    if path in TEMPLATES:
        return 'template'
    if path in CONFIG:
        return 'config'
    if path in WORKING_FILES or path.startswith(WORKING_PREFIX) or path.endswith('.gitkeep'):
        return 'working'
    return 'reference'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def manifest(run):
    f = MAN / (run + '.txt')
    if not f.exists():
        return None
    out = {}
    for line in f.read_text().splitlines():
        if line.startswith('#') or not line.strip():
            continue
        h, path = line.split(None, 1)
        out[path[2:] if path.startswith('./') else path] = h
    return out


def git(gd, *a, raw=False):
    out = subprocess.run(['git', '--git-dir', str(gd)] + list(a), capture_output=True).stdout
    return out if raw else out.decode('utf-8', 'replace')


def may_base(gd, ref):
    log = git(gd, 'log', '--format=%H %s', '--reverse', ref).splitlines()
    base = None
    for line in log:
        h, _, s = line.partition(' ')
        if s.startswith(('init:', 'setup:')):
            base = h
        elif base:
            break
    return base


def linediff(a, b):
    d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm='', n=0))
    return (sum(1 for x in d if x.startswith('+') and not x.startswith('+++')),
            sum(1 for x in d if x.startswith('-') and not x.startswith('---')))


def main():
    rows = []
    for r in csv.DictReader(open(HERE / 'inventory.csv')):
        run = r['run']
        root = JROOT / 'final' / run
        res = dict(run=run, group=r['group'], model=r['model'], condition=r['condition'], exclude=r['exclude'])
        mod = {k: [] for k in ('reference', 'template', 'config', 'working')}
        dele = {k: [] for k in ('reference', 'template', 'config', 'working')}
        if r['group'] == 'may':
            src = Path(r['source'])
            gd = src / '.git'
            base = may_base(gd, r['ref_final'])
            res['baseline'] = 'commit %s' % (base or '?')[:7]
            if not base:
                rows.append(dict(res, note='no init/setup commit found'))
                continue
            files = [x for x in git(gd, 'ls-tree', '-r', '--name-only', base).splitlines()]
            for path in files:
                old = git(gd, 'show', '%s:%s' % (base, path), raw=True)
                newp = root / path
                if not newp.exists():
                    dele[klass(path)].append(path)
                    continue
                new = newp.read_bytes()
                if new != old:
                    k = klass(path)
                    if k != 'working':
                        a, d = linediff(old.decode('utf-8', 'replace'), new.decode('utf-8', 'replace'))
                        mod[k].append('%s (+%d/-%d)' % (path, a, d))
                    else:
                        mod[k].append(path)
        else:
            m = manifest(run)
            if m is None:
                rows.append(dict(res, note='no manifest'))
                continue
            res['baseline'] = 'manifest %s.txt' % run
            src = Path(r['source'])
            gd = src if src.name.endswith('.git') else src / '.git'
            roots = git(gd, 'rev-list', '--max-parents=0', 'HEAD').split()
            first = roots[-1] if roots else None
            for path, h in m.items():
                p = root / path
                if not p.exists():
                    dele[klass(path)].append(path)
                elif sha(p) != h:
                    k = klass(path)
                    old = git(gd, 'show', '%s:%s' % (first, path), raw=True) if first else b''
                    if k != 'working' and old and hashlib.sha256(old).hexdigest() == h:
                        a, d = linediff(old.decode('utf-8', 'replace'), p.read_bytes().decode('utf-8', 'replace'))
                        mod[k].append('%s (+%d/-%d)' % (path, a, d))
                    else:
                        mod[k].append(path)
        out = dict(res)
        for k in ('reference', 'template', 'config', 'working'):
            out[k + '_modified'] = len(mod[k])
            out[k + '_deleted'] = len(dele[k])
        for k in ('reference', 'template', 'config'):
            out[k + '_modified_files'] = ' ; '.join(mod[k])
            out[k + '_deleted_files'] = ' ; '.join(dele[k])
        out['working_deleted_files'] = ' ; '.join(dele['working'])
        rows.append(out)
    keys = []
    for x in rows:
        keys += [k for k in x if k not in keys]
    with open(HERE / 'kit_edits.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, restval='')
        w.writeheader()
        w.writerows(rows)
    print('wrote kit_edits.csv', len(rows))


if __name__ == '__main__':
    main()
