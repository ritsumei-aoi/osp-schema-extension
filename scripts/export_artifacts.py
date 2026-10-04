"""
Export structured verification artifacts (JSON) for C(n+1) triviality.
Generates complete data for n=1, 2, 3 including:
- Algebra basis, grading, and dimensions
- Non-zero structure constants
- Explicit matrix representation of odd map f
- Exact verification that gamma_gb == delta(-f)
"""

import json
import sympy as sp
from sympy import symbols, Rational, simplify

def generate_json_artifacts(output_path="data/verification_artifacts_cn1.json"):
    results = {
        "title": "Triviality Verification Artifacts for C(n+1) = osp(2|2n) Inhomogeneous Deformations",
        "theorem": "For all n >= 1, the inhomogeneous deformation gamma_gb of C(n+1) is unconditionally trivial (i.e., a coboundary gamma_gb = delta(-f)) for all deformation parameters gb.",
        "cases": {}
    }

    for n in [1, 2, 3]:
        print(f"Generating structured artifacts for n = {n}...")
        
        # 1. Oscillators
        oscillators = []
        oscillators.append(('a', 1, +1))
        oscillators.append(('a', 1, -1))
        for j in range(1, n+1):
            oscillators.append(('b', j, +1))
            oscillators.append(('b', j, -1))
            
        def osc_p(osc):
            return 1 if osc[0] == 'a' else 0

        gb_vars = {}
        gb_names = []
        for sigma in [+1, -1]:
            sig_str = '+' if sigma == +1 else '-'
            for j in range(1, n+1):
                for s in [+1, -1]:
                    s_str = '+' if s == +1 else '-'
                    var_name = f"gb_{sig_str}_{j}_{s_str}"
                    gb_vars[(sigma, j, s)] = symbols(var_name)
                    gb_names.append(var_name)

        def comm_0(u, v):
            if u[0] == 'a' and v[0] == 'a':
                if (u[2] == -1 and v[2] == +1) or (u[2] == +1 and v[2] == -1):
                    return Rational(1)
                return Rational(0)
            elif u[0] == 'b' and v[0] == 'b':
                if u[1] == v[1]:
                    if u[2] == -1 and v[2] == +1:
                        return Rational(1)
                    elif u[2] == +1 and v[2] == -1:
                        return Rational(-1)
                return Rational(0)
            return Rational(0)
                
        def comm_1(u, v):
            if u[0] == 'b' and v[0] == 'a':
                return -gb_vars[(v[2], u[1], u[2])]
            elif u[0] == 'a' and v[0] == 'b':
                return gb_vars[(u[2], v[1], v[2])]
            return Rational(0)

        # Basis
        basis = []
        basis_names = []
        basis_parities = []
        
        basis.append([(Rational(1), ('a', 1, +1), ('a', 1, -1)),
                      (Rational(1), ('b', 1, +1), ('b', 1, -1))])
        basis_names.append("H_1")
        basis_parities.append(0)
        
        for k in range(2, n+1):
            basis.append([(Rational(1), ('b', k-1, +1), ('b', k-1, -1)),
                          (Rational(-1), ('b', k, +1), ('b', k, -1))])
            basis_names.append(f"H_{k}")
            basis_parities.append(0)
            
        basis.append([(Rational(-1), ('b', n, +1), ('b', n, -1))])
        basis_names.append(f"H_{n+1}")
        basis_parities.append(0)
        
        for k in range(1, n+1):
            basis.append([(Rational(1, 2), ('b', k, +1), ('b', k, +1))])
            basis_names.append(f"E_2delta_{k}")
            basis_parities.append(0)
            
        for k in range(1, n+1):
            basis.append([(Rational(1, 2), ('b', k, -1), ('b', k, -1))])
            basis_names.append(f"E_-2delta_{k}")
            basis_parities.append(0)
            
        for k in range(1, n+1):
            for l in range(1, n+1):
                if k != l:
                    basis.append([(Rational(1), ('b', k, +1), ('b', l, -1))])
                    basis_names.append(f"E_delta_{k}-delta_{l}")
                    basis_parities.append(0)
                    
        for k in range(1, n+1):
            for l in range(k+1, n+1):
                basis.append([(Rational(1), ('b', k, +1), ('b', l, +1))])
                basis_names.append(f"E_delta_{k}+delta_{l}")
                basis_parities.append(0)
                
        for k in range(1, n+1):
            for l in range(k+1, n+1):
                basis.append([(Rational(1), ('b', k, -1), ('b', l, -1))])
                basis_names.append(f"E_-delta_{k}-delta_{l}")
                basis_parities.append(0)

        dim_even = len(basis)
        
        for l in range(1, n+1):
            basis.append([(Rational(1), ('a', 1, +1), ('b', l, +1))])
            basis_names.append(f"E_eps+delta_{l}")
            basis_parities.append(1)
            
        for l in range(1, n+1):
            basis.append([(Rational(1), ('a', 1, +1), ('b', l, -1))])
            basis_names.append(f"E_eps-delta_{l}")
            basis_parities.append(1)
            
        for l in range(1, n+1):
            basis.append([(Rational(1), ('a', 1, -1), ('b', l, +1))])
            basis_names.append(f"E_-eps+delta_{l}")
            basis_parities.append(1)
            
        for l in range(1, n+1):
            basis.append([(Rational(1), ('a', 1, -1), ('b', l, -1))])
            basis_names.append(f"E_-eps-delta_{l}")
            basis_parities.append(1)
            
        dim = len(basis)

        def reduce_pair(u, v):
            vec = [Rational(0)] * dim
            scalar = Rational(0)
            
            if u[0] == 'a' and v[0] == 'a':
                if u[2] == +1 and v[2] == -1:
                    vec[0] += Rational(1)
                    for k in range(2, n+1):
                        vec[k-1] -= Rational(1)
                    vec[n] += Rational(1)
                elif u[2] == -1 and v[2] == +1:
                    vec[0] -= Rational(1)
                    for k in range(2, n+1):
                        vec[k-1] += Rational(1)
                    vec[n] -= Rational(1)
                    scalar += Rational(1)
                    
            elif u[0] == 'b' and v[0] == 'b':
                k, s_k = u[1], u[2]
                l, s_l = v[1], v[2]
                if s_k == +1 and s_l == +1:
                    if k == l:
                        idx = basis_names.index(f"E_2delta_{k}")
                        vec[idx] += Rational(2)
                    elif k < l:
                        idx = basis_names.index(f"E_delta_{k}+delta_{l}")
                        vec[idx] += Rational(1)
                    else:
                        idx = basis_names.index(f"E_delta_{l}+delta_{k}")
                        vec[idx] += Rational(1)
                elif s_k == -1 and s_l == -1:
                    if k == l:
                        idx = basis_names.index(f"E_-2delta_{k}")
                        vec[idx] += Rational(2)
                    elif k < l:
                        idx = basis_names.index(f"E_-delta_{k}-delta_{l}")
                        vec[idx] += Rational(1)
                    else:
                        idx = basis_names.index(f"E_-delta_{l}-delta_{k}")
                        vec[idx] += Rational(1)
                elif s_k == +1 and s_l == -1:
                    if k != l:
                        idx = basis_names.index(f"E_delta_{k}-delta_{l}")
                        vec[idx] += Rational(1)
                    else:
                        for m in range(k+1, n+1):
                            vec[m-1] += Rational(1)
                        vec[n] -= Rational(1)
                elif s_k == -1 and s_l == +1:
                    if k != l:
                        idx = basis_names.index(f"E_delta_{l}-delta_{k}")
                        vec[idx] += Rational(1)
                    else:
                        for m in range(k+1, n+1):
                            vec[m-1] += Rational(1)
                        vec[n] -= Rational(1)
                        scalar += Rational(1)
                        
            elif u[0] == 'a' and v[0] == 'b':
                sig = u[2]
                l, s = v[1], v[2]
                sig_s = "eps" if sig == +1 else "-eps"
                s_s = f"+delta_{l}" if s == +1 else f"-delta_{l}"
                name = f"E_{sig_s}{s_s}"
                idx = basis_names.index(name)
                vec[idx] += Rational(1)
            elif u[0] == 'b' and v[0] == 'a':
                sig = v[2]
                l, s = u[1], u[2]
                sig_s = "eps" if sig == +1 else "-eps"
                s_s = f"+delta_{l}" if s == +1 else f"-delta_{l}"
                name = f"E_{sig_s}{s_s}"
                idx = basis_names.index(name)
                vec[idx] += Rational(1)
                
            return vec, scalar

        def bracket_monomial(u1, u2, w1, w2):
            p1, p2 = osc_p(u1), osc_p(u2)
            q1, q2 = osc_p(w1), osc_p(w2)
            
            vec0 = [Rational(0)] * dim
            scalar0 = Rational(0)
            
            c0_21 = comm_0(u2, w1)
            if c0_21 != 0:
                v, s = reduce_pair(u1, w2)
                for idx in range(dim): vec0[idx] += c0_21 * v[idx]
                scalar0 += c0_21 * s
                
            c0_22 = comm_0(u2, w2)
            if c0_22 != 0:
                sign = (-1)**(p2 * q1)
                v, s = reduce_pair(u1, w1)
                for idx in range(dim): vec0[idx] += sign * c0_22 * v[idx]
                scalar0 += sign * c0_22 * s
                
            c0_11 = comm_0(u1, w1)
            if c0_11 != 0:
                sign = (-1)**(p2 * (q1 + q2))
                v, s = reduce_pair(w2, u2)
                for idx in range(dim): vec0[idx] += sign * c0_11 * v[idx]
                scalar0 += sign * c0_11 * s
                
            c0_12 = comm_0(u1, w2)
            if c0_12 != 0:
                sign = (-1)**(p2 * (q1 + q2) + p1 * q1)
                v, s = reduce_pair(w1, u2)
                for idx in range(dim): vec0[idx] += sign * c0_12 * v[idx]
                scalar0 += sign * c0_12 * s
                
            vec1 = [sp.sympify(0) for _ in range(dim)]
            scalar1 = sp.sympify(0)
            
            c1_21 = comm_1(u2, w1)
            if c1_21 != 0:
                sign = (-1)**p1
                v, s = reduce_pair(u1, w2)
                for idx in range(dim): vec1[idx] += sign * c1_21 * v[idx]
                scalar1 += sign * c1_21 * s
                
            c1_22 = comm_1(u2, w2)
            if c1_22 != 0:
                sign = (-1)**(p2 * q1 + p1 + q1)
                v, s = reduce_pair(u1, w1)
                for idx in range(dim): vec1[idx] += sign * c1_22 * v[idx]
                scalar1 += sign * c1_22 * s
                
            c1_11 = comm_1(u1, w1)
            if c1_11 != 0:
                sign = (-1)**(p2 * (q1 + q2))
                v, s = reduce_pair(w2, u2)
                for idx in range(dim): vec1[idx] += sign * c1_11 * v[idx]
                scalar1 += sign * c1_11 * s
                
            c1_12 = comm_1(u1, w2)
            if c1_12 != 0:
                sign = (-1)**(p2 * (q1 + q2) + p1 * q1 + q1)
                v, s = reduce_pair(w1, u2)
                for idx in range(dim): vec1[idx] += sign * c1_12 * v[idx]
                scalar1 += sign * c1_12 * s
                
            return vec0, scalar0, vec1, scalar1

        def bracket_basis(i, j):
            b_i = basis[i]
            b_j = basis[j]
            out_v0 = [Rational(0)] * dim
            out_s0 = Rational(0)
            out_v1 = [sp.sympify(0) for _ in range(dim)]
            out_s1 = sp.sympify(0)
            
            for c_i, u1, u2 in b_i:
                for c_j, w1, w2 in b_j:
                    t_v0, t_s0, t_v1, t_s1 = bracket_monomial(u1, u2, w1, w2)
                    coeff = c_i * c_j
                    for idx in range(dim):
                        out_v0[idx] += coeff * t_v0[idx]
                        out_v1[idx] += coeff * t_v1[idx]
                    out_s0 += coeff * t_s0
                    out_s1 += coeff * t_s1
            return out_v0, out_s0, out_v1, out_s1

        br0 = {}
        gamma = {}
        for i in range(dim):
            for j in range(dim):
                v0, _, v1, _ = bracket_basis(i, j)
                br0[(i, j)] = v0
                gamma[(i, j)] = v1

        # Non-zero structure constants for undeformed bracket
        nonzero_structure_constants = []
        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    val = br0[(i, j)][k]
                    if val != 0:
                        nonzero_structure_constants.append({
                            "i": basis_names[i],
                            "j": basis_names[j],
                            "k": basis_names[k],
                            "coeff": str(val)
                        })

        # Theoretical f map
        f_matrix = []
        f_coefficients = {}
        for k in range(dim):
            name = basis_names[k]
            p = basis_parities[k]
            f_vec = [sp.sympify(0) for _ in range(dim)]
            
            if p == 0:
                if name == "H_1":
                    for j in range(1, n+1):
                        v1, _ = reduce_pair(('b', j, +1), ('a', 1, -1))
                        for d in range(dim): f_vec[d] += gb_vars[(+1, j, -1)] * v1[d]
                        
                        v2, _ = reduce_pair(('b', j, -1), ('a', 1, -1))
                        for d in range(dim): f_vec[d] -= gb_vars[(+1, j, +1)] * v2[d]
                        
                        v3, _ = reduce_pair(('a', 1, +1), ('b', j, +1))
                        for d in range(dim): f_vec[d] -= gb_vars[(-1, j, -1)] * v3[d]
                        
                        v4, _ = reduce_pair(('a', 1, +1), ('b', j, -1))
                        for d in range(dim): f_vec[d] += gb_vars[(-1, j, +1)] * v4[d]
            else:
                sigma = +1 if "eps" in name and "-eps" not in name else -1
                s = +1 if "+delta" in name else -1
                l = int(name.split("delta_")[1])
                for j in range(1, n+1):
                    v1, _ = reduce_pair(('b', j, +1), ('b', l, s))
                    for d in range(dim): f_vec[d] += gb_vars[(sigma, j, -1)] * v1[d]
                    
                    v2, _ = reduce_pair(('b', j, -1), ('b', l, s))
                    for d in range(dim): f_vec[d] -= gb_vars[(sigma, j, +1)] * v2[d]
                    
            f_matrix.append(f_vec)
            
            # Record non-zero components of f
            for d in range(dim):
                if f_vec[d] != 0:
                    f_coefficients[f"f({name}) -> {basis_names[d]}"] = str(f_vec[d])

        # Compute delta(f)
        def compute_delta_f(f_map, i, j):
            p_i = basis_parities[i]
            p_j = basis_parities[j]
            res = [sp.sympify(0) for _ in range(dim)]
            
            s1 = (-1)**p_i
            fy = f_map[j]
            for m in range(dim):
                if fy[m] != 0:
                    v_im = br0[(i, m)]
                    for d in range(dim):
                        res[d] += s1 * fy[m] * v_im[d]
                        
            s2 = - ((-1)**((p_i + 1) * p_j))
            fx = f_map[i]
            for m in range(dim):
                if fx[m] != 0:
                    v_jm = br0[(j, m)]
                    for d in range(dim):
                        res[d] += s2 * fx[m] * v_jm[d]
                        
            v_ij = br0[(i, j)]
            for k in range(dim):
                if v_ij[k] != 0:
                    fk = f_map[k]
                    for d in range(dim):
                        res[d] -= v_ij[k] * fk[d]
                        
            return res

        # Verify gamma == -delta(f)
        all_match = True
        mismatches = 0
        total_checks = dim * dim
        for i in range(dim):
            for j in range(dim):
                g_ij = gamma[(i, j)]
                df_ij = compute_delta_f(f_matrix, i, j)
                for d in range(dim):
                    diff = simplify(g_ij[d] - (-df_ij[d]))
                    if diff != 0:
                        all_match = False
                        mismatches += 1

        print(f"n={n}: Checked {total_checks} bracket pairs. All match: {all_match}")

        results["cases"][f"C_{n+1}"] = {
            "n": n,
            "algebra": f"C({n+1}) = osp(2|{2*n})",
            "superdimension": {
                "even": dim_even,
                "odd": dim - dim_even,
                "total": dim
            },
            "generators": basis_names,
            "generator_parities": basis_parities,
            "gb_parameters": gb_names,
            "num_nonzero_structure_constants": len(nonzero_structure_constants),
            "theoretical_shift_f": {
                "formula_summary": "Induced by fermionic oscillator shift v^sigma = sum_j (gb_{sigma, j, -} b_j^+ - gb_{sigma, j, +} b_j^-)",
                "nonzero_components": f_coefficients
            },
            "verification": {
                "coboundary_relation": "gamma_{gb} = delta(-f)",
                "total_pairs_checked": total_checks,
                "mismatches": mismatches,
                "verified": all_match
            }
        }

    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Structured artifacts written to {output_path}")

if __name__ == "__main__":
    generate_json_artifacts()
