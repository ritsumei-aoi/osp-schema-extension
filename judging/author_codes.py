"""author_codes.py — the numeric codes the author may type in the author_* columns, and their values.

Table agreed by the author on 2026-10-14 (lead: notes/author_input_codes.md, 087210b). The author may write
either the number or the English value; text may follow after '; ' (e.g. '3; Fabrication', '2; theory 1, 3').
The author's cells are never rewritten: scripts call decode() when they count, and decode_author.py writes
the decoded copies (judgments_decoded.csv, manager_review_check_decoded.csv).

Accepted forms of a cell (leading/trailing spaces ignored; full-width digits and '；' are read as ASCII):
  'N'  /  'N; text'  /  'N text'          N = a code of the column
  'value'  /  'value; text'  /  'value: text'  /  'value text'   value = an English value of the column
Anything else is reported by jtool.check() (warning only) and decodes to value ''.
"""
import re
import unicodedata

CODES = {
    # judgments.csv
    'author_verdict': {'1': 'pass', '2': 'insufficient', '3': 'fail', '4': 'excluded'},
    'author_result': {'1': 'pass', '2': 'insufficient', '3': 'fail', '4': 'n/a'},
    'author_argument': {'1': 'no error', '2': 'error', '3': 'unchecked'},
    'author_interpretation': {'1': 'odd-gb', '2': 'even-gb', '3': 'both stated', '4': 'inconsistent',
                              '5': 'K-dependent', '6': 'n/a'},
    # manager_review_check.csv
    'author_agree': {'1': 'yes', '2': 'no', '3': 'unsure'},
    'author_kind': {'1': 'M1-false', '2': 'M2-unverified', '3': 'M3-added', '4': 'ok'},   # only when agree = no
}
JUDGMENT_COLS = ['author_verdict', 'author_result', 'author_argument', 'author_interpretation']
REVIEW_COLS = ['author_agree', 'author_kind']

_NUM = re.compile(r'^(\d+)\s*(?:;\s*|\s+|$)(.*)$', re.S)


def decode(col, raw):
    """(value, text, ok) of one cell. value is the English value ('' if empty or not recognised),
    text is what follows the code or value, ok is False only for a non-empty cell not recognised."""
    s = unicodedata.normalize('NFKC', raw or '').strip()
    if not s:
        return '', '', True
    table = CODES[col]
    m = _NUM.match(s)
    if m:
        v = table.get(m.group(1))
        return (v, m.group(2).strip(), True) if v else ('', s, False)
    # longest first, so that 'no error' is not read as 'no' and 'error' is not matched inside 'no error'
    for v in sorted(table.values(), key=len, reverse=True):
        if s.lower() == v.lower() or (s.lower().startswith(v.lower()) and s[len(v)] in ';: \t'):
            return v, s[len(v):].lstrip(';: \t').strip(), True
    return '', s, False


def value(col, raw):
    """The English value only ('' if empty or not recognised)."""
    return decode(col, raw)[0]


def display(col, raw):
    """'value; text' (or the raw cell, marked '?', if not recognised) — for tables shown to the reader."""
    v, t, ok = decode(col, raw)
    if not ok:
        return '?' + (raw or '').strip()
    return '%s; %s' % (v, t) if v and t else v
