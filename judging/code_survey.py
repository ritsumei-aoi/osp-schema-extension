#!/usr/bin/env python3
"""code_survey.py — rough, mechanical survey of the code each run produced
(reusability proxies), on the git-archive copies. Facts only; no judgment.

Per run (final commit): Python files written by the Worker (excluding the kit:
handover/, templates, docs/math), lines, functions, classes, main guard, command
line parameters, whether n is a parameter/loop, tests, absolute paths, libraries,
code only inside Markdown blocks, and where the code lives.

Usage: JROOT=<scratchpad>/jroot python3 judging/code_survey.py
writes judging/code_survey.csv
"""
import ast
import csv
import os
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
JROOT = Path(os.environ['JROOT'])
KIT = ('handover/', 'docs/math/', '.github/')


def worker_py(root):
    for p in sorted(root.rglob('*.py')):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(KIT) or '__pycache__' in rel or 'template' in rel:
            continue
        yield rel, p


def survey(run, root):
    d = defaultdict(int)
    dirs, libs = set(), set()
    for rel, p in worker_py(root):
        try:
            src = p.read_text(errors='replace')
        except OSError:
            continue
        is_test = '/tests/' in '/' + rel or Path(rel).name.startswith('test_')
        d['py_tests' if is_test else 'py_files'] += 1
        d['loc'] += sum(1 for l in src.splitlines() if l.strip() and not l.strip().startswith('#'))
        dirs.add(rel.split('/')[0] if '/' in rel else '.')
        if re.search(r'/Users/|/home/|/private/tmp|["\']/tmp/', src):
            d['abs_path_files'] += 1
        if "__name__" in src and "__main__" in src:
            d['main_guard'] += 1
        if 'argparse' in src or 'sys.argv' in src:
            d['cli_args'] += 1
        if re.search(r'for\s+n\s+in|range\(1,\s*4\)|\[1,\s*2,\s*3\]|def \w+\([^)]*\bn\b', src):
            d['n_param'] += 1
        for m in re.finditer(r'^\s*(?:import|from)\s+(sympy|numpy|scipy|fractions|mpmath)', src, re.M):
            libs.add(m.group(1))
        try:
            tree = ast.parse(src)
        except SyntaxError:
            d['syntax_error'] += 1
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if is_test and node.name.startswith('test'):
                    d['test_funcs'] += 1
                else:
                    d['functions'] += 1
                    if ast.get_docstring(node):
                        d['functions_doc'] += 1
            elif isinstance(node, ast.ClassDef):
                d['classes'] += 1
    md_blocks = 0
    for p in root.rglob('*.md'):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(KIT) or 'template' in rel:
            continue
        md_blocks += len(re.findall(r'```python', p.read_text(errors='replace')))
    json_files = sum(1 for p in root.rglob('*.json') if not p.relative_to(root).as_posix().startswith(KIT))
    readme = any(p.name.lower().startswith('readme') and not p.relative_to(root).as_posix().startswith(KIT)
                 for p in root.rglob('*'))
    return dict(py_files=d['py_files'], py_tests=d['py_tests'], loc=d['loc'], functions=d['functions'],
                functions_doc=d['functions_doc'], classes=d['classes'], main_guard=d['main_guard'],
                cli_args=d['cli_args'], n_param=d['n_param'], test_funcs=d['test_funcs'],
                abs_path_files=d['abs_path_files'], syntax_error=d['syntax_error'],
                md_python_blocks=md_blocks, json_files=json_files, readme_beyond_kit=int(readme),
                libs=' '.join(sorted(libs)), code_dirs=' '.join(sorted(dirs)))


def main():
    inv = list(csv.DictReader(open(HERE / 'inventory.csv')))
    sheet = {(r['run'], r['commit_checked']): r for r in csv.DictReader(open(HERE / 'sheet.csv'))}
    rows = []
    for r in inv:
        root = JROOT / 'final' / r['run']
        if not root.exists():
            continue
        s = survey(r['run'], root)
        rr = sheet.get((r['run'], 'final'), {}).get('rerun', '')
        rows.append(dict(run=r['run'], model=r['model'], condition=r['condition'], exclude=r['exclude'],
                         rerun_excerpt=' '.join(rr.split())[:120], **s))
    keys = list(rows[0])
    with open(HERE / 'code_survey.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print('wrote code_survey.csv', len(rows))


if __name__ == '__main__':
    main()
