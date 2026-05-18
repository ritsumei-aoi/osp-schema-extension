import json
import os
from fractions import Fraction
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict
from src.C_generators import OscillatorOperator, OscillatorWord, OscillatorExpression, normal_order, multiply_expressions, CGenerator

class DeformedExpression:
    def __init__(self):
        # Key: (tuple(operators), gb_label or None, has_kappa)
        self.terms: Dict[Tuple[Tuple[OscillatorOperator, ...], Optional[str], bool], Fraction] = {}

    def add_term(self, operators: Tuple[OscillatorOperator, ...], coeff: Any, gb_label: Optional[str] = None, has_kappa: bool = False):
        if coeff == 0: return
        key = (operators, gb_label, has_kappa)
        self.terms[key] = self.terms.get(key, Fraction(0)) + Fraction(coeff)
        if self.terms[key] == 0:
            del self.terms[key]

    def __repr__(self):
        if not self.terms: return "0"
        res = []
        for (ops, gb, kappa), c in self.terms.items():
            parts = [str(c)]
            if gb: parts.append(gb)
            if kappa: parts.append("kappa")
            parts.extend(repr(op) for op in ops)
            res.append(" * ".join(parts))
        return " + ".join(res)

def deformed_normal_order(expr: DeformedExpression) -> DeformedExpression:
    current = expr
    while True:
        new_expr = DeformedExpression()
        changed = False
        for (ops, gb, kappa), c in current.terms.items():
            ops_list = list(ops)
            word_changed = False
            for i in range(len(ops_list) - 1):
                op1, op2 = ops_list[i], ops_list[i+1]
                
                # Standard nilpotency
                if op1 == op2 and op1.is_fermion:
                    word_changed = True
                    changed = True
                    break

                if op1.sort_key() > op2.sort_key():
                    # Check for [b, a] deformation
                    # [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
                    is_b_a = (not op1.is_fermion and op2.is_fermion and op2.name == 'a' and op2.index == 1)
                    is_a_b = (op1.is_fermion and op1.name == 'a' and op1.index == 1 and not op2.is_fermion)

                    if is_b_a or is_a_b:
                        # 1. Swapped term
                        new_expr.add_term(tuple(ops_list[:i] + [op2, op1] + ops_list[i+2:]), c, gb, kappa)
                        
                        # 2. Deformation term
                        if not kappa and not gb:
                            if is_b_a: # b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma,j,s} * kappa
                                sigma = 'p' if op2.is_creation else 'm'
                                s = 'p' if op1.is_creation else 'm'
                                param = f"gb_a1{sigma}_b{op1.index}{s}"
                                new_expr.add_term(tuple(ops_list[:i] + ops_list[i+2:]), -c, param, True)
                            else: # a_1^sigma b_j^s = b_j^s a_1^sigma + gb_{sigma,j,s} * kappa
                                sigma = 'p' if op1.is_creation else 'm'
                                s = 'p' if op2.is_creation else 'm'
                                param = f"gb_a1{sigma}_b{op2.index}{s}"
                                new_expr.add_term(tuple(ops_list[:i] + ops_list[i+2:]), c, param, True)
                    
                    # Standard CAR/CCR
                    elif op1.name == op2.name and op1.index == op2.index and op1.is_creation != op2.is_creation:
                        if op1.is_fermion:
                            # a_m a_p = 1 - a_p a_m
                            new_expr.add_term(tuple(ops_list[:i] + ops_list[i+2:]), c, gb, kappa)
                            new_expr.add_term(tuple(ops_list[:i] + [op2, op1] + ops_list[i+2:]), -c, gb, kappa)
                        else:
                            # b_m b_p = 1 + b_p b_m
                            new_expr.add_term(tuple(ops_list[:i] + ops_list[i+2:]), c, gb, kappa)
                            new_expr.add_term(tuple(ops_list[:i] + [op2, op1] + ops_list[i+2:]), c, gb, kappa)
                    else:
                        sign = -1 if (op1.is_fermion and op2.is_fermion) else 1
                        new_expr.add_term(tuple(ops_list[:i] + [op2, op1] + ops_list[i+2:]), c * sign, gb, kappa)
                    
                    word_changed = True
                    changed = True
                    break
            
            if not word_changed:
                new_expr.add_term(tuple(ops_list), c, gb, kappa)
        
        current = new_expr
        if not changed: break
    return current

def compute_deformed_bracket(X_ops: Tuple[OscillatorOperator, ...], X_c: Fraction, Y_ops: Tuple[OscillatorOperator, ...], Y_c: Fraction, pX: int, pY: int) -> DeformedExpression:
    res = DeformedExpression()
    res.add_term(X_ops + Y_ops, X_c * Y_c)
    sign = -1 if (pX == 1 and pY == 1) else 1
    res.add_term(Y_ops + X_ops, -X_c * Y_c * sign)
    return deformed_normal_order(res)

class CGammaGenerator:
    def __init__(self, n: int):
        self.n = n
        self.gen_base = CGenerator(n)
        self.gb_params = []
        for sigma in ["p", "m"]:
            for j in range(1, n + 1):
                for s in ["p", "m"]:
                    self.gb_params.append(f"gb_a1{sigma}_b{j}{s}")
        
    def compute_gamma(self) -> List[Dict[str, Any]]:
        all_basis = self.gen_base.basis_odd + self.gen_base.basis_even
        parity = self.gen_base.to_json()['parity']
        gamma_map = defaultdict(Fraction)
        
        for i, name_x in enumerate(all_basis):
            for j, name_y in enumerate(all_basis):
                if i > j: continue
                
                expr_x = self.gen_base.generators[name_x]
                expr_y = self.gen_base.generators[name_y]
                
                full_gamma = DeformedExpression()
                
                for ops_x, c_x in expr_x.words.items():
                    for ops_y, c_y in expr_y.words.items():
                        bracket = compute_deformed_bracket(ops_x, c_x, ops_y, c_y, parity[name_x], parity[name_y])
                        for (ops, gb, kappa), c in bracket.terms.items():
                            if kappa and gb:
                                full_gamma.add_term(ops, c, gb, True)
                
                if not full_gamma.terms: continue
                
                for (ops, gb, kappa), c in full_gamma.terms.items():
                    temp_expr = OscillatorExpression()
                    temp_expr.add_word(OscillatorWord(list(ops), c))
                    
                    identities = self.gen_base.identify_expression(temp_expr)
                    for ident in identities:
                        key = (name_x, name_y, ident["Z"], gb)
                        gamma_map[key] += Fraction(ident["coeff"])

        gamma_entries = []
        for (nx, ny, nz, gb), coeff in gamma_map.items():
            if coeff != 0:
                gamma_entries.append({
                    "X": nx, "Y": ny, "Z": nz, "parameter": gb, "coeff": str(coeff)
                })
        return gamma_entries

    def generate_json(self):
        gamma_structure = self.compute_gamma()
        data = {
            "schema_version": "5.0",
            "algebra": {
                "family": "C", "n": self.n, "cartan_type": f"C({self.n+1})"
            },
            "inhomogeneous_deformation": {
                "parameters": self.gb_params,
                "exchange_relations": {
                    "description": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
                    "formula": "[b_j^s, a_1^sigma] = - gb_a1{sigma}_b{j}{s} * kappa"
                },
                "gamma_structure": gamma_structure
            },
            "metadata": {
                "generated_by": "C_gamma_generators.py",
                "generation_date": "2026-05-18",
                "sign_convention": "Option A: [b, a] = -gb * kappa"
            }
        }
        return data

if __name__ == "__main__":
    for n in [1, 2, 3]:
        gen = CGammaGenerator(n)
        data = gen.generate_json()
        os.makedirs("data", exist_ok=True)
        filename = f"data/C_{n}_gamma.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}")
