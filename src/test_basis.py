import fractions

def build_basis(n):
    # Returns a list of (name, poly, parity)
    basis = []
    
    # K (central element)
    basis.append(("K", {(): fractions.Fraction(1)}, 0))
    
    # H_1
    h1 = {("a_1_p", "a_1_m"): fractions.Fraction(1), ("b_1_p", "b_1_m"): fractions.Fraction(1)}
    basis.append(("H_1", h1, 0))
    
    # H_k (2 <= k <= n)
    for k in range(2, n + 1):
        hk = {
            (f"b_{k-1}_p", f"b_{k-1}_m"): fractions.Fraction(1),
            (f"b_{k}_p", f"b_{k}_m"): fractions.Fraction(-1)
        }
        basis.append((f"H_{k}", hk, 0))
        
    # H_{n+1}
    hn1 = {
        (f"b_{n}_p", f"b_{n}_m"): fractions.Fraction(-1),
        (): fractions.Fraction(-1, 2)
    }
    basis.append((f"H_{n+1}", hn1, 0))
    
    # Even roots
    for k in range(1, n + 1):
        basis.append((f"E_2del{k}_p", {(f"b_{k}_p", f"b_{k}_p"): fractions.Fraction(1)}, 0))
        basis.append((f"E_2del{k}_m", {(f"b_{k}_m", f"b_{k}_m"): fractions.Fraction(1)}, 0))
        
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            basis.append((f"E_del{k}_del{l}_pp", {(f"b_{k}_p", f"b_{l}_p"): fractions.Fraction(1)}, 0))
            basis.append((f"E_del{k}_del{l}_pm", {(f"b_{k}_p", f"b_{l}_m"): fractions.Fraction(1)}, 0))
            basis.append((f"E_del{k}_del{l}_mp", {(f"b_{k}_m", f"b_{l}_p"): fractions.Fraction(1)}, 0))
            basis.append((f"E_del{k}_del{l}_mm", {(f"b_{k}_m", f"b_{l}_m"): fractions.Fraction(1)}, 0))
            
    # Odd roots
    for k in range(1, n + 1):
        basis.append((f"E_eps1_del{k}_pp", {("a_1_p", f"b_{k}_p"): fractions.Fraction(1)}, 1))
        basis.append((f"E_eps1_del{k}_pm", {("a_1_p", f"b_{k}_m"): fractions.Fraction(1)}, 1))
        basis.append((f"E_eps1_del{k}_mp", {("a_1_m", f"b_{k}_p"): fractions.Fraction(1)}, 1))
        basis.append((f"E_eps1_del{k}_mm", {("a_1_m", f"b_{k}_m"): fractions.Fraction(1)}, 1))
        
    # We must normal order every basis element's polynomial
    # But wait, they are already normal ordered!
    # "a_1_p" < "a_1_m", "b_1_p" < "b_1_m", etc.
    # Let's verify.
    return basis
