"""Hand-checked sanity tests for the oscillator engine (run: python3 scripts/test_engine.py)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fractions import Fraction as F
from osc_algebra import OscAlgebra, ONE, p_add

A = OscAlgebra(1)
P = lambda w: {w: dict(ONE)}
gb = lambda sigma, j, s: A.gb_index[(sigma, j, s)]

checks = []

# a- a+ = 1 - a+ a-
r = A.normal_word((2, 1))
checks.append(("a- a+ = 1 - a+ a-", r == {(): {(): F(1)}, (1, 2): {(): F(-1)}}))

# b- b+ = b+ b- + 1
r = A.normal_word((4, 3))
checks.append(("b- b+ = b+ b- + 1", r == {(): {(): F(1)}, (3, 4): {(): F(1)}}))

# b1+ a+ = a+ b1+ - gb(+,1,+) kappa
r = A.normal_word((3, 1))
checks.append(("b1+ a+ = a+ b1+ - gb(+,1,+) kappa",
               r == {(1, 3): {(): F(1)}, (0,): {(gb('+', 1, '+'),): F(-1)}}))

# a+ kappa = - kappa a+
r = A.normal_word((1, 0))
checks.append(("a+ kappa = -kappa a+", r == {(0, 1): {(): F(-1)}}))

# kappa^2 = 0, (a+)^2 = 0
checks.append(("kappa^2 = 0", A.normal_word((0, 0)) == {}))
checks.append(("(a+)^2 = 0", A.normal_word((1, 1)) == {}))

# [a+ b1+, (b1-)^2] = -2 a+ b1- + 2 gb(+,1,-) kappa (b1+ b1- + 1)
r = A.supercomm(P((1, 3)), P((4, 4)))
exp = {(1, 4): {(): F(-2)},
       (0, 3, 4): {(gb('+', 1, '-'),): F(2)},
       (0,): {(gb('+', 1, '-'),): F(2)}}
checks.append(("[a+ b1+, (b1-)^2]", r == exp))

# {a+ b1+, a- b1-} = (1 - a+a-) + b1+ b1- + kappa(gb(-,1,+) a+ b1- + gb(+,1,-) a- b1+)
r = A.supercomm(P((1, 3)), P((2, 4)))
exp = {(): {(): F(1)}, (1, 2): {(): F(-1)}, (3, 4): {(): F(1)},
       (0, 1, 4): {(gb('-', 1, '+'),): F(1)},
       (0, 2, 3): {(gb('+', 1, '-'),): F(1)}}
checks.append(("{a+ b1+, a- b1-}", r == exp))

# shifted boson  bt = b1+ + kappa (gb(-,1,+) a+ + gb(+,1,+) a-)  commutes with a+, a-
c = {(0, 1): {(gb('-', 1, '+'),): F(1)}, (0, 2): {(gb('+', 1, '+'),): F(1)}}
bt = p_add(P((3,)), c)
checks.append(("[b~1+, a+] = 0", A.supercomm(bt, P((1,))) == {}))
checks.append(("[b~1+, a-] = 0", A.supercomm(bt, P((2,))) == {}))
# [b~1-, b~1+] = 1
c2 = {(0, 1): {(gb('-', 1, '-'),): F(1)}, (0, 2): {(gb('+', 1, '-'),): F(1)}}
bt2 = p_add(P((4,)), c2)
checks.append(("[b~1-, b~1+] = 1", A.supercomm(bt2, bt) == {(): {(): F(1)}}))

ok = True
for name, res in checks:
    print(("PASS " if res else "FAIL ") + name)
    ok &= res
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
