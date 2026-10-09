"""Print the explicit cocycle gamma_gb and the explicit map f for a given n
(default n=1) in human-readable form, from the JSON artifact."""
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
with open(os.path.join(ROOT, "artifacts", f"Cn1_triviality_n{n}.json")) as fh:
    D = json.load(fh)
lab = [b["label"] for b in D["basis"]]
gbl = [g["label"] for g in D["gb_parameters"]]


def term(v, name):
    v = str(v)
    if v == "1":
        return f"+ {name}"
    if v == "-1":
        return f"- {name}"
    return f"{'+' if not v.startswith('-') else '-'} {v.lstrip('-')} {name}"


print(f"# n = {n}: basis")
for b in D["basis"]:
    print(f"  Z_{b['index']:<2} = {b['label']:<12} parity {b['parity']}  weight {b['weight']}   {b['oscillator_expression']}")
print("\n# gb parameters")
for g in D["gb_parameters"]:
    print(f"  gb[{g['index']}] = {g['label']:<18} {g['relation']}")

print("\n# explicit f  (f(Z_i) = sum_m phi_{m i} Z_m), only nonzero columns")
col = defaultdict(list)
for m, i, a, v in D["f_explicit"]["entries"]:
    col[i].append(term(v, f"{gbl[a]} {lab[m]}"))
for i in sorted(col):
    print(f"  f({lab[i]}) = " + " ".join(col[i]))
print("\n# scalar part f'' (doc ordering)")
col = defaultdict(list)
for i, a, v in D["f_explicit"]["scalar_part"]:
    col[i].append(term(v, gbl[a]))
for i in sorted(col):
    print(f"  f''({lab[i]}) = " + " ".join(col[i]))

print("\n# gamma_gb(Z_i, Z_j), g-valued part, i <= j only (super-skew-symmetric)")
ent = defaultdict(list)
for i, j, m, a, v in D["gamma_g_part"]:
    if i <= j:
        ent[(i, j)].append(term(v, f"{gbl[a]} {lab[m]}"))
for (i, j) in sorted(ent):
    print(f"  gamma({lab[i]}, {lab[j]}) = " + " ".join(ent[(i, j)]))
print("\n# gamma_gb scalar part (doc ordering), i <= j")
ent = defaultdict(list)
for i, j, a, v in D["gamma_scalar_part"]:
    if i <= j:
        ent[(i, j)].append(term(v, gbl[a]))
for (i, j) in sorted(ent):
    print(f"  gamma0({lab[i]}, {lab[j]}) = " + " ".join(ent[(i, j)]))
