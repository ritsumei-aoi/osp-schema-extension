"""
Verification artifacts for the triviality theorem of C(n+1) = osp(2|2n)
inhomogeneous deformations.

Theorem: gamma_gb is trivial (= delta f up to scalar) iff all gb = 0.

This script encodes the key structure constants and obstruction witnesses
in machine-readable form to support future computational verification.
"""

# ─── Root data for C(2) = osp(2|2), n=1 ────────────────────────────────────
# Generators: (label, parity, oscillator expression)
GENERATORS_N1 = [
    ("H1",    0, "a+a- + b+b-"),
    ("H2",    0, "-b+b- - 1/2"),
    ("E2d",   0, "(1/2)(b+)^2"),
    ("E-2d",  0, "(1/2)(b-)^2"),
    ("Eed",   1, "a+b+"),
    ("Eed-",  1, "a+b-"),
    ("E-ed",  1, "a-b+"),
    ("E-ed-", 1, "a-b-"),
]

# Root eigenvalues: (root_label, H1_eigenvalue, H2_eigenvalue)
# Meaning: [Hi, E_root] = eigenvalue_i * E_root
ROOT_EIGENVALUES = [
    ("e+d",  2,  -1),
    ("e-d",  0,   1),
    ("-e+d", 0,  -1),
    ("-e-d", -2,  1),
    ("2d",   2,  -2),
    ("-2d",  -2,  2),
]

# ─── gamma_gb structure constants (n=1, mod scalar K) ───────────────────────
# Format: { (X_label, Y_label): {gen_label: coeff_string} }
# Parity of gamma(X,Y) = p(X)+p(Y)+1 mod 2  (from p(kappa)=1)
# Computed from deformed oscillator algebra: b^s a^sigma = a^sigma b^s - gb*kappa
GAMMA_GB_N1 = {
    # odd-odd pairs -> odd result (p=1+1+1=1)
    ("Eed-", "E-ed-"): {"Eed-": "-gb_pm", "E-ed-": "-gb_mm"},
    ("Eed",  "E-ed"):  {"Eed":  "-gb_mp",  "E-ed":  "-gb_pp"},
    # even-odd pairs -> even result (p=0+1+1=0)
    ("H2", "Eed-"):  {"H2":  "-gb_pm"},        # g-component modulo K
    ("H2", "E-ed-"): {"H2":  "-gb_mm"},
    ("H2", "Eed"):   {"E2d": "2*gb_pm"},
    ("H2", "E-ed"):  {"E2d": "2*gb_mm"},
}

# ─── Key Lie superalgebra brackets (undeformed) ─────────────────────────────
BRACKETS_N1 = {
    # { (X, Y): result_description }
    ("Eed-", "E-ed-"): "2*E-2d",          # [E_{e-d}, E_{-e-d}] = 2 E_{-2d}
    ("Eed",  "E-ed"):  "2*E2d",            # [E_{e+d}, E_{-e+d}] = 2 E_{2d}
    ("Eed-", "E-ed"):  "H1",               # [E_{e-d}, E_{-e+d}] = H1 = N_f+N_b
    ("Eed",  "E-ed-"): "-H1 - 2*H2",      # mod scalar K
    ("Eed-", "Eed"):   "0",               # (a+)^2 = 0
    ("E-ed-","E-ed"):  "0",               # (a-)^2 = 0
}

# ─── Image analysis: key obstruction ────────────────────────────────────────
# [E_{e-d}, E_beta]_0 for beta in odd generators
IMAGE_E_ED_MINUS = {
    "Eed-":  "0",       # (a+)^2 = 0
    "Eed":   "0",       # (a+)^2 = 0
    "E-ed-": "2*E-2d",  # = 2 E_{-2delta}
    "E-ed":  "H1",      # = N_f + N_b
}
# H2 is NOT in this image. This is the key obstruction.

# [E_{e+d}, E_beta]_0 for beta in odd generators
IMAGE_E_ED_PLUS = {
    "Eed-":  "0",
    "Eed":   "0",
    "E-ed-": "-H1-2*H2",  # mod scalar K
    "E-ed":  "2*E2d",
}

# ─── Obstruction witnesses ───────────────────────────────────────────────────
OBSTRUCTIONS = [
    {
        "pair": ("H2", "Eed-"),
        "gamma": {"H2": "-gb_pm"},
        "coboundary_requires": "[E_{e-d}, f(H2)] must contain -2*gb_pm * H2",
        "image_of_E_ed_minus_contains_H2": False,
        "conclusion": "gb_pm = 0 is necessary for triviality",
    },
    {
        "pair": ("H2", "E-ed-"),
        "gamma": {"H2": "-gb_mm"},
        "coboundary_requires": "[E_{-e-d}, f(H2)] must contain -2*gb_mm * H2",
        "image_of_E_minus_ed_minus_contains_H2": False,
        "conclusion": "gb_mm = 0 is necessary for triviality",
    },
    {
        "pair": ("H2", "Eed"),
        "gamma": {"E2d": "2*gb_pm"},
        "coboundary_requires": "H1 coefficient in [E_{e+d}, f(H2)] must vanish, forcing H2 coeff=0, giving gb_pp=0",
        "conclusion": "gb_pp = 0 is necessary for triviality",
    },
    {
        "pair": ("H2", "E-ed"),
        "gamma": {"E2d": "2*gb_mm"},
        "conclusion": "gb_mp = 0 is necessary for triviality",
    },
]

# ─── Main theorem data ───────────────────────────────────────────────────────
def triviality_theorem(n):
    """
    Returns structured data for the triviality theorem for C(n+1) = osp(2|2n).
    """
    params = {f"gb_{s}{j}{t}": 0
              for j in range(1, n+1)
              for s in ["+", "-"]
              for t in ["+", "-"]}
    return {
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "n_deformation_params": 4 * n,
        "theorem": "gamma_gb trivial (= delta_f up to scalar) iff all gb = 0",
        "triviality_conditions": params,
        "obstruction_generators": [f"(H2, E_{{eps-delta_{j}}})" for j in range(1, n+1)] +
                                   [f"(H2, E_{{eps+delta_{j}}})" for j in range(1, n+1)],
        "structural_reason": (
            "H2 (so(2) Cartan of osp(2|2n)) is not in the image of ad(E_{eps-delta_j}) "
            "restricted to g_odd; hence [E_{eps-delta_j}, f(H2)] cannot produce H2-terms, "
            "while gamma_gb(H2, E_{eps-delta_j}) = -gb_{+,j,-} * H2 is nonzero if gb!=0."
        ),
    }

# ─── Run and print ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("TRIVIALITY THEOREM: C(n+1) INHOMOGENEOUS DEFORMATION")
    print("=" * 65)
    for n in [1, 2, 3]:
        t = triviality_theorem(n)
        print(f"\n  {t['algebra']}")
        print(f"  Parameters: {t['n_deformation_params']}")
        print(f"  Theorem: {t['theorem']}")
        print(f"  Obstructions from: {t['obstruction_generators']}")

    print("\n" + "=" * 65)
    print("GAMMA_GB STRUCTURE CONSTANTS (n=1, mod scalar K)")
    print("=" * 65)
    for (X, Y), val in GAMMA_GB_N1.items():
        print(f"  gamma_gb({X}, {Y}) = {val}")

    print("\n" + "=" * 65)
    print("OBSTRUCTION WITNESSES")
    print("=" * 65)
    for obs in OBSTRUCTIONS:
        print(f"  Pair {obs['pair']}: {obs['conclusion']}")

    print("\n" + "=" * 65)
    print("ADJOINT IMAGE (key fact: H2 not in image)")
    print("=" * 65)
    print("  [E_{e-d}, E_beta] for odd E_beta:")
    for gen, result in IMAGE_E_ED_MINUS.items():
        print(f"    beta={gen}: {result}")
    print(f"  => H2 in image? {any('H2' in v for v in IMAGE_E_ED_MINUS.values())}")
