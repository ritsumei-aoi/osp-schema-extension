import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import coboundary as cb  # noqa: E402
from gamma import param_keys, param_name  # noqa: E402
from gauge_f import closed_form_f  # noqa: E402

for n in (1, 2, 3):
    L = cb.Layer1(n)
    elem = {m: cb.delta_elementary(L, *m) for m in L.odd_map_basis()}
    ev = json.load(open(os.path.join(cb.DATA, "C_%d_evaluated.json" % n)))
    keys = {param_name(k): k for k in param_keys(n)}
    res = []
    for p in ev["profiles"]:
        gb = {keys[q]: v for q, v in p["gb"].items()}
        f = closed_form_f(n, gb)
        df = cb.delta_of_f(f, elem)
        gam = cb.triple_dict(p["gamma_evaluated"])
        found = None
        for s in (1, -1):
            r = dict(gam)
            cb._add(r, df, -s)
            if not r:
                found = s
                break
        res.append(found)
    print(n, set(res))
