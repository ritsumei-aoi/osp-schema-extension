import sys
sys.path.append('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-A1/.gemini/antigravity-cli/brain/654dfce4-b8df-497b-869d-784f1053ddd2/scratch')
import C_generators as cg
from fractions import Fraction

for n in [1, 2, 3]:
    schema = cg.build_schema1_json(n)
    sc = schema['structure_constants']
    par = schema['parity']
    
    # Store in dict
    sc_dict = {}
    for entry in sc:
        sc_dict[(entry['X'], entry['Y'], entry['Z'])] = Fraction(entry['coeff'])
        
    # Check graded antisymmetry: [Y, X} = - (-1)^{pX pY} [X, Y}
    anti_fails = 0
    checked_pairs = set()
    for (x, y, z), coeff in sc_dict.items():
        px, py = par[x], par[y]
        expected_other = - (-1)**(px * py) * coeff
        actual_other = sc_dict.get((y, x, z), Fraction(0))
        if actual_other != expected_other:
            anti_fails += 1
            print(f"Antisymmetry fail for ({x}, {y}, {z}): {coeff} vs {actual_other}")
            
    print(f"n={n}: Graded antisymmetry checked ({len(sc)} brackets): failures={anti_fails}")
    
    # Check Graded Jacobi identity
    basis = schema['basis']['odd'] + schema['basis']['even']
    dim = len(basis)
    jacobi_fails = 0
    for i in range(dim):
        x = basis[i]
        px = par[x]
        for j in range(dim):
            y = basis[j]
            py = par[y]
            for k in range(dim):
                z = basis[k]
                pz = par[z]
                
                s_x = (-1)**(px * pz)
                s_y = (-1)**(py * px)
                s_z = (-1)**(pz * py)
                
                for l in range(dim):
                    w = basis[l]
                    val = Fraction(0)
                    for m in range(dim):
                        u = basis[m]
                        # s_x * [X, [Y, Z]]
                        c_yz_u = sc_dict.get((y, z, u), Fraction(0))
                        if c_yz_u != 0:
                            c_xu_w = sc_dict.get((x, u, w), Fraction(0))
                            if c_xu_w != 0:
                                val += s_x * c_yz_u * c_xu_w
                        # s_y * [Y, [Z, X]]
                        c_zx_u = sc_dict.get((z, x, u), Fraction(0))
                        if c_zx_u != 0:
                            c_yu_w = sc_dict.get((y, u, w), Fraction(0))
                            if c_yu_w != 0:
                                val += s_y * c_zx_u * c_yu_w
                        # s_z * [Z, [X, Y]]
                        c_xy_u = sc_dict.get((x, y, u), Fraction(0))
                        if c_xy_u != 0:
                            c_zu_w = sc_dict.get((z, u, w), Fraction(0))
                            if c_zu_w != 0:
                                val += s_z * c_xy_u * c_zu_w
                                
                    if val != 0:
                        jacobi_fails += 1
    print(f"n={n}: Graded Jacobi checked ({dim**3} triples): failures={jacobi_fails}")
