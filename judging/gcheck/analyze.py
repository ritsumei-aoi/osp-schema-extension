"""Gamma comparison and rank check (generalized from analysis_scripts/flash_gamma for judging/).

usage: python3 analyze.py [n ...] [--runs run1,run2]   (default n=1 2)
writes results_n<N>.json next to this file and prints a summary.

Conventions
- Pairs: every dict {(X,Y,Z): c} is canonicalized to ordered pairs (X,Y) with
  index(X) <= index(Y) in the Worker basis; a missing canonical entry is filled
  from the recorded reverse pair via graded antisymmetry
  c(Y,X,Z) = -(-1)^{p(X)p(Y)} c(X,Y,Z). Pairs recorded in both orders whose
  values violate this relation are counted ('antisym_conflicts'); the canonical
  value is used.
- Reference: refmodel.WorkerBasisRef (independent_triviality4 definitions with the
  Worker's generator realizations). sign=True: kappa supercommutes; sign=False: kappa commutes.
- nonK: entries with Z != 'K'; K: entries with Z == 'K'.
"""
import json, os, sys
from fractions import Fraction as F
from loader import (ALL_RUNS, VERSION, load_gamma, load_coboundary, load_structure, evaluated_info, gbparse)
from refmodel import WorkerBasisRef

HERE = os.path.dirname(os.path.abspath(__file__))


def canon(D, basis, parity):
    idx = {g: i for i, g in enumerate(basis)}
    byp = {}
    for (X, Y, Z), c in D.items():
        byp.setdefault((X, Y), {})[Z] = c
    out, conflicts = {}, 0
    for (X, Y), zs in byp.items():
        if idx[X] <= idx[Y]:
            for Z, c in zs.items():
                if c: out[(X, Y, Z)] = c
    for (X, Y), zs in byp.items():
        if idx[X] > idx[Y]:
            s = -(-1) ** (parity[X] * parity[Y])
            if (Y, X) in byp:
                other = byp[(Y, X)]
                conflicts += sum(1 for Z in set(zs) | set(other) if s * zs.get(Z, 0) != other.get(Z, 0))
            else:
                for Z, c in zs.items():
                    if c: out[(Y, X, Z)] = s * c
    return out, conflicts


def split(D, withK):
    return {k: v for k, v in D.items() if (k[2] == 'K') == withK}


def classify(ref, w):
    """ref, w: canonical dicts. Returns dict of counts and relation."""
    keys = set(ref) | set(w)
    match = sum(1 for k in keys if k in ref and k in w and ref[k] == w[k])
    missing = sum(1 for k in keys if k in ref and k not in w)
    extra = sum(1 for k in keys if k not in ref and k in w)
    differ = sum(1 for k in keys if k in ref and k in w and ref[k] != w[k])
    negated = sum(1 for k in keys if k in ref and k in w and ref[k] == -w[k])
    if not keys:
        rel = 'both empty'
    elif not w:
        rel = 'worker empty'
    elif not ref:
        rel = 'ref empty'
    elif missing == 0 and extra == 0:
        ratios = {w[k] / ref[k] for k in keys}
        rel = ('identical' if ratios == {1} else 'negated' if ratios == {-1}
               else 'scaled x%s' % next(iter(ratios)) if len(ratios) == 1 else 'different')
    else:
        rel = 'different'
    return dict(rel=rel, ref=len(ref), worker=len(w), match=match, missing=missing,
                extra=extra, differ=differ, differ_negated=negated)


def rank_report(R, A_cols, G_by_p, withK):
    """A_cols: list of canonical dicts; G_by_p: {p: canonical dict}. Drops K rows unless withK."""
    f = (lambda d: d) if withK else (lambda d: split(d, False))
    A = [f(c) for c in A_cols]
    rA = R.rank(A)
    G = [f(G_by_p.get(p, {})) for p in R.gb_params]
    rAG = R.rank(A + G)
    per = {str(p): R.rank(A + [g]) - rA for p, g in zip(R.gb_params, G)}
    return dict(rankA=rA, rankAG=rAG, rankG=R.rank(G), per_direction_increase=per,
                n_dirs_trivial=sum(1 for v in per.values() if v == 0), n_cols=len(A))


def analyze(run, n):
    res = dict(run=run, version=VERSION[run], n=n)
    basis, parity, real, sc_w = load_structure(run, n)
    R = WorkerBasisRef(n, basis, parity, real)
    res['basis'] = basis
    # consistency of the Worker's own structure constants with its realizations
    sc_r = R.structure_constants()
    scd_w = {(X, Y, Z): c for (X, Y), d in sc_w.items() for Z, c in d.items()}
    scd_r = {(X, Y, Z): c for (X, Y), d in sc_r.items() for Z, c in d.items()}
    cw, _ = canon(scd_w, basis, parity); cr, _ = canon(scd_r, basis, parity)
    res['structure_constants_vs_realization'] = classify(cr, cw)
    res['undeformed_K_components_from_realization'] = sum(1 for k in scd_r if k[2] == 'K')

    Gw_raw, ginfo = load_gamma(run, n)
    res['gamma_file'] = ginfo
    res['evaluated_file'] = evaluated_info(run, n)
    Aw_raw, cinfo = load_coboundary(run, n)
    res['coboundary_file'] = cinfo

    Gw, conf = {}, 0
    if Gw_raw:
        for p, D in Gw_raw.items():
            Gw[p], c = canon(D, basis, parity); conf += c
        res['gamma_params'] = sorted(map(str, Gw_raw))
        res['gamma_pairs_recorded'] = len({(X, Y) for D in Gw_raw.values() for (X, Y, _z) in D})
        res['gamma_entries_nonK'] = sum(1 for D in Gw_raw.values() for k in D if k[2] != 'K')
        res['gamma_entries_K'] = sum(1 for D in Gw_raw.values() for k in D if k[2] == 'K')
        res['gamma_antisym_conflicts'] = conf

    Gref = {}
    res['gamma_cmp'] = {}
    for sign in (True, False):
        Gref[sign] = {p: canon(R.gamma(p, sign), basis, parity)[0] for p in R.gb_params}
        if not Gw_raw:
            continue
        for withK in (False, True):
            per = {str(p): classify(split(Gref[sign][p], withK), split(Gw.get(p, {}), withK))
                   for p in R.gb_params}
            tot = {k: sum(v[k] for v in per.values()) for k in
                   ('ref', 'worker', 'match', 'missing', 'extra', 'differ', 'differ_negated')}
            rels = sorted({v['rel'] for v in per.values()})
            res['gamma_cmp']['%s_%s' % ('super' if sign else 'none', 'K' if withK else 'nonK')] = dict(
                per_param=per, total=tot, relations=rels)

    # ranks
    Aind = [canon(c, basis, parity)[0] for c in R.coboundary_columns().values()]
    res['rank'] = {}
    for withK in (False, True):
        tag = 'K' if withK else 'nonK'
        for sign in (True, False):
            res['rank']['ref_A__ref_G_%s_%s' % ('super' if sign else 'none', tag)] = rank_report(R, Aind, Gref[sign], withK)
        if Gw_raw:
            res['rank']['ref_A__worker_G_' + tag] = rank_report(R, Aind, Gw, withK)
    if Aw_raw:
        Aw = {ph: canon(D, basis, parity) for ph, D in Aw_raw.items()}
        res['coboundary_phi_columns'] = len(Aw)
        res['coboundary_pairs_recorded'] = len({(X, Y) for D in Aw_raw.values() for (X, Y, _z) in D})
        res['coboundary_antisym_conflicts'] = sum(c for _d, c in Aw.values())
        res['coboundary_K_rows'] = sum(1 for D in Aw_raw.values() for k in D if k[2] == 'K')
        Awc = [d for d, _c in Aw.values()]
        refset = [split(c, False) for c in Aind]
        eq = sum(1 for c in Awc if split(c, False) in refset)
        sub = sum(1 for c in Awc if split(c, False) not in refset and split(c, False) and any(
            all(r.get(k) == v for k, v in split(c, False).items()) for r in refset))
        res['coboundary_columns_vs_independent'] = dict(
            identical_nonK=eq, proper_subset_nonK=sub, other=len(Awc) - eq - sub,
            worker_nonK_entries=sum(len(split(c, False)) for c in Awc),
            independent_nonK_entries=sum(len(c) for c in refset))
        for withK in (False, True):
            tag = 'K' if withK else 'nonK'
            if Gw_raw:
                res['rank']['worker_A__worker_G_' + tag] = rank_report(R, Awc, Gw, withK)
            # column space of the Worker's A vs independent A
            f = (lambda d: d) if withK else (lambda d: split(d, False))
            a1, a2 = [f(c) for c in Awc], [f(c) for c in Aind]
            res['rank']['colspace_' + tag] = dict(rank_worker_A=R.rank(a1), rank_ref_A=R.rank(a2),
                                                  rank_both=R.rank(a1 + a2))
    return res


def main():
    args = sys.argv[1:]
    runs = ALL_RUNS
    if '--runs' in args:
        i = args.index('--runs'); runs = args[i + 1].split(','); del args[i:i + 2]
    ns = [int(a) for a in args] or [1, 2]
    for n in ns:
        out = []
        for r in runs:
            try:
                res = analyze(r, n)
            except Exception as e:  # report, do not hide
                res = dict(run=r, version=VERSION.get(r), n=n, error='%s: %s' % (type(e).__name__, e))
            out.append(res)
            brief(res)
        tag = os.environ.get('RESULTS_TAG', 'partial')
        fn = os.path.join(HERE, 'results_n%d.json' % n if runs == ALL_RUNS else 'results_n%d_%s.json' % (n, tag))
        json.dump(out, open(fn, 'w'), indent=1, default=str)
        print('wrote', fn)


def brief(res):
    print('=== %s n=%d' % (res['run'], res['n']))
    if 'error' in res:
        print('  ERROR', res['error']); return
    print('  struct consts vs realization:', res['structure_constants_vs_realization']['rel'],
          {k: v for k, v in res['structure_constants_vs_realization'].items() if k != 'rel'})
    print('  gamma file:', res['gamma_file'], 'pairs', res.get('gamma_pairs_recorded'),
          'nonK', res.get('gamma_entries_nonK'), 'K', res.get('gamma_entries_K'),
          'antisym conflicts', res.get('gamma_antisym_conflicts'))
    for k, v in res['gamma_cmp'].items():
        print('   cmp %-11s rels=%s tot=%s' % (k, v['relations'], v['total']))
    print('  coboundary file:', res['coboundary_file'], 'phi cols', res.get('coboundary_phi_columns'),
          'K rows', res.get('coboundary_K_rows'), 'antisym conflicts', res.get('coboundary_antisym_conflicts'))
    if 'coboundary_columns_vs_independent' in res:
        print('   A columns vs independent (canonical pairs):', res['coboundary_columns_vs_independent'])
    for k, v in res['rank'].items():
        if 'rankA' in v:
            print('   rank %-28s A=%d [A|G]=%d G=%d dirs trivial=%d/%d cols=%d' % (
                k, v['rankA'], v['rankAG'], v['rankG'], v['n_dirs_trivial'], len(v['per_direction_increase']), v['n_cols']))
        else:
            print('   rank %-28s %s' % (k, v))


if __name__ == '__main__':
    main()
