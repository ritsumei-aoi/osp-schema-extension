#!/usr/bin/env python3
"""predict.py — mechanical (rule-based) prediction of the verdict, for comparison
with the author's judgment. Reference only; never used as a judgment.

The prediction is computed from sheet.csv columns by fixed rules (RULES_VERSION).
It is frozen into judgments.csv before the author starts judging (design §9.29);
later changes of the rules must use a new version and a new column, so that the
recorded prediction stays comparable with the human verdict.

Rules v1 (first matching rule decides; the reason lists every feature used):
  R0  status not completed (exclude set)                        -> excluded
  R1  no computation code (computation/test_range text says so: no computation,
      no linear algebra, hand-written dicts, static dictionaries, stub,
      placeholder data)                                          -> fail
  R2  no stated conclusion (stated_class 'none')                 -> fail
  R2b no triviality test at all (test range 'none')              -> fail
  R2c the triviality test uses only K components (K-only, no non-K
      comparison; reevaluation.md §2.4)                          -> fail
  Runs with γ checked by gcheck (G, A, F, May-Iterative):
  R3  γ unreadable (placeholder etc.)                            -> fail
  R4  K-dependent: stated 'trivial iff gb=0' while the run's own
      γ with K dropped does not imply it (criterion (b))         -> fail
  R5  stated class matches neither data_implies (K dropped / kept) -> fail
  R6  γ identical to a reference up to overall sign, test range
      'joint', and no theory contradiction with strong evidence  -> pass
  R7  otherwise                                                  -> insufficient
  Runs without γ check (C, May-OneShot):
  R8  test range 'joint' and no theory contradiction with strong
      evidence and no reported rank mismatch                     -> pass
  R9  otherwise                                                  -> insufficient
Strong evidence = validated_reference, run_own_code_or_data, definition_docs,
own_other_statement, logs (not agent_unvalidated, not not_checked).
Work items and remark_readings are not used (remark only).

Calibration note: rules-v1 was written while looking at the 26 earlier verdicts
(prior.csv), so agreement on those 26 rows is not independent evidence of accuracy.

Usage: python3 judging/predict.py   (writes judging/predictions.csv)
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_VERSION = 'rules-v1 (2026-10-07)'
STRONG = ('validated_reference', 'run_own_code_or_data', 'definition_docs', 'own_other_statement', 'logs')
NO_COMP = re.compile(r'no computation|no code (that )?comput|no code computes|is a stub|only a stub|'
                     r'placeholder|dummy code|no linear algebra|hand-written dict|static dictionar|'
                     r'no bracket/normal-ordering', re.I)
NO_JOINT = re.compile(r'\bno\b[^.;]{0,30}\bjoint|not joint|no (joint/)?combination', re.I)


def says_no_computation(text):
    """NO_COMP match that is not negated ('no placeholder', 'not a stub')."""
    for m in NO_COMP.finditer(text):
        before = text[max(0, m.start() - 14):m.start()].lower()
        if m.group(0).lower().startswith('no ') or not re.search(r'\b(no|not)\b', before):
            return True
    return False


def tr_summary(text):
    """The test-range text without its evidence part (JSON 'summary' if present)."""
    t = text.strip()
    if t.startswith('{'):
        try:
            import json
            d = json.loads(t)
            return str(d.get('summary', t))
        except ValueError:
            pass
    return t.split(' -- ')[0]


def cls(text):
    t = text.lower()
    if t.startswith('all'):
        return 'all'
    if 'iff' in t and not t.startswith('cond'):
        return 'iff0'
    if t.startswith('cond'):
        return 'cond'
    if t.startswith('none') or not t.strip():
        return 'none'
    return 'other'


def strong_theory(items):
    n = 0
    for line in items.split('\n'):
        m = re.match(r'\[(\w+); (\w+)\]', line)
        if m and m.group(1) == 'contradiction' and m.group(2) in STRONG:
            n += 1
    return n


def predict(r):
    feats = []
    if r['exclude']:
        return 'excluded', 'R0 ' + r['exclude']
    comp = r['computation']
    st = cls(r['stated_class'])
    sth = strong_theory(r['theory_items'])
    trs = tr_summary(r['test_range'])
    trl = trs.lower()
    joint = bool(re.search(r'\bjoint\b', trl)) and not NO_JOINT.search(trs)
    k_only = trl.startswith('k-only') or 'only the k components' in trl or 'only k components' in trl
    none_test = trl.startswith('none') or trl.startswith('no computation')
    feats = ['stated=%s' % st, 'joint=%s' % joint, 'strong_theory_contradictions=%d' % sth]
    comp_txt = re.sub(r'"?hardcoded_or_placeholder"?\s*:?\s*("none found"|none found)?', '', comp)
    if says_no_computation(comp_txt[:400]) or says_no_computation(trs[:40]):
        return 'fail', 'R1 no computation code; ' + '; '.join(feats)
    if st == 'none':
        return 'fail', 'R2 no stated conclusion; ' + '; '.join(feats)
    if none_test:
        return 'fail', 'R2b no triviality test; ' + '; '.join(feats)
    if k_only and not joint:
        return 'fail', 'R2c K-only test; ' + '; '.join(feats)
    if r['gamma_vs_ref_n1'] or r['data_implies_n1']:
        g = r['gamma_vs_ref_n1']
        imp = r['data_implies_n1']
        nonk, _, kk = imp.partition(' / ')
        feats += ['gamma=%s' % (g[:12] or '-'), 'implies=%s' % imp]
        if g.startswith('unreadable') or not imp.strip(' -/'):
            return 'fail', 'R3 gamma unreadable; ' + '; '.join(feats)
        if st == 'iff0' and nonk and not nonk.startswith('trivial iff'):
            return 'fail', 'R4 K-dependent (own γ with K dropped does not give iff gb=0); ' + '; '.join(feats)
        want = {'all': 'all gb trivial', 'iff0': 'trivial iff gb=0'}.get(st)
        if want and want not in (nonk, kk):
            return 'fail', 'R5 stated conclusion not implied by own data; ' + '; '.join(feats)
        exact = g[:1] in '=-'
        if exact and joint and sth == 0:
            return 'pass', 'R6; ' + '; '.join(feats)
        return 'insufficient', 'R7 (exact_gamma=%s); ' % exact + '; '.join(feats)
    mismatch = bool(re.search(r"(does not|doesn't|do not) match|mismatch|not reproduce", r['reported_numbers'], re.I))
    feats.append('reported_rank_mismatch=%s' % mismatch)
    if joint and sth == 0 and not mismatch:
        return 'pass', 'R8; ' + '; '.join(feats)
    return 'insufficient', 'R9; ' + '; '.join(feats)


def main():
    rows = list(csv.DictReader(open(HERE / 'sheet.csv', newline='')))
    out = []
    for r in rows:
        v, why = predict(r)
        out.append(dict(run=r['run'], commit_checked=r['commit_checked'], predicted_verdict=v,
                        predicted_reason=why, predicted_rules=RULES_VERSION))
    with open(HERE / 'predictions.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print('wrote predictions.csv', len(out), Counter(o['predicted_verdict'] for o in out))


if __name__ == '__main__':
    main()
