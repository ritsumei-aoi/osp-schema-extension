import sys
sys.path.append('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r2-F/.gemini/antigravity-cli/brain/3090f976-3b8f-4950-840e-bdc00768cc80/scratch')
from test_poly import Poly, Monomial
from fractions import Fraction
import sympy

def get_basis_and_generators(n):
    # Oscillators
    ap = Poly.from_osc("a_1_p", n)
    am = Poly.from_osc("a_1_m", n)
    bps = [Poly.from_osc(f"b_{k+1}_p", n) for k in range(n)]
    bms = [Poly.from_osc(f"b_{k+1}_m", n) for k in range(n)]
    
    generators = {}
    parities = {}
    
    # 1. Cartan
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    generators["H_1"] = ap * am + bps[0] * bms[0]
    parities["H_1"] = 0
    
    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- (for 2 <= k <= n)
    for k in range(2, n + 1):
        generators[f"H_{k}"] = bps[k-2] * bms[k-2] - bps[k-1] * bms[k-1]
        parities[f"H_{k}"] = 0
        
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    generators[f"H_{n+1}"] = bps[n-1] * bms[n-1] * Fraction(-1) - Poly.const(Fraction(1, 2), n)
    parities[f"H_{n+1}"] = 0
    
    even_cartan = [f"H_{k}" for k in range(1, n + 2)]
    
    # 2. Long even roots: E_2del{k}_p, E_2del{k}_m
    even_long_p = []
    even_long_m = []
    for k in range(1, n + 1):
        name_p = f"E_2del{k}_p"
        name_m = f"E_2del{k}_m"
        generators[name_p] = bps[k-1] * bps[k-1]
        generators[name_m] = bms[k-1] * bms[k-1]
        parities[name_p] = 0
        parities[name_m] = 0
        even_long_p.append(name_p)
        even_long_m.append(name_m)
        
    # 3. Short even roots: E_del{i}_del{j}_pp/mm/pm/mp (1 <= i < j <= n)
    even_short = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pp = f"E_del{i}_del{j}_pp"
            mm = f"E_del{i}_del{j}_mm"
            pm = f"E_del{i}_del{j}_pm"
            mp = f"E_del{i}_del{j}_mp"
            generators[pp] = bps[i-1] * bps[j-1]
            generators[mm] = bms[i-1] * bms[j-1]
            generators[pm] = bps[i-1] * bms[j-1]
            generators[mp] = bms[i-1] * bps[j-1]
            for name in [pp, mm, pm, mp]:
                parities[name] = 0
            even_short.extend([pp, mm, pm, mp])
            
    even_basis = even_cartan + even_long_p + even_long_m + even_short
    
    # 4. Odd roots (Mode block order Option A):
    # For k in 1..n: E_eps1_del{k}_pp, pm, mp, mm
    odd_basis = []
    for k in range(1, n + 1):
        pp = f"E_eps1_del{k}_pp"
        pm = f"E_eps1_del{k}_pm"
        mp = f"E_eps1_del{k}_mp"
        mm = f"E_eps1_del{k}_mm"
        generators[pp] = ap * bps[k-1]
        generators[pm] = ap * bms[k-1]
        generators[mp] = am * bps[k-1]
        generators[mm] = am * bms[k-1]
        for name in [pp, pm, mp, mm]:
            parities[name] = 1
            odd_basis.append(name)
            
    full_basis = odd_basis + even_basis # PBW order: odd < even
    return full_basis, even_basis, odd_basis, generators, parities

def graded_bracket(X_poly, pX, Y_poly, pY):
    # [X, Y} = XY - (-1)^{pX * pY} YX
    sign = -1 if (pX * pY) % 2 == 1 else 1
    return X_poly * Y_poly - Y_poly * X_poly * sign

def decompose_in_basis(poly, basis_list, generators):
    # Express poly as linear combination of generators in basis_list
    # Collect all unique monomials in basis
    all_monos = set()
    for b in basis_list:
        all_monos.update(generators[b].terms.keys())
    all_monos = sorted(list(all_monos), key=lambda m: (m.fp, m.fm, m.bp, m.bm))
    mono_to_idx = {m: i for i, m in enumerate(all_monos)}
    
    # Check if poly has any monomial not in all_monos
    for m in poly.terms.keys():
        if m not in mono_to_idx:
            return None # Cannot decompose
            
    # Set up linear system M * c = v
    # where columns of M are basis vectors
    import sympy
    M = sympy.zeros(len(all_monos), len(basis_list))
    for col, b in enumerate(basis_list):
        for m, coeff in generators[b].terms.items():
            M[mono_to_idx[m], col] = sympy.Rational(coeff.numerator, coeff.denominator)
            
    v = sympy.zeros(len(all_monos), 1)
    for m, coeff in poly.terms.items():
        v[mono_to_idx[m], 0] = sympy.Rational(coeff.numerator, coeff.denominator)
        
    # Solve system
    try:
        sol, params = M.gauss_jordan_solve(v)
        # Check if residual is 0
        residual = M * sol - v
        if any(r != 0 for r in residual):
            return None
        # Convert sol to dict of basis_name: Fraction
        res = {}
        for col, b in enumerate(basis_list):
            val = sol[col]
            if val != 0:
                res[b] = Fraction(int(val.p), int(val.q))
        return res
    except Exception as e:
        return None

for n in [1, 2, 3]:
    full_basis, even_basis, odd_basis, generators, parities = get_basis_and_generators(n)
    print(f"\n================= Testing C({n+1}) = osp(2|{2*n}) =================")
    print(f"Total generators: {len(full_basis)}, Even: {len(even_basis)}, Odd: {len(odd_basis)}")
    
    # Compute all brackets
    structure_constants = []
    non_zero_brackets = 0
    all_closed = True
    
    bracket_dict = {}
    
    for i, X in enumerate(full_basis):
        for j, Y in enumerate(full_basis):
            pX = parities[X]
            pY = parities[Y]
            br = graded_bracket(generators[X], pX, generators[Y], pY)
            bracket_dict[(X, Y)] = br
            if len(br.terms) > 0:
                non_zero_brackets += 1
                decomp = decompose_in_basis(br, full_basis, generators)
                if decomp is None:
                    print(f"FAILURE: [{X}, {Y}] not in basis! Terms: {br.terms}")
                    all_closed = False
                    break
                else:
                    for Z, coeff in decomp.items():
                        # Check parity conservation: pZ == (pX + pY) % 2
                        if parities[Z] != (pX + pY) % 2:
                            print(f"FAILURE: Parity mismatch! [{X}, {Y}] has component {Z}")
                            all_closed = False
                        structure_constants.append((X, Y, Z, coeff))
        if not all_closed:
            break
            
    print(f"All brackets closed in basis: {all_closed}")
    print(f"Non-zero ordered brackets (X, Y): {non_zero_brackets}")
    print(f"Total non-zero structure constant triples (X, Y, Z): {len(structure_constants)}")
    
    # Verify Graded Jacobi Identity:
    # (-1)^{pX pZ} [X, [Y, Z}} + (-1)^{pY pX} [Y, [Z, X}} + (-1)^{pZ pY} [Z, [X, Y}} = 0
    # Test sample or all triples
    jacobi_passed = True
    # For n=1, total 8^3 = 512 triples (test all)
    # For n=2, 19^3 = 6859 triples (test all)
    # For n=3, 34^3 = 39304 triples (test subset or all)
    import itertools
    triples_to_test = list(itertools.product(full_basis, full_basis, full_basis))
    if n == 3:
        # Sample 1000 triples or run all? Let's check time
        import random
        random.seed(42)
        triples_to_test = random.sample(triples_to_test, 2000)
        
    for X, Y, Z in triples_to_test:
        pX, pY, pZ = parities[X], parities[Y], parities[Z]
        # term 1: (-1)^{pX pZ} [X, [Y, Z}}
        br_YZ = bracket_dict[(Y, Z)]
        p_YZ = (pY + pZ) % 2
        term1 = graded_bracket(generators[X], pX, br_YZ, p_YZ) * ((-1)**((pX * pZ) % 2))
        
        # term 2: (-1)^{pY pX} [Y, [Z, X}}
        br_ZX = bracket_dict[(Z, X)]
        p_ZX = (pZ + pX) % 2
        term2 = graded_bracket(generators[Y], pY, br_ZX, p_ZX) * ((-1)**((pY * pX) % 2))
        
        # term 3: (-1)^{pZ pY} [Z, [X, Y}}
        br_XY = bracket_dict[(X, Y)]
        p_XY = (pX + pY) % 2
        term3 = graded_bracket(generators[Z], pZ, br_XY, p_XY) * ((-1)**((pZ * pY) % 2))
        
        jac = term1 + term2 + term3
        if len(jac.terms) > 0:
            print(f"FAILURE: Jacobi failed for ({X}, {Y}, {Z})! Terms: {jac.terms}")
            jacobi_passed = False
            break
            
    print(f"Graded Jacobi identity passed: {jacobi_passed}")
