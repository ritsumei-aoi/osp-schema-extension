"""Print concrete Layer 3 / Layer 4 evidence used in the I08 report."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

for n, name in ((1, "plus"), (1, "single"), (2, "alt")):
    suffix = "" if name == "plus" else "_" + name
    d3 = json.load(open(DATA / f"C_{n}_evaluated{suffix}.json"))
    d4 = json.load(open(DATA / f"C_{n}_coboundary{suffix}.json"))
    print(n, name, {k: v for k, v in d3["profile"]["gb_values"].items() if v != "0"})
    print("  f_K:", [(e["X"], e["coeff"]) for e in d4["odd_map"]["central_component"]])
    print("  central residue:", [(e["X"], e["Y"], e["coeff"]) for e in d3["evaluated_deformation"]["central_component"]][:24])
    g3 = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in d3["evaluated_deformation"]["gamma"]}
    g4 = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in d4["coboundary"]["delta_f"]}
    ex = [k for k in sorted(g3)][:3]
    for k in ex:
        print("  gamma", k, g3[k], " delta f:", g4.get(k))
