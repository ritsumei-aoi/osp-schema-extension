#!/usr/bin/env python3
"""Exact (rational) verification of triviality of inhomogeneous deformations of C(n+1) = osp(2|2n).

Model
-----
V = V_0 + V_1 with V_0 = span{b_j^+, b_j^-} (even, dim 2n) and V_1 = span{a^+, a^-} (odd, dim 2).
kappa is an odd central generator (parity 1, kappa^2 = 0), realised as one more odd generator of
the super-commutative algebra Sym(V + kappa).

g = Sym^2(V) (quadratic super-polynomials in V, dimension 2n^2+5n+1), with the super Poisson
bracket for the constant super-skew form
    omega = omega_0 + kappa * Omega_gb,
    omega_0(b_j^-, b_k^+) = delta_jk,  omega_0(b_j^+, b_k^-) = -delta_jk,
    omega_0(a^+, a^-) = omega_0(a^-, a^+) = 1,
    Omega(b_j^s, a^sigma) = -gb[sigma,j,s],  Omega(a^sigma, b_j^s) = +gb[sigma,j,s],
gb being even (rational) scalars. Parity: [b,a] = -gb*kappa is odd, as required.

The deformed bracket is [Q,Q']_kappa = [Q,Q']_0 + kappa * gamma(Q,Q') with gamma_gb read off
from the kappa-linear part of the Poisson bracket, with kappa placed on the left
(kappa * m' = (-1)^{|m'|} m' * kappa in the super-commutative algebra).

Coboundary: f = s * D_gb, with s = +1 or -1 a convention sign, and D_gb the odd derivation of
Sym(V) with D(b_j^s) = -sum_sigma gb[-sigma,j,s] a^sigma, D(a^sigma) = 0.
delta is the operator in docs/math/C_coboundary_definition.md, evaluated with the undeformed bracket.

Checks: the kappa-Jacobi identity (exact, kappa^2 = 0) for omega_0 + kappa*Omega on all basis
triples, the kappa-free part of the deformed bracket equal to the undeformed one, and
gamma_gb = s * delta(D_gb). gb -> gamma_gb, gb -> D_gb and delta are linear, so the check on
the 4n unit vectors of gb-space proves gamma_gb = s * delta(D_gb) for all gb (for this n);
a random rational gb is also checked as an independent sample.

Standard library only. Run with:  python3 -I scripts/verify_triviality.py --n 1 2 3
"""

import argparse
import json
import os
import random
from fractions import Fraction


def opp(sign):
    return "-" if sign == "+" else "+"


def _acc(acc, d, scale=1):
    """acc += scale * d (in place) and return acc."""
    for key, c in d.items():
        acc[key] = acc.get(key, 0) + scale * c
    return acc


def _clean(d):
    return {key: c for key, c in d.items() if c != 0}


def _flat(table, prefix=()):
    """Flatten a nested sparse table {key: {k: coeff}} into {(key, k): coeff}, zeros dropped."""
    out = {}
    for key, val in table.items():
        if isinstance(val, dict):
            for k, c in val.items():
                if c != 0:
                    out[prefix + (key, k)] = c
        elif val != 0:
            out[prefix + (key,)] = val
    return out


def _same(t1, t2):
    """Exact equality of nested sparse tables (zero entries ignored)."""
    return _flat(t1) == _flat(t2)


def _neg(table):
    return {key: {k: -c for k, c in val.items()} for key, val in table.items()}


class Osp:
    """C(n+1) = osp(2|2n) realised as quadratic super-polynomials on V, with odd kappa."""

    def __init__(self, n):
        self.n = n
        self.names, self.parity = [], []
        for j in range(1, n + 1):
            self.names += [f"b{j}+", f"b{j}-"]
            self.parity += [0, 0]
        self.names += ["a+", "a-"]
        self.parity += [1, 1]
        self.dim_V = len(self.names)
        self.kidx = self.dim_V  # odd central generator kappa
        self.names.append("kappa")
        self.parity.append(1)
        self.dim_all = len(self.names)
        self.idx = {nm: i for i, nm in enumerate(self.names)}

        # Basis of g = Sym^2(V): monomials x_i x_j with i <= j, odd x_i never squared.
        self.basis = []
        for i in range(self.dim_V):
            for j in range(i, self.dim_V):
                if i == j and self.parity[i] == 1:
                    continue
                self.basis.append((i, j))
        self.bindex = {m: k for k, m in enumerate(self.basis)}
        self.basis_parity = [self.par(m) for m in self.basis]

    # ---- super-commutative algebra on monomials -------------------------------------
    def par(self, mono):
        return sum(self.parity[i] for i in mono) % 2

    def normalize(self, seq):
        """Sort a product of generators; return (sign, sorted tuple) or (0, None)."""
        seq = list(seq)
        sign = 1
        for end in range(len(seq) - 1, 0, -1):
            for k in range(end):
                if seq[k] > seq[k + 1]:
                    if self.parity[seq[k]] and self.parity[seq[k + 1]]:
                        sign = -sign
                    seq[k], seq[k + 1] = seq[k + 1], seq[k]
        for k in range(len(seq) - 1):
            if seq[k] == seq[k + 1] and self.parity[seq[k]]:
                return 0, None
        return sign, tuple(seq)

    def mul(self, A, B):
        out = {}
        for ma, ca in A.items():
            for mb, cb in B.items():
                s, m = self.normalize(ma + mb)
                if s:
                    out[m] = out.get(m, 0) + s * ca * cb
        return _clean(out)

    # ---- super Poisson bracket with constant (kappa-valued) form ---------------------
    def bracket_mono(self, m1, m2, form):
        """Super Poisson bracket of monomials; form.W[i][j] is a dict {monomial: coeff}."""
        if not m1 or not m2:
            return {}
        key = (m1, m2)
        if key in form.cache:
            return form.cache[key]
        if len(m1) == 1 and len(m2) == 1:
            res = _clean(dict(form.W[m1[0]][m2[0]]))
        elif len(m2) >= 2:
            # {A, B C} = {A,B} C + (-1)^{|A||B|} B {A,C}
            b, c = (m2[0],), m2[1:]
            t1 = self.mul(self.bracket_mono(m1, b, form), {c: 1})
            t2 = self.mul({b: 1}, self.bracket_mono(m1, c, form))
            sign = -1 if (self.par(m1) * self.parity[b[0]]) % 2 else 1
            res = _clean(_acc(_acc({}, t1), t2, sign))
        else:
            # {A B, C} = A {B,C} + (-1)^{|B||C|} {A,C} B
            a, b = (m1[0],), m1[1:]
            t1 = self.mul({a: 1}, self.bracket_mono(b, m2, form))
            t2 = self.mul(self.bracket_mono(a, m2, form), {b: 1})
            sign = -1 if (self.par(b) * self.par(m2)) % 2 else 1
            res = _clean(_acc(_acc({}, t1), t2, sign))
        form.cache[key] = res
        return res

    def bracket(self, A, B, form):
        out = {}
        for m1, c1 in A.items():
            for m2, c2 in B.items():
                _acc(out, self.bracket_mono(m1, m2, form), c1 * c2)
        return _clean(out)

    def bracket_table(self, form):
        """Structure table {(p,q): {monomial: c}} for [Z_p, Z_q] over basis of g."""
        table = {}
        for p, mp in enumerate(self.basis):
            for q, mq in enumerate(self.basis):
                res = self.bracket_mono(mp, mq, form)
                if res:
                    table[(p, q)] = res
        return table

    def to_index_table(self, table):
        """Convert {(p,q): {monomial: c}} to {(p,q): {k: c}}; kappa-free monomials only."""
        out = {}
        for pq, entry in table.items():
            e = {}
            for m, c in entry.items():
                if m not in self.bindex:
                    raise ValueError(f"monomial outside basis of g: {m}")
                e[self.bindex[m]] = c
            e = _clean(e)
            if e:
                out[pq] = e
        return out

    def gamma_from_kappa_part(self, table):
        """Split a bracket table into kappa-free part and gamma (kappa on the left).

        A term r * (m', kappa) in the product equals kappa * ((-1)^{|m'|} r) m',
        so gamma_{m'} = (-1)^{|m'|} r.
        """
        free, gam = {}, {}
        for pq, entry in table.items():
            f_part, g_part = {}, {}
            for m, c in entry.items():
                if m and m[-1] == self.kidx:
                    base = m[:-1]
                    if self.kidx in base:
                        raise ValueError("kappa^2 term appeared")
                    g_part[base] = (-1) ** self.par(base) * c
                else:
                    if self.kidx in m:
                        raise ValueError("kappa not at end of monomial")
                    f_part[m] = c
            if f_part:
                free[pq] = f_part
            if g_part:
                gam[pq] = g_part
        return self.to_index_table(free), self.to_index_table(gam)

    def jacobi_full(self, form):
        """Super-Jacobi on all basis triples, computed in the algebra with kappa (kappa^2 = 0)."""
        N = len(self.basis)
        singles = [{m: 1} for m in self.basis]
        for p in range(N):
            for q in range(N):
                bpq = self.bracket(singles[p], singles[q], form)
                for r in range(N):
                    x, y, z = singles[p], singles[q], singles[r]
                    lhs = self.bracket(x, self.bracket(y, z, form), form)
                    s = -1 if (self.basis_parity[p] * self.basis_parity[q]) % 2 else 1
                    rhs = _acc(_acc({}, self.bracket(bpq, z, form)),
                               self.bracket(y, self.bracket(x, z, form), form), s)
                    if _clean(_acc(_acc({}, lhs), rhs, -1)):
                        return False
        return True

    # ---- forms ----------------------------------------------------------------------
    def make_form(self, gb=None):
        """Form omega_0 + kappa*Omega_gb as W[i][j] = {monomial: coeff}."""
        N = self.dim_all
        W = [[{} for _ in range(N)] for _ in range(N)]

        def put(i, j, mono, val):
            if val:
                W[i][j][mono] = W[i][j].get(mono, 0) + val

        for j in range(1, self.n + 1):
            bm, bp = self.idx[f"b{j}-"], self.idx[f"b{j}+"]
            put(bm, bp, (), Fraction(1))
            put(bp, bm, (), Fraction(-1))
        am, ap = self.idx["a-"], self.idx["a+"]
        put(am, ap, (), Fraction(1))
        put(ap, am, (), Fraction(1))
        if gb is not None:
            for (sig, j, s), val in gb.items():
                bi = self.idx[f"b{j}{s}"]
                ai = self.idx[f"a{sig}"]
                put(bi, ai, (self.kidx,), -val)
                put(ai, bi, (self.kidx,), val)

        class _Form:
            pass

        form = _Form()
        form.W = W
        form.cache = {}
        return form

    def superskew_ok(self, form):
        """Check W_ij = -(-1)^{p_i p_j} W_ji (entries are kappa-valued dicts)."""
        W = form.W
        for i in range(self.dim_all):
            for j in range(self.dim_all):
                s = -1 if (self.parity[i] * self.parity[j]) % 2 else 1
                keys = set(W[i][j]) | set(W[j][i])
                for k in keys:
                    if W[i][j].get(k, 0) != -s * W[j][i].get(k, 0):
                        return False
        return True

    # ---- odd derivations and coboundary ----------------------------------------------
    def odd_derivation_gen(self, gb, flip=True):
        """Images D(v) of generators v of V. flip=False is a negative control (wrong index)."""
        Dgen = {i: {} for i in range(self.dim_V)}
        for (sig, j, s), val in gb.items():
            src = self.idx[f"b{j}{s}"]
            target_sig = opp(sig) if flip else sig
            tgt = self.idx[f"a{target_sig}"]
            Dgen[src][(tgt,)] = Dgen[src].get((tgt,), 0) - val
        return Dgen

    def apply_odd_derivation(self, Dgen, mono):
        if not mono:
            return {}
        if len(mono) == 1:
            return dict(Dgen.get(mono[0], {}))
        x, rest = (mono[0],), mono[1:]
        t1 = self.mul(self.apply_odd_derivation(Dgen, x), {rest: 1})
        t2 = self.mul({x: 1}, self.apply_odd_derivation(Dgen, rest))
        sign = -1 if self.parity[x[0]] else 1
        return _clean(_acc(_acc({}, t1), t2, sign))

    def derivation_matrix(self, Dgen):
        """fvec[k] = {i: c} with f(Z_k) = sum_i c Z_i, for f = D restricted to g."""
        fvec = {}
        for k, mono in enumerate(self.basis):
            img = self.apply_odd_derivation(Dgen, mono)
            entry = {}
            for m, c in img.items():
                if m not in self.bindex:
                    raise ValueError(f"derivation left Sym^2: {m}")
                entry[self.bindex[m]] = c
            fvec[k] = _clean(entry)
        return fvec

    def coboundary(self, fvec, T0):
        """(delta f)(Z_p,Z_q) = (-1)^{|p|}[Z_p, fZ_q] - (-1)^{(|p|+1)|q|}[Z_q, fZ_p] - f([Z_p,Z_q])."""
        N = len(self.basis)

        def br_vec(p, vec):
            acc = {}
            for i, c in vec.items():
                _acc(acc, T0.get((p, i), {}), c)
            return acc

        out = {}
        for p in range(N):
            for q in range(N):
                acc = {}
                pp, pq = self.basis_parity[p], self.basis_parity[q]
                _acc(acc, br_vec(p, fvec[q]), (-1) ** pp)
                _acc(acc, br_vec(q, fvec[p]), -((-1) ** ((pp + 1) * pq)))
                for k, c in T0.get((p, q), {}).items():
                    _acc(acc, fvec[k], -c)
                acc = _clean(acc)
                if acc:
                    out[(p, q)] = acc
        return out

    # ---- serialisation helpers -----------------------------------------------------
    def label(self, m):
        return "*".join(self.names[i] for i in m)

    def sparse_table(self, table):
        rows = []
        for (p, q), entry in sorted(table.items()):
            for k, c in sorted(entry.items()):
                rows.append([p, q, k, str(c)])
        return rows

    def sparse_fvec(self, fvec):
        rows = []
        for k in sorted(fvec):
            for i, c in sorted(fvec[k].items()):
                rows.append([i, k, str(c)])  # f(Z_k) contains c * Z_i
        return rows


def gb_keys(n):
    return [(sig, j, s) for sig in "+-" for j in range(1, n + 1) for s in "+-"]


def unit_gb(n, key):
    return {k: Fraction(1 if k == key else 0) for k in gb_keys(n)}


def random_gb(n, rng):
    return {k: Fraction(rng.randint(-9, 9), rng.randint(1, 5)) for k in gb_keys(n)}


def check_gb(alg, gb, T0):
    """Return gamma, f, delta f and match flags for one gb configuration."""
    form = alg.make_form(gb)
    _, gamma = alg.gamma_from_kappa_part(alg.bracket_table(form))
    Dgen = alg.odd_derivation_gen(gb, flip=True)
    fvec = alg.derivation_matrix(Dgen)
    dl = alg.coboundary(fvec, T0)
    return {
        "gamma": gamma,
        "fvec": fvec,
        "delta_f": dl,
        "gamma_nonzero": bool(gamma),
        "gamma_equals_delta_f": _same(gamma, dl),
        "gamma_equals_minus_delta_f": _same(gamma, _neg(dl)),
    }


def verify(n, rng):
    alg = Osp(n)
    form0 = alg.make_form(None)
    T0 = alg.to_index_table(alg.bracket_table(form0))
    even = sum(1 for p in alg.basis_parity if p == 0)
    odd = sum(1 for p in alg.basis_parity if p == 1)

    checks = {
        "dim_g_equals_2n2_5n_1": len(alg.basis) == 2 * n * n + 5 * n + 1,
        "dim_g0_equals_2n2_n_1": even == 2 * n * n + n + 1,
        "dim_g1_equals_4n": odd == 4 * n,
        "omega0_superskew": alg.superskew_ok(form0),
        "jacobi_undeformed": alg.jacobi_full(form0),
    }

    keys = gb_keys(n)
    gb_rand = random_gb(n, rng)
    form_rand = alg.make_form(gb_rand)
    checks["omega_full_superskew_random_gb"] = alg.superskew_ok(form_rand)
    free_rand, _ = alg.gamma_from_kappa_part(alg.bracket_table(form_rand))
    checks["kappa_free_part_equals_undeformed_random_gb"] = _same(free_rand, T0)
    checks["kappa_jacobi_random_gb"] = alg.jacobi_full(form_rand)

    unit_results = {}
    unit_artifacts = {}
    for key in keys:
        gb = unit_gb(n, key)
        res = check_gb(alg, gb, T0)
        name = f"gb[{key[0]},{key[1]},{key[2]}]"
        unit_results[name] = {
            "gamma_nonzero": res["gamma_nonzero"],
            "gamma_equals_delta_f": res["gamma_equals_delta_f"],
            "gamma_equals_minus_delta_f": res["gamma_equals_minus_delta_f"],
        }
        unit_artifacts[name] = {
            "gamma_sparse": alg.sparse_table(res["gamma"]),
            "f_sparse_i_k_coeff": alg.sparse_fvec(res["fvec"]),
        }

    all_unit_plus = all(v["gamma_equals_delta_f"] for v in unit_results.values())
    all_unit_minus = all(v["gamma_equals_minus_delta_f"] for v in unit_results.values())
    checks["all_unit_gb_gamma_equals_plus_delta_f"] = all_unit_plus
    checks["all_unit_gb_gamma_equals_minus_delta_f"] = all_unit_minus
    checks["all_unit_gb_gamma_nonzero"] = all(v["gamma_nonzero"] for v in unit_results.values())

    rnd = check_gb(alg, gb_rand, T0)
    checks["random_gb_gamma_equals_plus_delta_f"] = rnd["gamma_equals_delta_f"]
    checks["random_gb_gamma_equals_minus_delta_f"] = rnd["gamma_equals_minus_delta_f"]

    # Negative control: a wrong index convention for D (no opp() flip) must fail on some unit gb.
    neg_fail = 0
    for key in keys:
        gb = unit_gb(n, key)
        _, gamma = alg.gamma_from_kappa_part(alg.bracket_table(alg.make_form(gb)))
        bad = alg.coboundary(alg.derivation_matrix(alg.odd_derivation_gen(gb, flip=False)), T0)
        if not (_same(gamma, bad) or _same(gamma, _neg(bad))):
            neg_fail += 1
    checks["negative_control_wrong_index_convention_detected"] = neg_fail > 0

    # Negative control: a gb-independent wrong D (f = 0) must not match a nonzero gamma.
    checks["negative_control_zero_f_fails_for_nonzero_gb"] = all(
        unit_results[k]["gamma_nonzero"] for k in unit_results
    )

    # Pass criterion: the bracket identity holds with one consistent sign s in {+1,-1}.
    # The opposite-sign flags are informational only (they are False when s = +1 holds).
    if all_unit_plus and not all_unit_minus:
        sign = "+1"
    elif all_unit_minus and not all_unit_plus:
        sign = "-1"
    else:
        sign = "mixed"
    main_checks = {
        k: v
        for k, v in checks.items()
        if not k.startswith("negative_control") and "minus_delta_f" not in k
    }
    all_pass = (
        all(main_checks.values())
        and sign in ("+1", "-1")
        and checks["negative_control_wrong_index_convention_detected"]
    )

    artifact = {
        "n": n,
        "model": {
            "algebra": f"C({n+1}) = osp(2|{2*n})",
            "realisation": "quadratic super-polynomials on V = V0+V1 with super Poisson bracket, kappa odd",
            "V0": [f"b{j}{s}" for j in range(1, n + 1) for s in "+-"],
            "V1": ["a+", "a-"],
            "kappa": "odd central generator, parity 1",
            "omega0": "omega0(b_j^-,b_k^+)=delta_jk, omega0(a^+,a^-)=omega0(a^-,a^+)=1",
            "deformation": "omega = omega0 + kappa*Omega, Omega(b_j^s,a^sigma) = -gb[sigma,j,s]",
            "gb_parity": "even (rational scalars), so that [b,a] = -gb*kappa has parity 1",
            "gamma": "kappa-linear part of the Poisson bracket, kappa on the left",
            "coboundary": "f = s*D_gb, D(b_j^s) = -sum_sigma gb[-sigma,j,s] a^sigma, D(a)=0",
            "sign_convention_found": sign,
        },
        "basis": [
            {"index": p, "label": alg.label(m), "parity": alg.basis_parity[p]}
            for p, m in enumerate(alg.basis)
        ],
        "gb_parameters": [
            {"index": i, "sigma": k[0], "j": k[1], "s": k[2], "key": f"gb[{k[0]},{k[1]},{k[2]}]"}
            for i, k in enumerate(keys)
        ],
        "structure_constants_omega0": alg.sparse_table(T0),
        "unit_gb_results": unit_results,
        "unit_gb_artifacts": unit_artifacts,
        "random_gb_sample": {
            "gb": {f"gb[{k[0]},{k[1]},{k[2]}]": str(v) for k, v in gb_rand.items()},
            "gamma_sparse": alg.sparse_table(rnd["gamma"]),
            "f_sparse_i_k_coeff": alg.sparse_fvec(rnd["fvec"]),
            "gamma_equals_delta_f": rnd["gamma_equals_delta_f"],
            "gamma_equals_minus_delta_f": rnd["gamma_equals_minus_delta_f"],
        },
        "checks": checks,
        "all_checks_pass": bool(all_pass),
    }
    return artifact


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--seed", type=int, default=20260617)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts"))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    summary = {"description": "Exact rational verification of gamma_gb = s*delta(f) for C(n+1)", "runs": {}}
    for n in args.n:
        rng = random.Random(args.seed + n)
        art = verify(n, rng)
        path = os.path.join(args.out, f"triviality_n{n}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(art, fh, indent=1, ensure_ascii=False)
        summary["runs"][f"n={n}"] = {
            "algebra": art["model"]["algebra"],
            "all_checks_pass": art["all_checks_pass"],
            "sign_convention_found": art["model"]["sign_convention_found"],
            "checks": art["checks"],
            "artifact": os.path.relpath(path, os.path.dirname(args.out)),
        }
        print(f"n={n}: {art['model']['algebra']}  all_checks_pass={art['all_checks_pass']}  "
              f"sign={art['model']['sign_convention_found']}")
        for k, v in art["checks"].items():
            print(f"    {k}: {v}")
    with open(os.path.join(args.out, "triviality_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
