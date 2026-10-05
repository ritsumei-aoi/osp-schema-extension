import test_jacobi
import verify_all_n

# Compare the C matrices for n=1:
dim = 8
names = test_jacobi.names

# Let's get C from verify_all_n
# In verify_all_n for n=1:
# basis:
# 0: J
# 1: B((1,+), (1,+)) = B(1+, 1+) -> index in test_jacobi: 1 (E)
# 2: B((1,+), (1,-)) = B(1+, 1-) -> index in test_jacobi: 3 (H)
# 3: B((1,-), (1,-)) = B(1-, 1-) -> index in test_jacobi: 2 (F)
# 4: F('+', (1,+)) -> index in test_jacobi: 4 (F++)
# 5: F('+', (1,-)) -> index in test_jacobi: 5 (F+-)
# 6: F('-', (1,+)) -> index in test_jacobi: 6 (F-+)
# 7: F('-', (1,-)) -> index in test_jacobi: 7 (F--)

perm = [0, 1, 3, 2, 4, 5, 6, 7] # mapping from verify_all_n index to test_jacobi index
# inverse perm:
inv_perm = [perm.index(i) for i in range(8)]

# Let's inspect where C differs!
for i in range(8):
    for j in range(8):
        # test_jacobi:
        c_tj = test_jacobi.C[(i, j)]
        # verify_all_n:
        vi, vj = inv_perm[i], inv_perm[j]
        # let's run the C computation from verify_all_n:
