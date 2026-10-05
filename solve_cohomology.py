import sympy as sp
from solver import get_generators, get_parity, bracket
from extract import extract_gen_coeffs

def solve_for_n(n):
    gens = get_generators(n)
    gen_names = list(gens.keys())
    num_gens = len(gen_names)
    
    # Precompute structure constants and gamma
    # struct_consts[X][Y] = {Z: coeff}
    # gamma[X][Y] = {Z: coeff}
    struct_consts = {}
    gamma = {}
    
    for i, X in enumerate(gen_names):
        struct_consts[X] = {}
        gamma[X] = {}
        for j, Y in enumerate(gen_names):
            pX = get_parity(X)
            pY = get_parity(Y)
            
            b = bracket(gens[X], gens[Y], pX, pY)
            
            b_0 = [t for t in b if t.kappa_power == 0]
            b_1 = [t for t in b if t.kappa_power == 1]
            
            # Decompose b_0
            c_0 = extract_gen_coeffs(b_0, gens)
            struct_consts[X][Y] = c_0
            
            # Decompose b_1 (which is gamma(X,Y))
            if b_1:
                # b_1 has some kappa, we just strip kappa and extract
                for t in b_1:
                    t.kappa_power = 0
                c_1 = extract_gen_coeffs(b_1, gens)
                gamma[X][Y] = c_1
            else:
                gamma[X][Y] = {g: 0 for g in gen_names}
                
    # Now setup the system of equations
    # gamma(X, Y) = delta f(X, Y)
    # delta f(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])
    
    # f is an odd linear map, so f(E) = sum phi_{E, O} O, f(O) = sum phi_{O, E} E
    # Let's create phi symbols
    phi = {}
    for X in gen_names:
        for Y in gen_names:
            if get_parity(X) != get_parity(Y):
                phi[(X, Y)] = sp.Symbol(f"phi_{X}_{Y}")
            else:
                phi[(X, Y)] = 0
                
    eqs = []
    
    # We will gather coefficients for each basis element Z in gamma(X, Y) - delta f(X,Y)
    for X in gen_names:
        for Y in gen_names:
            pX = get_parity(X)
            pY = get_parity(Y)
            
            for Z in gen_names:
                # delta f(X, Y)|_Z
                
                # term 1: (-1)^p(X) [X, f(Y)]|_Z
                term1 = 0
                for W in gen_names:
                    # f(Y) has component phi[(Y, W)] on W
                    # [X, W] has component struct_consts[X][W][Z] on Z
                    if phi[(Y, W)] != 0:
                        term1 += (-1)**pX * phi[(Y, W)] * struct_consts[X][W][Z]
                        
                # term 2: - (-1)^{(pX+1)*pY} [Y, f(X)]|_Z
                term2 = 0
                for W in gen_names:
                    if phi[(X, W)] != 0:
                        term2 -= (-1)**((pX+1)*pY) * phi[(X, W)] * struct_consts[Y][W][Z]
                        
                # term 3: - f([X, Y])|_Z
                term3 = 0
                for W in gen_names:
                    # [X, Y] has component struct_consts[X][Y][W] on W
                    # f(W) has component phi[(W, Z)] on Z
                    if phi[(W, Z)] != 0:
                        term3 -= struct_consts[X][Y][W] * phi[(W, Z)]
                        
                delta_f_val = term1 + term2 + term3
                gamma_val = gamma[X][Y][Z]
                
                expr = gamma_val - delta_f_val
                if expr != 0:
                    eqs.append(expr)
                    
    # Now we have a list of equations eqs = 0
    # The variables are phi's and gb's.
    # We want to know if there exists phi's for EVERY choice of gb?
    # No, we want to know FOR WHICH gb there exists phi.
    # So we write the equations as M * phi = N * gb.
    # The condition for existence of phi is that N * gb is in the column space of M.
    # So (I - M M^+) N * gb = 0.
    
    phi_vars = [phi[k] for k in phi if phi[k] != 0]
    # find all gb variables
    gb_vars = set()
    for e in eqs:
        gb_vars.update([s for s in e.free_symbols if str(s).startswith('gb')])
    gb_vars = list(gb_vars)
    
    # Construct Matrix M (coeff of phi) and N (coeff of gb, wait: eq is N*gb - M*phi = 0 => M*phi = N*gb)
    M = sp.zeros(len(eqs), len(phi_vars))
    N = sp.zeros(len(eqs), len(gb_vars))
    
    for i, e in enumerate(eqs):
        for j, p in enumerate(phi_vars):
            M[i, j] = -e.coeff(p) # since expr = gamma - delta_f, phi is in -delta_f. So expr = gamma(gb) - M*phi. M*phi = gamma.
        for j, g in enumerate(gb_vars):
            N[i, j] = e.coeff(g)
            
    print(f"Matrix M shape: {M.shape}")
    print(f"Matrix N shape: {N.shape}")
    
    # We can just use sympy to find relations on gb
    # Put [M | N] into row echelon form
    aug = M.row_join(N)
    reduced, pivots = aug.rref()
    
    # The rows of `reduced` that have all zeros in the M part (columns 0 to len(phi)-1)
    # but non-zeros in the N part (columns len(phi) to end) give the conditions on gb.
    conditions = []
    for i in range(reduced.shape[0]):
        # check if M part is zero
        is_M_zero = True
        for j in range(len(phi_vars)):
            if reduced[i, j] != 0:
                is_M_zero = False
                break
        
        if is_M_zero:
            # check N part
            cond = 0
            for j in range(len(gb_vars)):
                if reduced[i, len(phi_vars) + j] != 0:
                    cond += reduced[i, len(phi_vars) + j] * gb_vars[j]
            if cond != 0:
                conditions.append(cond)
                
    print(f"Number of conditions on gb: {len(conditions)}")
    for c in conditions:
        print(f"0 = {c}")

if __name__ == "__main__":
    solve_for_n(1)
