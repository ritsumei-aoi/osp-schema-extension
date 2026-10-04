import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any
from src.C_generators import CAlgebra, OscillatorPoly, gaussian_elimination_fractions

# Parameter labels for gb matrix:
# gb_{sigma, k, s} where sigma in ['p', 'm'], k in 1..n, s in ['p', 'm']
# e.g., "gb_a1_p_b_1_p", "gb_a1_p_b_1_m", "gb_a1_m_b_1_p", "gb_a1_m_b_1_m"

def get_gb_label(sigma: str, k: int, s: str) -> str:
    return f"gb_a1_{sigma}_b_{k}_{s}"

def compute_gamma_for_monomials(n: int, mono1, mono2, px: int, py: int) -> Dict[str, OscillatorPoly]:
    """
    Computes gamma part for m1 * m2 - (-1)^(px py) m2 * m1
    Returns dict mapping gb_label -> OscillatorPoly
    """
    res = {}
    
    # Process m1 * m2
    g1 = gamma_monomial_product(n, mono1, mono2)
    for gb, poly in g1.items():
        res[gb] = res.get(gb, OscillatorPoly.zero(n)).add(poly)

    # Process m2 * m1
    g2 = gamma_monomial_product(n, mono2, mono1)
    sign = -1 if (px == 1 and py == 1) else 1
    for gb, poly in g2.items():
        res[gb] = res.get(gb, OscillatorPoly.zero(n)).add(poly.scale(-sign))

    return res


def gamma_monomial_product(n: int, m1, m2) -> Dict[str, OscillatorPoly]:
    """
    Given two monomials m1 and m2 in normal form, sequence is (f1, b1) then (f2, b2).
    In tensor product form: f1 b1 f2 b2.
    Interactions between b1 and f2:
    b1 consists of bosonic operators (b_k^s)^v, f2 consists of fermionic operators (a_1^sigma)^u.
    
    For each boson operator in b1 and each fermion operator in f2:
    Commuting b_k^s past a_1^sigma produces commutator [b_k^s, a_1^sigma] = - gb_{sigma, k, s} * kappa.
    
    Remaining operators:
    Fermions: f1 and f2 with the selected a_1^sigma removed.
    Bosons: b1 with the selected b_k^s removed, and b2.
    
    We evaluate the remaining operators using standard CAR/CCR normal ordering!
    """
    f1, b1 = m1
    f2, b2 = m2

    res = {}

    # Expand f1, b1, f2, b2 into individual operator factors
    # f1 = (up1, um1), f2 = (up2, um2)
    f2_ops = []
    if f2[0] == 1: f2_ops.append(('p',))
    if f2[1] == 1: f2_ops.append(('m',))

    # b1 = tuple of (vp, vm) for k=1..n
    b1_ops = []
    for k_idx, (vp, vm) in enumerate(b1):
        k = k_idx + 1
        for _ in range(vp): b1_ops.append((k, 'p'))
        for _ in range(vm): b1_ops.append((k, 'm'))

    # For each pair (b_op in b1_ops, f_op in f2_ops):
    for i_b, (k_b, s_b) in enumerate(b1_ops):
        for i_f, (sigma_f,) in enumerate(f2_ops):
            gb_label = get_gb_label(sigma_f, k_b, s_b)

            # Build remaining f2 (f2 with i_f removed)
            rem_f2_ops = [op for idx, op in enumerate(f2_ops) if idx != i_f]
            rem_f2 = (1 if any(op[0] == 'p' for op in rem_f2_ops) else 0,
                      1 if any(op[0] == 'm' for op in rem_f2_ops) else 0)

            # Build remaining b1 (b1 with i_b removed)
            rem_b1_list = list(b1)
            vp, vm = rem_b1_list[k_b - 1]
            if s_b == 'p':
                rem_b1_list[k_b - 1] = (vp - 1, vm)
            else:
                rem_b1_list[k_b - 1] = (vp, vm - 1)
            rem_b1 = tuple(rem_b1_list)

            # Multiply remaining sequence: (f1, rem_b1) * (rem_f2, b2)
            # Note: factor is -1 from [b_k^s, a_1^sigma] = - gb * kappa
            # Also need sign from moving f2_ops[i_f] past preceding elements in f2 if needed,
            # but f2 is already in standard order (a1_p then a1_m).
            # If f2 had both a1_p and a1_m, f2_ops = [('p',), ('m',)].
            # If we pick i_f = 0 (a1_p), a1_p was first, no sign.
            # If we pick i_f = 1 (a1_m), a1_p was before it, so a1_p remains in rem_f2.
            # But wait: b_k^s was after f1, before f2.
            # To pair b_k^s with f2_ops[i_f], b_k^s moves past f2_ops[0...i_f-1].
            # Since f2_ops are fermions, moving a boson past fermions has sign +1 (bosons commute with everything parity-wise).
            
            rem_prod = mul_monomials(n, (f1, rem_b1), (rem_f2, b2))
            rem_poly = OscillatorPoly(n, rem_prod).scale(Fraction(-1))

            res[gb_label] = res.get(gb_label, OscillatorPoly.zero(n)).add(rem_poly)

    return res


def mul_monomials(n: int, m1, m2):
    from src.C_generators import mul_monomials as mm
    return mm(n, m1, m2)


def generate_schema_2(n: int) -> Dict[str, Any]:
    alg = CAlgebra(n)
    schema1 = json.load(open(f"data/C_{n}_structure.json"))

    gb_labels = []
    for k in range(1, n + 1):
        for sigma in ['p', 'm']:
            for s in ['p', 'm']:
                gb_labels.append(get_gb_label(sigma, k, s))

    # Compute gamma structure constants
    gamma_sc_list = []

    for i, x in enumerate(alg.basis_all):
        px = alg.parities[x]
        rx = alg.realizations[x]
        for j, y in enumerate(alg.basis_all):
            py = alg.parities[y]
            ry = alg.realizations[y]

            # Compute gamma poly for each gb parameter
            gb_polys: Dict[str, OscillatorPoly] = {}
            for mx, cx in rx.terms.items():
                for my, cy in ry.terms.items():
                    m_gamma = compute_gamma_for_monomials(n, mx, my, px, py)
                    for gb, poly in m_gamma.items():
                        gb_polys[gb] = gb_polys.get(gb, OscillatorPoly.zero(n)).add(poly.scale(cx * cy))

            # Express each gb_poly in basis
            for gb, poly in gb_polys.items():
                if not poly.terms:
                    continue
                coeffs = alg.express_in_basis(poly)
                for z, coeff in coeffs.items():
                    c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    gamma_sc_list.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "gb_param": gb,
                        "coeff": c_str
                    })

    # Build gb matrix layout for schema
    gb_matrix = {
        "dimensions": [2, 2 * n],
        "rows": ["a_1_p", "a_1_m"],
        "columns": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ["p", "m"]],
        "parameters": gb_labels
    }

    schema2 = dict(schema1)
    schema2["schema_version"] = "5.0"
    schema2["inhomogeneous_deformation"] = {
        "description": "Deformation gamma(X, Y) defined by [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa",
        "gb_matrix": gb_matrix,
        "gamma_structure_constants": gamma_sc_list
    }

    return schema2


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = generate_schema_2(n)
        filename = f"data/C_{n}_gamma.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (Gamma SC count: {len(data['inhomogeneous_deformation']['gamma_structure_constants'])})")
