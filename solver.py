import sympy as sp
import itertools

class Term:
    def __init__(self, coeff, kappa_power, ops):
        self.coeff = coeff
        self.kappa_power = kappa_power
        self.ops = tuple(ops)
    
    def __repr__(self):
        return f"{self.coeff} * k^{self.kappa_power} * {self.ops}"

def order_val(op):
    if op == 'a+': return 1
    if op == 'a-': return 2
    if op.startswith('b'):
        idx = int(op[1:-1])
        sign = 1 if op[-1] == '+' else 2
        return 10 + idx * 10 + sign
    return 1000

def M(sig1, sig2):
    if sig1 == 'a+' and sig2 == 'a-': return 1
    if sig1 == 'a-' and sig2 == 'a+': return 1
    return 0

def J(op1, op2):
    idx1 = int(op1[1:-1]); s1 = 1 if op1[-1]=='+' else -1
    idx2 = int(op2[1:-1]); s2 = 1 if op2[-1]=='+' else -1
    if idx1 == idx2 and s1 == -s2:
        return s2
    return 0

def normal_order_term(coeff, kappa_power, ops):
    terms = [Term(coeff, kappa_power, ops)]
    ordered_terms = []
    
    while terms:
        t = terms.pop(0)
        c = t.coeff
        k = t.kappa_power
        o = list(t.ops)
        
        swapped = False
        for i in range(len(o) - 1):
            if order_val(o[i]) > order_val(o[i+1]):
                op1 = o[i]
                op2 = o[i+1]
                
                if op1.startswith('b') and op2.startswith('b'):
                    new_o = o[:]
                    new_o[i] = op2; new_o[i+1] = op1
                    terms.append(Term(c, k, new_o))
                    val = J(op1, op2)
                    if val != 0:
                        new_o_scalar = o[:i] + o[i+2:]
                        terms.append(Term(c * val, k, new_o_scalar))
                    swapped = True; break
                    
                elif op1.startswith('a') and op2.startswith('a'):
                    new_o = o[:]
                    new_o[i] = op2; new_o[i+1] = op1
                    terms.append(Term(-c, k, new_o))
                    val = M(op1, op2)
                    if val != 0:
                        new_o_scalar = o[:i] + o[i+2:]
                        terms.append(Term(c * val, k, new_o_scalar))
                    swapped = True; break
                    
                elif op1.startswith('b') and op2.startswith('a'):
                    new_o = o[:]
                    new_o[i] = op2; new_o[i+1] = op1
                    terms.append(Term(c, k, new_o))
                    gb_sym = sp.Symbol(f"gb_{op2}_{op1}")
                    a_count = sum(1 for x in o[:i] if x.startswith('a'))
                    kappa_sign = (-1)**a_count
                    new_o_gb = o[:i] + o[i+2:]
                    terms.append(Term(c * (-gb_sym) * kappa_sign, k + 1, new_o_gb))
                    swapped = True; break
        if not swapped:
            ordered_terms.append(t)
            
    agg = {}
    for t in ordered_terms:
        if t.coeff == 0: continue
        key = (t.kappa_power, t.ops)
        if key not in agg: agg[key] = 0
        agg[key] += t.coeff
        
    res = []
    for k, v in agg.items():
        if sp.simplify(v) != 0:
            res.append(Term(sp.simplify(v), k[0], k[1]))
    return res

def normal_order_expr(expr):
    res = []
    for t in expr:
        res.extend(normal_order_term(t.coeff, t.kappa_power, t.ops))
    
    agg = {}
    for t in res:
        key = (t.kappa_power, t.ops)
        if key not in agg: agg[key] = 0
        agg[key] += t.coeff
    return [Term(sp.simplify(v), k[0], k[1]) for k,v in agg.items() if sp.simplify(v) != 0]

def add_expr(expr1, expr2):
    return normal_order_expr(expr1 + expr2)

def mul_expr(expr1, expr2):
    res = []
    for t1 in expr1:
        for t2 in expr2:
            a_count_1 = sum(1 for x in t1.ops if x.startswith('a'))
            # kappa from t2 moving past a from t1
            # kappa is odd, so each 'a' gives a minus sign
            sign = (-1)**(a_count_1 * t2.kappa_power)
            new_ops = t1.ops + t2.ops
            res.append(Term(t1.coeff * t2.coeff * sign, t1.kappa_power + t2.kappa_power, new_ops))
    return normal_order_expr(res)

def get_generators(n):
    gens = {}
    
    # H_1
    gens['H1'] = [Term(1, 0, ('a+', 'a-')), Term(1, 0, ('b1+', 'b1-'))]
    
    # H_k (2 <= k <= n)
    for k in range(2, n+1):
        gens[f'H{k}'] = [Term(1, 0, (f'b{k-1}+', f'b{k-1}-')), Term(-1, 0, (f'b{k}+', f'b{k}-'))]
        
    # H_{n+1}
    gens[f'H{n+1}'] = [Term(-1, 0, (f'b{n}+', f'b{n}-')), Term(-sp.Rational(1,2), 0, ())]
    
    # E_{\pm 2\delta_k}
    for k in range(1, n+1):
        gens[f'E_2d{k}'] = [Term(sp.Rational(1,2), 0, (f'b{k}+', f'b{k}+'))]
        gens[f'E_-2d{k}'] = [Term(sp.Rational(1,2), 0, (f'b{k}-', f'b{k}-'))]
        
    # E_{\pm\delta_k \pm\delta_l} for k < l
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            gens[f'E_d{k}_d{l}'] = [Term(1, 0, (f'b{k}+', f'b{l}+'))]
            gens[f'E_d{k}_-d{l}'] = [Term(1, 0, (f'b{k}+', f'b{l}-'))]
            gens[f'E_-d{k}_d{l}'] = [Term(1, 0, (f'b{k}-', f'b{l}+'))]
            gens[f'E_-d{k}_-d{l}'] = [Term(1, 0, (f'b{k}-', f'b{l}-'))]
            
    # Odd generators
    for k in range(1, n+1):
        gens[f'E_e_d{k}'] = [Term(1, 0, ('a+', f'b{k}+'))]
        gens[f'E_e_-d{k}'] = [Term(1, 0, ('a+', f'b{k}-'))]
        gens[f'E_-e_d{k}'] = [Term(1, 0, ('a-', f'b{k}+'))]
        gens[f'E_-e_-d{k}'] = [Term(1, 0, ('a-', f'b{k}-'))]
        
    # Normal order all generators
    for k, v in gens.items():
        gens[k] = normal_order_expr(v)
        
    return gens

def get_parity(gen_name):
    if 'e' in gen_name: return 1
    return 0

def bracket(expr1, expr2, p1, p2):
    term1 = mul_expr(expr1, expr2)
    term2 = mul_expr(expr2, expr1)
    sign = -1 if (p1 * p2) % 2 == 0 else 1
    # X*Y - (-1)^{p1 p2} Y*X
    # So sign is -(-1)^{p1 p2}
    for t in term2:
        t.coeff *= sign
    return add_expr(term1, term2)

def main():
    n = 1
    gens = get_generators(n)
    
    # We want to compute gamma(X, Y)
    # gamma(X, Y) is the coefficient of kappa in [X, Y]_gamma
    # We can extract all terms with kappa_power = 1.
    
    print("Testing bracket of E_e_d1 and E_-e_-d1")
    X = gens['E_e_d1']
    Y = gens['E_-e_-d1']
    b = bracket(X, Y, 1, 1)
    for t in b:
        if t.kappa_power > 0:
            print(t)

if __name__ == "__main__":
    main()
