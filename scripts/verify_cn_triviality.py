import numpy as np
import json
import os

class OSP_Deformation_Analyzer:
    """
    Rigorously analyzes the triviality of inhomogeneous deformations gb 
    for the Lie superalgebra C(n+1) = osp(2|2n).
    """
    def __init__(self, n):
        self.n = n
        
        # 1. Build Basis
        # Even Basis: H0 = a1+ a1-, plus sp(2n) generators
        self.even_basis = [('H0',)]
        for j in range(1, n+1):
            for k in range(j, n+1):
                self.even_basis.append(('B++', j, k))
        for j in range(1, n+1):
            for k in range(j, n+1):
                self.even_basis.append(('B--', j, k))
        for j in range(1, n+1):
            for k in range(1, n+1):
                self.even_basis.append(('B+-', j, k))
                
        # Odd Basis: a1^\sigma b_j^s
        self.odd_basis = []
        for sig in ['+', '-']:
            for s in ['+', '-']:
                for j in range(1, n+1):
                    self.odd_basis.append(('F', sig, j, s))
                    
        self.dim_even = len(self.even_basis)
        self.dim_odd = len(self.odd_basis)
        self.dim_total = self.dim_even + self.dim_odd
        self.basis = self.even_basis + self.odd_basis
        
        self.even_map = {b: i for i, b in enumerate(self.even_basis)}
        self.odd_map = {b: i for i, b in enumerate(self.odd_basis)}
        
        # 4n Deformation parameters gb_{sigma, j, s}
        self.gb_params = []
        for sig in ['+', '-']:
            for j in range(1, n+1):
                for s in ['+', '-']:
                    self.gb_params.append((sig, j, s))
        self.num_gb = len(self.gb_params)
        self.gb_map = {p: i for i, p in enumerate(self.gb_params)}

    def boson_comm(self, j, s, k, t):
        if j != k:
            return 0
        if s == '-' and t == '+':
            return 1
        if s == '+' and t == '-':
            return -1
        return 0

    def express_boson_bilinear(self, j, s, k, t):
        if s == '+' and t == '+':
            idx = self.even_map[('B++', min(j, k), max(j, k))]
            return [(1.0, idx)]
        elif s == '-' and t == '-':
            idx = self.even_map[('B--', min(j, k), max(j, k))]
            return [(1.0, idx)]
        elif s == '+' and t == '-':
            idx = self.even_map[('B+-', j, k)]
            return [(1.0, idx)]
        elif s == '-' and t == '+':
            idx = self.even_map[('B+-', k, j)]
            return [(1.0, idx)]

    def un_deformed_bracket(self, idx_X, idx_Y):
        is_X_even = idx_X < self.dim_even
        is_Y_even = idx_Y < self.dim_even
        
        X = self.basis[idx_X]
        Y = self.basis[idx_Y]
        
        res = {}
        
        if is_X_even and is_Y_even:
            if X[0] == 'H0' or Y[0] == 'H0':
                return res
            _, j, k = X[0], X[1], X[2]
            s, t = ('+', '+') if X[0] == 'B++' else (('-', '-') if X[0] == 'B--' else ('+', '-'))
            _, l, m = Y[0], Y[1], Y[2]
            u, v = ('+', '+') if Y[0] == 'B++' else (('-', '-') if Y[0] == 'B--' else ('+', '-'))
            
            terms = [
                (self.boson_comm(j, s, l, u), k, t, m, v),
                (self.boson_comm(j, s, m, v), l, u, k, t),
                (self.boson_comm(k, t, l, u), j, s, m, v),
                (self.boson_comm(k, t, m, v), j, s, l, u)
            ]
            for c, p, r, q, w in terms:
                if c != 0:
                    for coeff, b_idx in self.express_boson_bilinear(p, r, q, w):
                        res[b_idx] = res.get(b_idx, 0.0) + c * coeff
                        
        elif is_X_even and not is_Y_even:
            if X[0] == 'H0':
                sig = Y[1]
                val = 1.0 if sig == '+' else -1.0
                res[idx_Y] = val
            else:
                _, j, k = X[0], X[1], X[2]
                s, t = ('+', '+') if X[0] == 'B++' else (('-', '-') if X[0] == 'B--' else ('+', '-'))
                _, sig, l, u = Y
                
                c1 = self.boson_comm(j, s, l, u)
                if c1 != 0:
                    target = self.dim_even + self.odd_map[('F', sig, k, t)]
                    res[target] = res.get(target, 0.0) + c1
                c2 = self.boson_comm(k, t, l, u)
                if c2 != 0:
                    target = self.dim_even + self.odd_map[('F', sig, j, s)]
                    res[target] = res.get(target, 0.0) + c2
                    
        elif not is_X_even and is_Y_even:
            sub = self.un_deformed_bracket(idx_Y, idx_X)
            for k, v in sub.items():
                res[k] = -v
                
        else:
            _, sig, j, s = X
            _, tau, k, t = Y
            
            c_bos = self.boson_comm(j, s, k, t)
            if sig == '+' and tau == '-':
                if c_bos != 0:
                    h0_idx = self.even_map[('H0',)]
                    res[h0_idx] = res.get(h0_idx, 0.0) + c_bos
                for coeff, b_idx in self.express_boson_bilinear(k, t, j, s):
                    res[b_idx] = res.get(b_idx, 0.0) + coeff
                    
            elif sig == '-' and tau == '+':
                if c_bos != 0:
                    h0_idx = self.even_map[('H0',)]
                    res[h0_idx] = res.get(h0_idx, 0.0) - c_bos
                for coeff, b_idx in self.express_boson_bilinear(k, t, j, s):
                    res[b_idx] = res.get(b_idx, 0.0) + coeff
            
        return res

    def gamma_gb_bracket(self, idx_X, idx_Y):
        is_X_even = idx_X < self.dim_even
        is_Y_even = idx_Y < self.dim_even
        
        X = self.basis[idx_X]
        Y = self.basis[idx_Y]
        
        res = {}
        
        if is_X_even and is_Y_even:
            return res
            
        elif is_X_even and not is_Y_even:
            if X[0] == 'H0':
                _, sig, l, u = Y
                gb_idx = self.gb_map[(sig, l, u)]
                h0_idx = self.even_map[('H0',)]
                val = 1.0 if sig == '+' else -1.0
                res[(h0_idx, gb_idx)] = val
            else:
                _, j, k = X[0], X[1], X[2]
                s, t = ('+', '+') if X[0] == 'B++' else (('-', '-') if X[0] == 'B--' else ('+', '-'))
                _, sig, l, u = Y
                
                gb1 = self.gb_map[(sig, j, s)]
                for coeff, b_idx in self.express_boson_bilinear(k, t, l, u):
                    key = (b_idx, gb1)
                    res[key] = res.get(key, 0.0) - coeff
                    
                gb2 = self.gb_map[(sig, k, t)]
                for coeff, b_idx in self.express_boson_bilinear(j, s, l, u):
                    key = (b_idx, gb2)
                    res[key] = res.get(key, 0.0) - coeff
                    
        elif not is_X_even and is_Y_even:
            sub = self.gamma_gb_bracket(idx_Y, idx_X)
            for (target_idx, gb_idx), v in sub.items():
                res[(target_idx, gb_idx)] = -v
                
        else:
            _, sig, j, s = X
            _, tau, k, t = Y
            
            gb1 = self.gb_map[(tau, j, s)]
            t1 = self.dim_even + self.odd_map[('F', sig, k, t)]
            res[(t1, gb1)] = res.get((t1, gb1), 0.0) - 1.0
            
            gb2 = self.gb_map[(sig, k, t)]
            t2 = self.dim_even + self.odd_map[('F', tau, j, s)]
            res[(t2, gb2)] = res.get((t2, gb2), 0.0) - 1.0
            
        return res

    def build_linear_system(self):
        num_f_params = 2 * self.dim_even * self.dim_odd
        
        def f_oe_param_idx(o, e):
            return o * self.dim_even + e

        def f_eo_param_idx(e, o):
            return self.dim_odd * self.dim_even + e * self.dim_odd + o

        eq_list = []
        
        # 1. Even-Even
        for i in range(self.dim_even):
            for j in range(i + 1, self.dim_even):
                bracket_ij = self.un_deformed_bracket(i, j)
                for target_odd in range(self.dim_odd):
                    target_idx = self.dim_even + target_odd
                    f_coeffs = np.zeros(num_f_params)
                    
                    for o in range(self.dim_odd):
                        p_idx = f_oe_param_idx(o, j)
                        br = self.un_deformed_bracket(i, self.dim_even + o)
                        if target_idx in br:
                            f_coeffs[p_idx] += br[target_idx]
                            
                    for o in range(self.dim_odd):
                        p_idx = f_oe_param_idx(o, i)
                        br = self.un_deformed_bracket(j, self.dim_even + o)
                        if target_idx in br:
                            f_coeffs[p_idx] -= br[target_idx]
                            
                    for e, c in bracket_ij.items():
                        if e < self.dim_even:
                            p_idx = f_oe_param_idx(target_odd, e)
                            f_coeffs[p_idx] -= c
                            
                    gb_coeffs = np.zeros(self.num_gb)
                    eq_list.append((f_coeffs, gb_coeffs, f"EE({i},{j})->odd({target_odd})"))

        # 2. Even-Odd
        for i in range(self.dim_even):
            for j in range(self.dim_odd):
                idx_Y = self.dim_even + j
                bracket_ij = self.un_deformed_bracket(i, idx_Y)
                gamma_ij = self.gamma_gb_bracket(i, idx_Y)
                
                for target_even in range(self.dim_even):
                    f_coeffs = np.zeros(num_f_params)
                    
                    for e in range(self.dim_even):
                        p_idx = f_eo_param_idx(e, j)
                        br = self.un_deformed_bracket(i, e)
                        if target_even in br:
                            f_coeffs[p_idx] += br[target_even]
                            
                    for o in range(self.dim_odd):
                        p_idx = f_oe_param_idx(o, i)
                        br = self.un_deformed_bracket(idx_Y, self.dim_even + o)
                        if target_even in br:
                            f_coeffs[p_idx] -= br[target_even]
                            
                    for o_idx, c in bracket_ij.items():
                        if o_idx >= self.dim_even:
                            o = o_idx - self.dim_even
                            p_idx = f_eo_param_idx(target_even, o)
                            f_coeffs[p_idx] -= c
                            
                    gb_coeffs = np.zeros(self.num_gb)
                    for (t_idx, g_idx), c in gamma_ij.items():
                        if t_idx == target_even:
                            gb_coeffs[g_idx] += c
                            
                    eq_list.append((f_coeffs, gb_coeffs, f"EO({i},{j})->even({target_even})"))

        # 3. Odd-Odd
        for i in range(self.dim_odd):
            for j in range(i, self.dim_odd):
                idx_X = self.dim_even + i
                idx_Y = self.dim_even + j
                bracket_ij = self.un_deformed_bracket(idx_X, idx_Y)
                gamma_ij = self.gamma_gb_bracket(idx_X, idx_Y)
                
                for target_odd in range(self.dim_odd):
                    target_idx = self.dim_even + target_odd
                    f_coeffs = np.zeros(num_f_params)
                    
                    for e in range(self.dim_even):
                        p_idx = f_eo_param_idx(e, j)
                        br = self.un_deformed_bracket(idx_X, e)
                        if target_idx in br:
                            f_coeffs[p_idx] -= br[target_idx]
                            
                    for e in range(self.dim_even):
                        p_idx = f_eo_param_idx(e, i)
                        br = self.un_deformed_bracket(idx_Y, e)
                        if target_idx in br:
                            f_coeffs[p_idx] -= br[target_idx]
                            
                    for e, c in bracket_ij.items():
                        if e < self.dim_even:
                            p_idx = f_oe_param_idx(target_odd, e)
                            f_coeffs[p_idx] -= c
                            
                    gb_coeffs = np.zeros(self.num_gb)
                    for (t_idx, g_idx), c in gamma_ij.items():
                        if t_idx == target_idx:
                            gb_coeffs[g_idx] += c
                            
                    eq_list.append((f_coeffs, gb_coeffs, f"OO({i},{j})->odd({target_odd})"))

        M_f = np.array([eq[0] for eq in eq_list])
        M_gb = np.array([eq[1] for eq in eq_list])
        
        return M_f, M_gb, num_f_params, eq_list

def run_analysis():
    os.makedirs("artifacts", exist_ok=True)
    all_results = {}
    
    for n in [1, 2, 3]:
        analyzer = OSP_Deformation_Analyzer(n)
        M_f, M_gb, num_f_params, _ = analyzer.build_linear_system()
        
        U, S, Vt = np.linalg.svd(M_f, full_matrices=True)
        tol = 1e-10
        rank_M_f = np.sum(S > tol)
        U_kernel = U[:, rank_M_f:].T
        A = U_kernel @ M_gb
        
        U_A, S_A, Vt_A = np.linalg.svd(A, full_matrices=True)
        rank_A = np.sum(S_A > tol)
        dim_trivial_gb = analyzer.num_gb - rank_A
        
        conclusion = "NON-TRIVIAL FOR ALL NON-ZERO PARAMETERS" if rank_A == analyzer.num_gb else "TRIVIAL"
        
        res = {
            "n": n,
            "algebra": f"C({n}+1) = osp(2|{2*n})",
            "dim_even": analyzer.dim_even,
            "dim_odd": analyzer.dim_odd,
            "dim_total": analyzer.dim_total,
            "num_gb_parameters": analyzer.num_gb,
            "num_equations": M_f.shape[0],
            "num_f_parameters": num_f_params,
            "rank_coboundary_M_f": int(rank_M_f),
            "dim_obstruction_space": int(U_kernel.shape[0]),
            "rank_obstruction_matrix_A": int(rank_A),
            "dim_trivial_gb_subspace": int(dim_trivial_gb),
            "conclusion": conclusion,
            "singular_values_obstruction_matrix": S_A[:rank_A].tolist()
        }
        all_results[f"C({n}+1)"] = res

    with open("artifacts/verification_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("Verification completed and artifacts written to artifacts/verification_results.json")

if __name__ == "__main__":
    run_analysis()
