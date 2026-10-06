"""Closed-form odd map f_gb realizing the gauge transformation b_j^s -> b_j^s + kappa*u_{j,s}.

In the deformed algebra [b_j^s, a^sigma] = -gb_{sigma,j,s} kappa.  Put b' = b + kappa*u with
    u_{j,s} = gb_{+,j,s} a_1^-  +  gb_{-,j,s} a_1^+ ,
then [b'_j^s, a^tau] = -gb_{tau,j,s} kappa + kappa {u_{j,s}, a^tau} = 0, i.e. the primed oscillators satisfy the
undeformed relations.  Writing a generator X (a quadratic) in terms of b' gives X' = X + kappa*f(X) + ...,
where f = D is the odd derivation of the (Weyl-symmetrised) quadratics with D(b_j^s) = u_{j,s}, D(a) = 0:
    D(S(xy)) = S(D(x) y) + (-1)^{p(x)} S(x D(y)).
closed_form_f returns D as {(to, from): coeff} on the basis of g; the trivializing map is f = -D
(verified exactly: delta(-D_gb) = gamma(gb) for every tested gb, see tests/test_coboundary.py).
"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import CAlgebra  # noqa: E402
from oscalg import AM, AP, OscAlgebra, letter_parity  # noqa: E402


def u_of(gb, j, s):
    """u_{j,s} as {letter: coeff}; gb keyed by (sigma, j, s)."""
    u = {}
    g_plus, g_minus = Fraction(gb.get(("p", j, s), 0)), Fraction(gb.get(("m", j, s), 0))
    if g_plus:
        u[AM] = g_plus
    if g_minus:
        u[AP] = g_minus
    return u


def _sym(osc, x, y):
    """Weyl-symmetrisation S(xy) = (xy + (-1)^{p(x)p(y)} yx)/2 as normal-ordered element."""
    out = {}
    OscAlgebra._add(out, osc.normal((x, y)), Fraction(1, 2))
    OscAlgebra._add(out, osc.normal((y, x)), Fraction(1, 2) * (-1) ** (letter_parity(x) * letter_parity(y)))
    return out


def trivializing_f(n, gb):
    """f = -D_gb with delta f = gamma(gb)."""
    return {k: -v for k, v in closed_form_f(n, gb).items()}


def closed_form_f(n, gb):
    """D_gb as {(to, frm): coeff}.  gb: {(sigma, j, s): number}."""
    alg = CAlgebra(n)
    osc = OscAlgebra()
    f = {}
    for frm in alg.labels:
        img = {}
        for w, c in alg.real[frm].items():
            if len(w) != 2:
                continue  # constants are annihilated by D
            x, y = w
            # S(D(x) y)
            if x >= 3:
                j, s = (x - 3) // 2 + 1, "p" if (x - 3) % 2 == 0 else "m"
                for ul, uc in u_of(gb, j, s).items():
                    OscAlgebra._add(img, _sym(osc, ul, y), c * uc)
            # (-1)^{p(x)} S(x D(y))
            if y >= 3:
                j, s = (y - 3) // 2 + 1, "p" if (y - 3) % 2 == 0 else "m"
                for ul, uc in u_of(gb, j, s).items():
                    OscAlgebra._add(img, _sym(osc, x, ul), c * uc * (-1) ** letter_parity(x))
        if not img:
            continue
        co, resid = alg.decompose(img)
        # symmetrised quadratics are in span(g) + constant; constants only arise via normal ordering of
        # S(a+ a-) = N_a - 1/2 which lies in span(H); anything else is an error
        if resid:
            raise ValueError(f"D({frm}) not in g: {resid}")
        for i, cc in co.items():
            f[(alg.labels[i], frm)] = cc
    return f
