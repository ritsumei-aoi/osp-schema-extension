"""
osp_engine.py  (kappa-odd corrected)
====================================

Oscillator engine for C(n+1) = osp(2|2n) and its inhomogeneous (gb) deformation.

Conventions (see docs/math/):
  Fermionic pair a1^+ , a1^-   with  {a1^-, a1^+} = 1 , (a1^±)^2 = 0.
  Bosonic pairs  b_j^+ , b_j^-  with  [b_j^-, b_k^+] = delta_{jk}.
  Deformed:      [b_j^s, a1^sigma] = - gb_{sigma, j, s} * kappa ,
                 i.e.  b_j^s a1^sigma = a1^sigma b_j^s - gb_{sigma,j,s} kappa.
  kappa : ODD, central, kappa^2 = 0 (first order in kappa).

IMPORTANT: kappa is ODD.  We keep it as an exponent kpow in {0,1} but ALWAYS
imagine it sitting at the far LEFT of the monomial.  Whenever kappa has to pass
oscillator content of parity p, it contributes a sign (-1)^p.  Two places need
this sign:
  (A) product of X (left) and Y=kappa^{kpY} tY (right): moving kappa^{kpY} left
      past tX gives (-1)^{parity(tX)*kpY};
  (B) a b->a reordering that *generates* kappa in the middle of a monomial:
      moving that kappa to the far left past the current prefix gives
      (-1)^{parity(prefix)}.

Element representation: dict  { (kpow, tokens_tuple) : coeff }  meaning
  coeff * kappa^kpow * (tokens in normal order),   kappa leftmost.

Tokens: ('a','+'), ('a','-'), ('b','+',j), ('b','-',j),  1<=j<=n.
"""

from sympy import symbols, simplify


def make_gb_symbols(n):
    gb = {}
    for sigma in ('+', '-'):
        for j in range(1, n + 1):
            for s in ('+', '-'):
                gb[(sigma, j, s)] = symbols(f"gb_{sigma}{j}{s}")
    return gb


def tok_key(t):
    if t[0] == 'a':
        return (0, 0 if t[1] == '+' else 1, 0)
    return (1, 0 if t[1] == '+' else 1, t[2])


def _fermion_parity(toks):
    return sum(1 for t in toks if t[0] == 'a') % 2


def reduce_monomial(kpow, tokens, coeff, gb):
    """Normal-order coeff * kappa^kpow * tokens.  Returns {(kpow,tuple):coeff}."""
    out = {}
    stack = [(kpow, list(tokens), coeff)]
    while stack:
        kp, toks, c = stack.pop()
        if c == 0 or kp >= 2:
            continue
        action = None
        for i in range(len(toks) - 1):
            L, R = toks[i], toks[i + 1]
            if L[0] == 'a' and R[0] == 'a' and L[1] == R[1]:
                action = ('zero', i); break
            if tok_key(L) > tok_key(R):
                action = ('swap', i); break
        if action is None:
            key = (kp, tuple(toks))
            out[key] = out.get(key, 0) + c
            continue
        kind, i = action
        if kind == 'zero':
            continue
        L, R = toks[i], toks[i + 1]
        base, rest = toks[:i], toks[i + 2:]
        if L[0] == 'b' and R[0] == 'a':
            # b a = a b - gb kappa ; kappa generated at position i -> move to far
            # left past `base`, sign (-1)^{parity(base)}.
            sigma, s, j = R[1], L[1], L[2]
            stack.append((kp, base + [R, L] + rest, c))               # a b  (swap)
            sign = -1 if _fermion_parity(base) % 2 else 1
            stack.append((kp + 1, base + rest, -c * gb[(sigma, j, s)] * sign))
        elif L[0] == 'a' and R[0] == 'a':
            # L='-', R='+':  a- a+ = -a+ a- + 1
            stack.append((kp, base + [R, L] + rest, -c))
            stack.append((kp, base + rest, c))
        elif L[0] == 'b' and R[0] == 'b':
            if L[1] == '-' and R[1] == '+':
                stack.append((kp, base + [R, L] + rest, c))
                if L[2] == R[2]:
                    stack.append((kp, base + rest, c))
            else:
                stack.append((kp, base + [R, L] + rest, c))
        else:
            raise RuntimeError(f"unexpected pair {L},{R}")
    return {k: v for k, v in out.items() if v != 0}


def normal_order(element, gb):
    out = {}
    for (kp, toks), c in element.items():
        for k, v in reduce_monomial(kp, toks, c, gb).items():
            out[k] = out.get(k, 0) + v
    return {k: simplify(v) for k, v in out.items() if simplify(v) != 0}


def mul(X, Y, gb):
    """Product X*Y.  kappa of Y must pass tokens of X -> sign (-1)^{p(tX)*kpY}."""
    out = {}
    for (kpX, tX), cX in X.items():
        for (kpY, tY), cY in Y.items():
            if kpX + kpY >= 2:
                continue
            sign = -1 if (_fermion_parity(tX) * kpY) % 2 else 1
            for k, v in reduce_monomial(kpX + kpY, list(tX) + list(tY),
                                        cX * cY * sign, gb).items():
                out[k] = out.get(k, 0) + v
    return {k: simplify(v) for k, v in out.items() if simplify(v) != 0}


def add(X, Y, scale=1):
    out = dict(X)
    for k, v in Y.items():
        out[k] = out.get(k, 0) + scale * v
    return {k: v for k, v in out.items() if v != 0}


def super_bracket(X, Y, pX, pY, gb):
    """[X,Y] = X Y - (-1)^{pX pY} Y X  (super-commutator in U(A))."""
    XY = mul(X, Y, gb)
    YX = mul(Y, X, gb)
    sign = -1 if (pX * pY) % 2 == 1 else 1
    return add(XY, YX, scale=-sign)
