"""Compute triviality conditions for C(2) = osp(2|2), n=1."""
import numpy as np
import json

n = 1; n_max = 10
dim_total = 2 * n_max

def idx(nf, nb): return nf * n_max + nb

ap = np.zeros((dim_total, dim_total))
am = np.zeros((dim_total, dim_total))
bp = np.zeros((dim_total, dim_total))
bm = np.zeros((dim_total, dim_total))

for nf in [0, 1]:
    for nb in range(n_max):
        s = idx(nf, nb)
        if nf == 0: ap[idx(1, nb), s] = 1.0
        if nf == 1: am[idx(0, nb), s] = 1.0
        if nb + 1 < n_max: bp[idx(nf, nb+1), s] = np.sqrt(nb + 1)
        if nb > 0: bm[idx(nf, nb-1), s] = np.sqrt(nb)

I = np.eye(dim_total)

H1 = ap @ am + bp @ bm
H2 = -bp @ bm - 0.5 * I
ep = 0.5 * bp @ bp
em = 0.5 * bm @ bm
o1 = ap @ bp
o2 = ap @ bm
o3 = am @ bp
o4 = am @ bm

gens = [('H_1', H1, 0), ('H_2', H2, 0), ('E_2d', ep, 0), ('E_-2d', em, 0),
        ('o1_e+d', o1, 1), ('o2_e-d', o2, 1), ('o3_-e+d', o3, 1), ('o4_-e-d', o4, 1)]

names = [g[0] for g in gens]
mats = [g[1] for g in gens]
pars = [g[2] for g in gens]
n_gen = len(gens)

V = np.column_stack([m.flatten() for m in mats])
print(f"Rank check: {np.linalg.matrix_rank(V, tol=1e-8)} (expect 8)")


def sbracket(A, pA, B, pB):
    return A @ B - ((-1) ** (pA * pB)) * B @ A


def decompose(mat, basis_mats, identity):
    cols = [m.flatten() for m in basis_mats] + [identity.flatten()]
    A = np.column_stack(cols)
    c, _, _, _ = np.linalg.lstsq(A, mat.flatten(), rcond=None)
    return c[:-1], c[-1]


sc = {}
print("\nStructure constants:")
for i in range(n_gen):
    for j in range(i, n_gen):
        br = sbracket(mats[i], pars[i], mats[j], pars[j])
        c, s = decompose(br, mats, I)
        d = {}
        for k in range(n_gen):
            val = round(c[k] * 4) / 4
            if abs(val) > 1e-6:
                d[k] = val
        sc[(i, j)] = d
        sign = -((-1) ** (pars[i] * pars[j]))
        sc[(j, i)] = {k: sign * v for k, v in d.items()}
        if d:
            terms = [f"{v:+g}*{names[k]}" for k, v in sorted(d.items())]
            print(f"  [{names[i]}, {names[j]}] = {' '.join(terms)}")

print("\nGamma computation:")
gb_names = ['gb_+1+', 'gb_+1-', 'gb_-1+', 'gb_-1-']
eps_val = 1e-5

gamma_comp = {}
for gi, gb_name in enumerate(gb_names):
    sigma = gb_name[3]
    s_sign = gb_name[5]

    a_neg = am if sigma == '+' else ap
    bp_d = bp + eps_val * a_neg if s_sign == '+' else bp.copy()
    bm_d = bm + eps_val * a_neg if s_sign == '-' else bm.copy()

    H1_d = ap @ am + bp_d @ bm_d
    H2_d = -bp_d @ bm_d - 0.5 * I
    ep_d = 0.5 * bp_d @ bp_d
    em_d = 0.5 * bm_d @ bm_d
    o1_d = ap @ bp_d
    o2_d = ap @ bm_d
    o3_d = am @ bp_d
    o4_d = am @ bm_d
    mats_d = [H1_d, H2_d, ep_d, em_d, o1_d, o2_d, o3_d, o4_d]

    gc = {}
    for i in range(n_gen):
        for j in range(n_gen):
            br_d = sbracket(mats_d[i], pars[i], mats_d[j], pars[j])
            br_o = sbracket(mats[i], pars[i], mats[j], pars[j])
            corr = (br_d - br_o) / eps_val
            c, s_coeff = decompose(corr, mats, I)
            d = {}
            for k in range(n_gen):
                val = round(c[k] * 4) / 4
                if abs(val) > 0.05:
                    d[k] = val
            if d:
                gc[(i, j)] = d

    gamma_comp[gb_name] = gc
    print(f"  {gb_name}: {sum(len(v) for v in gc.values())} nonzero entries")
    for (i, j), d in sorted(gc.items()):
        terms = [f"{v:+g}*{names[k]}" for k, v in sorted(d.items())]
        if i <= j:
            print(f"    gamma({names[i]},{names[j]}) = {' '.join(terms)}")

phi_idx = [(a, b) for a in range(n_gen) for b in range(n_gen) if pars[a] != pars[b]]
eq_idx = [(i, j, k) for i in range(n_gen) for j in range(i + 1, n_gen) for k in range(n_gen)]
n_phi = len(phi_idx)
n_eq = len(eq_idx)


def get_sc(i, j, k):
    return sc.get((i, j), {}).get(k, 0.0)


A_cob = np.zeros((n_eq, n_phi))
for row, (i, j, k) in enumerate(eq_idx):
    pi, pj = pars[i], pars[j]
    for col, (a, b) in enumerate(phi_idx):
        val = 0.0
        if b == j:
            val += ((-1) ** pi) * get_sc(i, a, k)
        if b == i:
            val -= ((-1) ** ((pi + 1) * pj)) * get_sc(j, a, k)
        if a == k:
            val -= get_sc(i, j, b)
        A_cob[row, col] = val

B_mat = np.zeros((n_eq, 4))
for gb_idx, gb_name in enumerate(gb_names):
    gc = gamma_comp[gb_name]
    for row, (i, j, k) in enumerate(eq_idx):
        if (i, j) in gc:
            B_mat[row, gb_idx] = gc[(i, j)].get(k, 0.0)

print(f"\nCoboundary A: {A_cob.shape}, rank={np.linalg.matrix_rank(A_cob, tol=1e-3)}")
print(f"Gamma B: {B_mat.shape}")

tol = 1e-3
U, S, Vt = np.linalg.svd(A_cob, full_matrices=True)
rank_A = int(np.sum(S > tol))
P = U[:, :rank_A] @ U[:, :rank_A].T

constraint = (np.eye(n_eq) - P) @ B_mat
U2, S2, Vt2 = np.linalg.svd(constraint, full_matrices=True)
n_con = int(np.sum(np.abs(S2) > tol))

print(f"\nRank of coboundary image: {rank_A}")
print(f"Constraints on gb: {n_con}")
print(f"Trivial space dim: {4 - n_con}")

if n_con == 4:
    print("=> ONLY gb=0 is trivial")
elif n_con == 0:
    print("=> ALL deformations are trivial")
else:
    print(f"=> {4 - n_con}-dim trivial subspace")
    print(f"Singular values: {S2}")

for gb_idx, gb_name in enumerate(gb_names):
    b_col = B_mat[:, gb_idx]
    resid = (np.eye(n_eq) - P) @ b_col
    print(f"  {gb_name}: |residual| = {np.linalg.norm(resid):.6f}")
    if np.linalg.norm(resid) < tol:
        phi_sol, _, _, _ = np.linalg.lstsq(A_cob, b_col, rcond=None)
        print(f"    => trivial (coboundary), f-params found")

print("\nDone.")
