#!/usr/bin/env python3
"""decode_author.py — copies of the author's files with the numeric codes replaced by English values
(table: author_codes.py, agreed 2026-10-14). The author's files are read only; their author_* cells stay
as written.

Output (all columns of the source, unchanged, plus for each coded column <col>_value and <col>_text, and
decode_warnings listing cells that are neither a code nor a value):
  judgments_decoded.csv             from judgments.csv (author_verdict, author_result, author_argument,
                                    author_interpretation; author_note is free text and not decoded)
  fix_judgments_decoded.csv         from fix_judgments.csv (fixed versions of the fix experiment; same columns)
  manager_review_check_decoded.csv  from manager_review_check.csv (author_agree, author_kind; also a
                                    warning when author_kind is given but author_agree is not 'no')
Generated files: do not edit; rerun after every change of the author's files (jtool.decode_files()).

Usage: python3 judging/decode_author.py
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import author_codes   # noqa: E402


def decode_file(src, dst, cols):
    with open(HERE / src, newline='') as fh:
        rd = csv.DictReader(fh)
        hdr, rows = list(rd.fieldnames), list(rd)
    out_cols = hdr + [c + suf for c in cols for suf in ('_value', '_text')] + ['decode_warnings']
    nwarn = 0
    for r in rows:
        warn = []
        for c in cols:
            v, t, ok = author_codes.decode(c, r.get(c, ''))
            r[c + '_value'], r[c + '_text'] = v, t
            if not ok:
                warn.append('%s not recognised: %r' % (c, r[c]))
        if 'author_kind' in cols and r.get('author_kind', '').strip() and r['author_agree_value'] != 'no':
            warn.append('author_kind given but author_agree is not no')
        r['decode_warnings'] = '; '.join(warn)
        nwarn += bool(warn)
    with open(HERE / dst, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=out_cols)
        w.writeheader()
        w.writerows(rows)
    filled = sum(1 for r in rows if any(r.get(c, '').strip() for c in cols))
    print('wrote %s: %d rows, %d with entries, %d with warnings' % (dst, len(rows), filled, nwarn))


def main():
    decode_file('judgments.csv', 'judgments_decoded.csv', author_codes.JUDGMENT_COLS)
    if (HERE / 'fix_judgments.csv').exists():
        decode_file('fix_judgments.csv', 'fix_judgments_decoded.csv', author_codes.JUDGMENT_COLS)
    if (HERE / 'manager_review_check.csv').exists():
        decode_file('manager_review_check.csv', 'manager_review_check_decoded.csv', author_codes.REVIEW_COLS)


if __name__ == '__main__':
    main()
