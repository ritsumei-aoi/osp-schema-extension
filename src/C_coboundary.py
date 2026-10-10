"""Schema 4 (coboundary structure) generator for C(n+1) (I07).

Defines an odd linear map f: g -> g (plus central K components) and computes
its coboundary with the convention from docs/math/C_coboundary_definition.md:

    (df)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])

The map f is the one induced on g by the kappa-shift of the fermionic pair

    a_1^sigma  ->  a_1^sigma + kappa * sum_{j,s} t_{sigma,j,s} b_j^s,
    t_{sigma,j,p} = -gb_{sigma,j,m},   t_{sigma,j,m} = +gb_{sigma,j,p},

i.e. f(X) = d/d(kappa) X(a_shifted). Concretely:
  - f(E_eps_del{l}_{sigma s'}) = sum_{j,s} t_{sigma,j,s} * NO(b_j^s b_l^{s'})
  - f(H_eps) = sum_{j,s} ( -t_{m,j,s} E_eps_del{j}_p{s} + t_{p,j,s} E_eps_del{j}_m{s} )
  - f(purely bosonic even generators) = 0

Usage: python3 src/C_coboundary.py   # writes data/C_{n}_coboundary.json
"""

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from oscillator_algebra import Element, letter_index
from C_generators import _basis_cache, decompose, DATA_DIR
from C_gamma import gb_labels

CONVENTION = (
    "(df)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])"
)


def t_coeff(sigma, j, s, assignment):
    """Shift coefficients t_{sigma,j,s} in terms of gb values."""
    if s == "p":
        return -assignment[f"gb_{sigma}_{j}_m"]
    return assignment[f"gb_{sigma}_{j}_p"]


def build_f(n, assignment):
    """Return f as {source_label: {target_label_or_K: Fraction}}."""
    labels, parity, _ = _basis_cache(n)
    f = {l: {} for l in labels}

    def add(src, dec):
        for z, c in dec.items():
            f[src][z] = f[src].get(z, Fraction(0)) + c
            if f[src][z] == 0:
                del f[src][z]

    for l in labels:
        if l.startswith("E_eps_del"):
            body = l[9:]
            k, ss = body.split("_")
            sigma, s_prime = ss[0], ss[1]
            lidx = int(k)
            for j in range(1, n + 1):
                for s in ("p", "m"):
                    t = t_coeff(sigma, j, s, assignment)
                    if t == 0:
                        continue
                    word = (letter_index(f"b_{j}_{s}"), letter_index(f"b_{lidx}_{s_prime}"))
                    prod = Element.from_words([((word[0],), 1)]).mul(
                        Element.from_words([((word[1],), 1)])
                    )
                    dec = decompose(prod, n, allow_constant=True)
                    add(l, {z: t * c for z, c in dec.items()})
        elif l == "H_eps":
            for j in range(1, n + 1):
                for s in ("p", "m"):
                    tm = t_coeff("m", j, s, assignment)
                    tp = t_coeff("p", j, s, assignment)
                    if tm:
                        add(l, {f"E_eps_del{j}_p{s}": -tm})
                    if tp:
                        add(l, {f"E_eps_del{j}_m{s}": tp})
        # purely bosonic generators: f = 0
    return f


def load_structure(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    labels = s1["basis"]["odd"] + s1["basis"]["even"]
    parity = dict(s1["parity"])
    parity["K"] = 0
    bracket = {}
    for rec in s1["structure_constants"]:
        bracket.setdefault((rec["X"], rec["Y"]), {})
        bracket[(rec["X"], rec["Y"])][rec["Z"]] = Fraction(rec["coeff"])
    return labels, parity, bracket


def compute_coboundary(n, assignment):
    """Return (f_map, records) with records = [{X,Y,Z,coeff}] for df."""
    labels, parity, bracket = load_structure(n)
    f = build_f(n, assignment)
    f["K"] = {}  # central: f(K) = 0

    def brk(x, y):
        if x == "K" or y == "K":
            return {}
        return bracket.get((x, y), {})

    def brk_with_combo(x, combo, scale):
        out = {}
        for z, c in combo.items():
            for w, cw in brk(x, z).items():
                out[w] = out.get(w, Fraction(0)) + scale * c * cw
        return {k: v for k, v in out.items() if v}

    records = []
    for x in labels:
        for y in labels:
            px, py = parity[x], parity[y]
            acc = {}
            # (-1)^{p(X)} [X, f(Y)]
            s1_ = Fraction(-1 if px else 1)
            for z, c in brk_with_combo(x, f[y], s1_).items():
                acc[z] = acc.get(z, Fraction(0)) + c
            # - (-1)^{(p(X)+1) p(Y)} [Y, f(X)]
            s2_ = Fraction(-1) * (-1 if ((px + 1) * py) % 2 else 1)
            for z, c in brk_with_combo(y, f[x], s2_).items():
                acc[z] = acc.get(z, Fraction(0)) + c
            # - f([X,Y])
            for z, c in brk(x, y).items():
                for w, cw in f.get(z, {}).items():
                    acc[w] = acc.get(w, Fraction(0)) - c * cw
            acc = {k: v for k, v in acc.items() if v}
            for z, c in sorted(acc.items()):
                records.append({"X": x, "Y": y, "Z": z, "coeff": str(c)})
    return f, records


def schema4(n, assignment_name="all_plus_one", assignment=None):
    labels_gb = gb_labels(n)
    if assignment is None:
        assignment = {l: Fraction(1) for l in labels_gb}
    f, records = compute_coboundary(n, assignment)
    # consistency with Layer 1 basis: all Z labels must be basis or K
    labels, parity, _ = load_structure(n)
    valid = set(labels) | {"K"}
    for rec in records:
        assert rec["X"] in labels and rec["Y"] in labels and rec["Z"] in valid
        # parity: df(X,Y) must have parity p(X)+p(Y)+1 (K = parity 0)
        want = (parity[rec["X"]] + parity[rec["Y"]] + 1) % 2
        assert parity[rec["Z"]] == want, rec
    f_entries = [
        {"source": src, "target": tgt, "coeff": str(c)}
        for src in labels
        for tgt, c in sorted(f[src].items())
    ]
    # f must be an odd map: p(f(Z)) = p(Z) + 1 (K components allowed on odd Z)
    for e in f_entries:
        want = (parity[e["source"]] + 1) % 2
        assert parity[e["target"]] == want, e
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra_ref": f"C_{n}_structure.json",
        "gb_assignment_name": assignment_name,
        "gb_assignment": {l: str(assignment[l]) for l in labels_gb},
        "f_map": {
            "description": (
                "Odd linear map f: g -> g (+ central K components), induced by "
                "the shift a_1^sigma -> a_1^sigma + kappa*sum t_{sigma,j,s} b_j^s "
                "with t_{sigma,j,p} = -gb_{sigma,j,m}, t_{sigma,j,m} = +gb_{sigma,j,p}"
            ),
            "entries": f_entries,
        },
        "coboundary": records,
        "convention": CONVENTION,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["docs/math/C_coboundary_definition.md"],
        },
    }


def main():
    for n in (1, 2, 3):
        data = schema4(n)
        path = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=1)
        print(
            f"C({n + 1}): f has {len(data['f_map']['entries'])} entries, "
            f"{len(data['coboundary'])} nonzero coboundary records -> "
            f"{os.path.relpath(path)} [basis/parity consistency: PASS]"
        )


if __name__ == "__main__":
    main()
