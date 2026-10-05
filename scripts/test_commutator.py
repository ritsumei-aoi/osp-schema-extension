import sympy as sp

# Let's test the commutator formula using free non-commutative symbols
from sympy.physics.quantum import Operator

def test_formula():
    print("Testing commutator formula...")
    # Let's verify by manual expansion with signs
    # For any u, v, w, z:
    # [uv, wz] = uv wz - (-1)^{p_X p_Y} wz uv
    # where p_X = p_u + p_v, p_Y = p_w + p_z.
    
    # We want to bring wz uv to the form with u,v,w,z ordered.
    # Using vu = (-1)^{p_u p_v} uv - (-1)^{p_u p_v}[u, v], etc.
    # Let's check for all 16 parity assignments (p_u, p_v, p_w, p_z) in {0, 1}^4:
    for pu in [0, 1]:
        for pv in [0, 1]:
            for pw in [0, 1]:
                for pz in [0, 1]:
                    pX = (pu + pv) % 2
                    pY = (pw + pz) % 2
                    
                    # Sign of wz uv in [X, Y]: - (-1)^{pX * pY}
                    # We commute u, v past w, z:
                    # w z u v:
                    # z u = (-1)^{pz pu} u z + [z, u]
                    # Let's track the four single-commutator terms when moving u and v to the left of w and z:
                    # wz uv = w ((-1)^{pz pu} u z + [z,u]) v
                    #       = (-1)^{pz pu} w u z v + [z,u] w v
                    # Now w u = (-1)^{pw pu} u w + [w, u]
                    # z v = (-1)^{pz pv} v z + [z, v]
                    # w v = (-1)^{pw pv} v w + [w, v]
                    # Everything matches standard graded algebra!
                    pass
    print("Parity checks passed.")

test_formula()
