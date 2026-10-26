#!/usr/bin/env python3
"""make_release.py — the judging/ part of the public record (design §9.58; lead request 2026-10-24).

Writes (judging/release/):
  FILES.txt           the judging/ paths to publish (relative to judging/), one per line, from INCLUDE below;
                      everything tracked in judging/ that is not listed is excluded (reasons in EXCLUDED below).
  inventory_public.csv  run, branch, final_commit, status (counted / excluded: reason / not run: reason),
                      verdict (the author's final verdict, decoded), verdict_at_reveal (before the predictions
                      were revealed, judgments.csv at post_verdict.REVEAL_COMMIT), condition, model, harness,
                      manager, manager_harness, run_note.
  judging/            the staged copies of the FILES.txt files (same relative paths) with the home path replaced
                      (design 9.58 (5), author 2026-10-25): '<home>' -> '<home>', '<home>/notebook' -> '<home>/notebook';
                      the folder structure after the home is kept. Text files, CSV/JSON and the members of the .tar.gz
                      files are rewritten; the original files in judging/ are not changed. The record branch takes this copy.
  scan.txt            hits of the checks for content unsuitable for publication over the staged copies (except
                      this script, which contains the check patterns)
                      (and the members of the .tar.gz files): e-mail addresses, home-directory paths, key-like
                      strings, quotes of the referee report.
It also regenerates the decoded copies (decode_author.py) so the published judgments are the decoded ones.

Usage: python3 judging/release/make_release.py
"""
import csv
import io
import re
import subprocess
import sys
import tarfile
from pathlib import Path

REL = Path(__file__).resolve().parent
J = REL.parent
REV = J.parent
sys.path.insert(0, str(J))
import author_codes   # noqa: E402
import post_verdict   # noqa: E402

INCLUDE = [
    # judgments (decoded copies; the codes table and the decoder)
    'judgments_decoded.csv', 'fix_judgments_decoded.csv', 'manager_review_check_decoded.csv',
    'author_codes.py', 'decode_author.py', 'build_fix_judgments.py',
    # frozen prediction and rules, earlier verdicts
    'predict.py', 'predictions.csv', 'prior.csv',
    # facts given to the author
    'build_sheet.py', 'sheet.csv', 'sheet.md', 'verdict_basis.py', 'verdict_basis.csv',
    'extract_spec.md', 'facts/', 'facts2/', 'readings_spec.md', 'readings/', 'readings_fix/',
    'agent_scripts.tar.gz', 'agent_scripts_stage2.tar.gz',
    # script checks (gamma, ranks, n = 4)
    'gcheck/', 'g_summary.py', 'g_summary.csv', 'g_summary.md', 'g4_summary.py', 'g4_summary.csv', 'g4_summary.md',
    'n4_spec.md', 'n4/', 'n4_summary.py', 'n4_summary.csv', 'n4_summary.md', 'reference_n4.txt', 'fix_gcheck.csv',
    # error stages, process, Manager claims
    'error_trace_spec.md', 'error_trace/', 'error_trace_summary.py', 'error_trace_summary.csv', 'error_trace_summary.md',
    'interactive_process_spec.md', 'process/',
    'manager_review_spec.md', 'manager_review/', 'manager_review_summary.py', 'manager_review_summary.csv',
    'manager_review_summary.md', 'manager_review_check.py',
    # surveys of the artifacts and the harness
    'code_survey.py', 'code_survey.csv', 'structure_survey.py', 'structure_survey.csv',
    'kit_edits.py', 'kit_edits.csv', 'kit_edits_summary.md', 'harness_items.py', 'harness_items.csv',
    'harness_items_groups.csv', 'timing.py', 'timing.csv', 'timing_issues.csv', 'timing_may.csv', 'timing_summary.md',
    'resources.py', 'resources.csv', 'inventory.py',
    # after the verdicts
    'post_verdict.py', 'verdict_cells.csv', 'verdict_vs_prediction.csv', 'fix_verdicts.csv', 'manager_check_summary.csv',
    'compare_pre_verdict.py', 'compare_pre_verdict.csv', 'compare_pre_verdict.md',
    # this directory
    'release/make_release.py', 'release/inventory_public.csv', 'release/README_judging.md',
]
EXCLUDED = {
    'judgments.csv / fix_judgments.csv / manager_review_check.csv': 'raw entries (codes); the decoded copies are published',
    'inventory.csv': 'contains local paths; replaced by release/inventory_public.csv',
    'jtool.py, JTOOL.md, JUDGING_GUIDE.md, make_copies.py': "the author's local working tools",
    'README.md, PROPOSALS.md, notes_*.md': 'working notes between sessions (decisions are in the design log, published)',
    'resources_scribe.md': "the scribe's own token use, not a study result",
    'literature/': 'literature surveys for the manuscript (quotes of third-party papers)',
    '.gitignore': 'not needed',
}


def tracked():
    out = subprocess.run(['git', '-C', str(J), 'ls-files', '.'], capture_output=True, text=True).stdout.split()
    return out


def files():
    t = tracked()
    sel = []
    for pat in INCLUDE:
        if pat.endswith('/'):
            sel += [f for f in t if f.startswith(pat)]
        elif pat in t or pat.startswith('release/'):
            sel.append(pat)
        else:
            raise SystemExit('listed but not tracked: ' + pat)
    return sorted(set(sel))


def inventory():
    inv = list(csv.DictReader(open(J / 'inventory.csv')))
    j = {(r['run'], r['commit_checked']): r for r in csv.DictReader(open(J / 'judgments.csv'))}
    at = subprocess.run(['git', '-C', str(J), 'show', '%s:./judgments.csv' % post_verdict.REVEAL_COMMIT],
                        capture_output=True, text=True).stdout
    at = {(r['run'], r['commit_checked']): r for r in csv.DictReader(io.StringIO(at))}
    rows = []
    for i in inv:
        run = i['run']
        if i['status'] == 'not_run':
            status = 'not run: ' + i['exclude'].replace('not run: ', '')
        elif i['exclude']:
            status = 'excluded: ' + re.sub(r'^(decision: |status=)', '', i['exclude'])
        else:
            status = 'counted'
        k = (run, 'final')
        rows.append(dict(run=run, branch='study/' + run, final_commit=i['commit_final'], status=status,
                         verdict=author_codes.value('author_verdict', j.get(k, {}).get('author_verdict', '')),
                         verdict_at_reveal=author_codes.value('author_verdict', at.get(k, {}).get('author_verdict', '')),
                         condition=i['condition'], model=i['model'], harness=i['harness'], manager=i.get('manager', ''),
                         manager_harness=i.get('manager_harness', ''), run_note=mask(i.get('run_note', '')),
                         group=i['group']))
    with open(REL / 'inventory_public.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print('wrote inventory_public.csv', len(rows))


CHECKS = [
    ('email', re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')),
    ('home path', re.compile(r'/Users/[A-Za-z0-9_.-]+|<home>/notebook|-Users-[A-Za-z0-9_.]+-')),
    ('user name', re.compile(r'\baoi\b')),
    ('key-like', re.compile(r'AIza[0-9A-Za-z_-]{20,}|sk-ant-[0-9A-Za-z_-]{10,}|ghp_[0-9A-Za-z]{20,}|ya29\.[0-9A-Za-z_-]{10,}|refresh_token|BEGIN [A-Z ]*PRIVATE KEY')),
    ('referee', re.compile(r'referee|Reviewer ?[12]\b|査読', re.I)),
]


def referee_sentences():
    p = REV / 'referee_report_IPSJ.txt'
    if not p.exists():
        return []
    txt = p.read_text(errors='replace')
    return [s.strip() for s in re.split(r'[.\n]', txt) if len(s.strip()) > 60][:400]


def scan(paths):
    refs = referee_sentences()
    hits = {}
    def check(name, text):
        for tag, rx in CHECKS:
            ms = sorted(set(m.group(0) for m in rx.finditer(text)))
            if ms:
                hits.setdefault(tag, {}).setdefault(name, ms[:5] + (['... %d more' % (len(ms) - 5)] if len(ms) > 5 else []))
        for s in refs:
            if s[:60] in text:
                hits.setdefault('referee quote', {}).setdefault(name, []).append(s[:60])
    # the staged copies, plus the top-level release/ files that the record branch takes as they are
    extra = ['release/' + n for n in ('inventory_public.csv', 'FILES.txt', 'README_judging.md')]
    for f in list(paths) + ['TOP:' + e for e in extra]:
        if f.endswith('release/make_release.py'):   # contains the check patterns themselves
            continue
        p = (J / f[4:]) if f.startswith('TOP:') else (REL / 'judging' / f)
        if not p.exists():
            continue
        if f.endswith('.tar.gz'):
            with tarfile.open(p) as t:
                for m in t.getmembers():
                    if m.isfile():
                        check(f + '!' + m.name, t.extractfile(m).read().decode('utf-8', 'replace'))
        else:
            check(f, p.read_text(errors='replace'))
    with open(REL / 'scan.txt', 'w') as fh:
        for tag in [c[0] for c in CHECKS] + ['referee quote']:
            fh.write('== %s: %d files\n' % (tag, len(hits.get(tag, {}))))
            for name, ms in sorted(hits.get(tag, {}).items()):
                fh.write('  %s: %s\n' % (name, ' | '.join(ms)))
    print('wrote scan.txt', {t: len(v) for t, v in hits.items()})


HOME_RULES = [('<home>', '<home>'), ('<home>/notebook', '<home>/notebook'),
              # the same home path encoded in Claude Code scratch-directory names (/private/tmp/claude-501/-<home>-...)
              ('-<home>-', '-<home>-')]


# also the shortened forms found in summary cells: '<home>' and a cell cut after '/Users/a'
HOME_TAIL = re.compile(r'/Users/(?:\.\.\.|a(?=["\s,]|$))', re.M)


def mask(text):
    for a, b in HOME_RULES:
        text = text.replace(a, b)
    return HOME_TAIL.sub('<home>', text)


def stage(paths):
    """Copy the files to release/judging/ with the home path replaced (tar.gz members rewritten)."""
    out = REL / 'judging'
    # files are overwritten in place; nothing is deleted. Staged files no longer in the list are reported.
    if out.exists():
        stale = [str(q.relative_to(out)) for q in out.rglob('*') if q.is_file() and str(q.relative_to(out)) not in paths]
        if stale:
            print('staged files not in FILES.txt (remove by hand if wanted):', stale)
    for f in paths:
        src, dst = J / f, out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        if f.endswith('.tar.gz'):
            with tarfile.open(src) as tin, tarfile.open(dst, 'w:gz') as tout:
                for m in tin.getmembers():
                    if m.isfile():
                        data = mask(tin.extractfile(m).read().decode('utf-8', 'surrogateescape')).encode('utf-8', 'surrogateescape')
                        m.size = len(data)
                        tout.addfile(m, io.BytesIO(data))
                    else:
                        tout.addfile(m)
        else:
            dst.write_text(mask(src.read_text(encoding='utf-8', errors='surrogateescape')),
                           encoding='utf-8', errors='surrogateescape')
    print('staged', len(paths), 'files in release/judging/')
    return out


def main():
    subprocess.run([sys.executable, '-I', str(J / 'decode_author.py')], check=True)
    inventory()
    fs = files()
    with open(REL / 'FILES.txt', 'w') as fh:
        fh.write('\n'.join(fs) + '\n')
    print('wrote FILES.txt', len(fs))
    stage(fs)
    scan(fs)


if __name__ == '__main__':
    main()
