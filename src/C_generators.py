import json
import os
from fractions import Fraction
from typing import List, Dict, Tuple, Any, Optional

class OscillatorOperator:
    def __init__(self, name: str, index: int, is_creation: bool, is_fermion: bool):
        self.name = name
        self.index = index
        self.is_creation = is_creation
        self.is_fermion = is_fermion
        self.label = f"{name}_{index}_{'p' if is_creation else 'm'}"

    def __repr__(self):
        return self.label

    def __eq__(self, other):
        if not isinstance(other, OscillatorOperator):
            return False
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def sort_key(self):
        # Creation operators before annihilation operators
        # a before b
        # Lower index before higher index
        return (not self.is_creation, self.name, self.index)

class OscillatorWord:
    def __init__(self, operators: List[OscillatorOperator], coeff: Any = 1):
        self.operators = tuple(operators)
        self.coeff = Fraction(coeff)

    def __repr__(self):
        if not self.operators:
            return str(self.coeff)
        return f"{self.coeff} * {' '.join(repr(op) for op in self.operators)}"

    @property
    def parity(self) -> int:
        return sum(1 for op in self.operators if op.is_fermion) % 2

    def __eq__(self, other):
        if not isinstance(other, OscillatorWord):
            return False
        return self.operators == other.operators and self.coeff == other.coeff

    def __hash__(self):
        return hash((self.operators, self.coeff))

class OscillatorExpression:
    def __init__(self, words: List[OscillatorWord] = None):
        self.words: Dict[Tuple[OscillatorOperator, ...], Fraction] = {}
        if words:
            for w in words:
                self.add_word(w)

    def add_word(self, word: OscillatorWord):
        if word.coeff == 0:
            return
        self.words[word.operators] = self.words.get(word.operators, Fraction(0)) + word.coeff
        if self.words[word.operators] == 0:
            del self.words[word.operators]

    def __repr__(self):
        if not self.words:
            return "0"
        return " + ".join(f"{c} * {' '.join(repr(op) for op in ops)}" if ops else str(c)
                          for ops, c in self.words.items())

    @property
    def parity(self) -> int:
        p = None
        for ops in self.words:
            word_parity = sum(1 for op in ops if op.is_fermion) % 2
            if p is None:
                p = word_parity
            elif p != word_parity:
                raise ValueError("Mixed parity expression")
        return p if p is not None else 0

def multiply_expressions(e1: OscillatorExpression, e2: OscillatorExpression) -> OscillatorExpression:
    result = OscillatorExpression()
    for ops1, c1 in e1.words.items():
        for ops2, c2 in e2.words.items():
            result.add_word(OscillatorWord(list(ops1) + list(ops2), c1 * c2))
    return result

def normal_order(expr: OscillatorExpression) -> OscillatorExpression:
    current_expr = expr
    while True:
        new_expr = OscillatorExpression()
        changed = False
        for ops, c in current_expr.words.items():
            ops_list = list(ops)
            word_changed = False
            for i in range(len(ops_list) - 1):
                op1 = ops_list[i]
                op2 = ops_list[i + 1]
                
                if op1 == op2 and op1.is_fermion:
                    # a_p a_p = 0
                    word_changed = True
                    changed = True
                    # This word becomes 0, so we don't add it to new_expr
                    break

                # We want Creation < Annihilation
                # If they are out of order, swap them
                if op1.sort_key() > op2.sort_key():
                    # Check if they are the same oscillator
                    if op1.name == op2.name and op1.index == op2.index and op1.is_creation != op2.is_creation:
                        # Case a_m a_p or b_m b_p
                        if op1.is_fermion:
                            # a_m a_p = 1 - a_p a_m
                            term1 = OscillatorWord(ops_list[:i] + ops_list[i+2:], c)
                            new_expr.add_word(term1)
                            term2_ops = ops_list[:i] + [op2, op1] + ops_list[i+2:]
                            new_expr.add_word(OscillatorWord(term2_ops, -c))
                        else:
                            # b_m b_p = 1 + b_p b_m
                            term1 = OscillatorWord(ops_list[:i] + ops_list[i+2:], c)
                            new_expr.add_word(term1)
                            term2_ops = ops_list[:i] + [op2, op1] + ops_list[i+2:]
                            new_expr.add_word(OscillatorWord(term2_ops, c))
                    else:
                        # Different oscillators or same type (p p or m m)
                        sign = -1 if (op1.is_fermion and op2.is_fermion) else 1
                        term_ops = ops_list[:i] + [op2, op1] + ops_list[i+2:]
                        new_expr.add_word(OscillatorWord(term_ops, c * sign))
                    
                    word_changed = True
                    changed = True
                    break
            
            if not word_changed:
                new_expr.add_word(OscillatorWord(ops_list, c))
        
        current_expr = new_expr
        if not changed:
            break
    return current_expr

def compute_bracket(e1: OscillatorExpression, e2: OscillatorExpression) -> OscillatorExpression:
    p1 = e1.parity
    p2 = e2.parity
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    
    # [X, Y} = XY - (-1)^(p1*p2) YX
    term1 = multiply_expressions(e1, e2)
    term2 = multiply_expressions(e2, e1)
    
    result = OscillatorExpression()
    for ops, c in term1.words.items():
        result.add_word(OscillatorWord(list(ops), c))
    for ops, c in term2.words.items():
        result.add_word(OscillatorWord(list(ops), -c * sign))
        
    return normal_order(result)

class CGenerator:
    def __init__(self, n: int):
        self.n = n
        self.fermions = [
            OscillatorOperator("a", 1, True, True),
            OscillatorOperator("a", 1, False, True)
        ]
        self.bosons = []
        for i in range(1, n + 1):
            self.bosons.append(OscillatorOperator("b", i, True, False))
            self.bosons.append(OscillatorOperator("b", i, False, False))
            
        self.generators: Dict[str, OscillatorExpression] = {}
        self.basis_even: List[str] = []
        self.basis_odd: List[str] = []
        self._build_basis()

    def _get_op(self, name: str, index: int, p_or_m: str) -> OscillatorOperator:
        is_creation = (p_or_m == "p")
        is_fermion = (name == "a")
        return OscillatorOperator(name, index, is_creation, is_fermion)

    def _build_basis(self):
        # 1. Odd Roots
        a1p = self._get_op("a", 1, "p")
        a1m = self._get_op("a", 1, "m")
        
        self.basis_odd = []
        for eps_sign in ["p", "m"]:
            a_op = a1p if eps_sign == "p" else a1m
            for del_sign in ["p", "m"]:
                for k in range(1, self.n + 1):
                    label = f"E_eps1_del{k}_{eps_sign}{del_sign}"
                    b_op = self._get_op("b", k, del_sign)
                    self.generators[label] = normal_order(OscillatorExpression([OscillatorWord([a_op, b_op])]))
                    self.basis_odd.append(label)

        # 2. Even Cartan
        self.basis_even = []
        for k in range(1, self.n + 2):
            label = f"H_{k}"
            if k == 1:
                expr = OscillatorExpression([
                    OscillatorWord([self._get_op("a", 1, "p"), self._get_op("a", 1, "m")]),
                    OscillatorWord([self._get_op("b", 1, "p"), self._get_op("b", 1, "m")])
                ])
            elif k <= self.n:
                expr = OscillatorExpression([
                    OscillatorWord([self._get_op("b", k-1, "p"), self._get_op("b", k-1, "m")]),
                    OscillatorWord([self._get_op("b", k, "p"), self._get_op("b", k, "m")], -1)
                ])
            else:
                expr = OscillatorExpression([
                    OscillatorWord([self._get_op("b", self.n, "p"), self._get_op("b", self.n, "m")], -1),
                    OscillatorWord([], Fraction(-1, 2))
                ])
            self.generators[label] = normal_order(expr)
            self.basis_even.append(label)

        # 3. Even Roots
        even_roots_pos = []
        even_roots_neg = []
        even_roots_mixed = []

        for k in range(1, self.n + 1):
            p_label = f"E_2del{k}_p"
            m_label = f"E_2del{k}_m"
            self.generators[p_label] = normal_order(OscillatorExpression([OscillatorWord([self._get_op("b", k, "p"), self._get_op("b", k, "p")])]))
            self.generators[m_label] = normal_order(OscillatorExpression([OscillatorWord([self._get_op("b", k, "m"), self._get_op("b", k, "m")])]))
            even_roots_pos.append(p_label)
            even_roots_neg.append(m_label)

        for i in range(1, self.n):
            for j in range(i + 1, self.n + 1):
                labels = [f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_mm", f"E_del{i}_del{j}_pm", f"E_del{i}_del{j}_mp"]
                ops = [
                    ([self._get_op("b", i, "p"), self._get_op("b", j, "p")]),
                    ([self._get_op("b", i, "m"), self._get_op("b", j, "m")]),
                    ([self._get_op("b", i, "p"), self._get_op("b", j, "m")]),
                    ([self._get_op("b", i, "m"), self._get_op("b", j, "p")])
                ]
                for label, op_list in zip(labels, ops):
                    self.generators[label] = normal_order(OscillatorExpression([OscillatorWord(op_list)]))
                    if "pp" in label: even_roots_pos.append(label)
                    elif "mm" in label: even_roots_neg.append(label)
                    else: even_roots_mixed.append(label)

        even_roots_pos.sort()
        even_roots_neg.sort()
        even_roots_mixed.sort()
        self.basis_even.extend(even_roots_pos)
        self.basis_even.extend(even_roots_neg)
        self.basis_even.extend(even_roots_mixed)

    def identify_expression(self, expr: OscillatorExpression) -> List[Dict[str, Any]]:
        remaining = OscillatorExpression()
        for ops, c in expr.words.items():
            remaining.add_word(OscillatorWord(list(ops), c))
            
        results = []
        
        # 1. Identify root generators (single words)
        root_generators = {k: v for k, v in self.generators.items() if "H_" not in k}
        # Sort to match longer words first? No, generators are all quadratic.
        for name, gen_expr in root_generators.items():
            gen_words = list(gen_expr.words.keys())
            if not gen_words: continue
            ref_word = gen_words[0]
            if ref_word in remaining.words:
                coeff = remaining.words[ref_word] / gen_expr.words[ref_word]
                results.append({"Z": name, "coeff": str(coeff)})
                for ops, c in gen_expr.words.items():
                    remaining.add_word(OscillatorWord(list(ops), -c * coeff))
        
        if not remaining.words:
            return results

        # 2. Identify Cartan generators and K
        diag_words = [tuple()]
        diag_words.append((self._get_op("a", 1, "p"), self._get_op("a", 1, "m")))
        for i in range(1, self.n + 1):
            diag_words.append((self._get_op("b", i, "p"), self._get_op("b", i, "m")))
            
        target = [remaining.words.get(w, Fraction(0)) for w in diag_words]
        
        # Solving for H_1, ..., H_{n+1}, K
        # H_1 = N_a1 + N_b1
        # H_2 = N_b1 - N_b2
        # ...
        # H_n = N_b{n-1} - N_bn
        # H_{n+1} = -N_bn - 1/2
        
        h_coeffs = [Fraction(0)] * (self.n + 2)
        # coeff(H_1) = target(N_a1)
        if len(target) > 1:
            h_coeffs[1] = target[1]
            # target(N_b1) = coeff(H_1) + coeff(H_2) => coeff(H_2) = target(N_b1) - coeff(H_1)
            if self.n >= 1:
                if len(target) > 2:
                    h_coeffs[2] = target[2] - h_coeffs[1]
                    for k in range(2, self.n):
                        # target(N_bk) = -coeff(H_k) + coeff(H_{k+1})
                        h_coeffs[k+1] = target[k+1] + h_coeffs[k]
                    # H_{n+1} has -N_bn
                    # target(N_bn) = -coeff(H_n) - coeff(H_{n+1}) => coeff(H_{n+1}) = -target(N_bn) - coeff(H_n)
                    # wait, let's re-verify H_{n+1}
                    # H_{n+1} = -b_np b_nm - 1/2
                    # so target(N_bn) = -coeff(H_n) - coeff(H_{n+1}) if n > 1
                    # if n=1: H_1 = N_a1 + N_b1, H_2 = -N_b1 - 1/2.
                    # target(N_b1) = coeff(H_1) - coeff(H_2) => coeff(H_2) = coeff(H_1) - target(N_b1)
                    if self.n == 1:
                        h_coeffs[2] = h_coeffs[1] - target[2]
                    else:
                        h_coeffs[self.n + 1] = h_coeffs[self.n] - target[self.n + 1]
            
            for i in range(1, self.n + 2):
                if h_coeffs[i] != 0:
                    results.append({"Z": f"H_{i}", "coeff": str(h_coeffs[i])})
                    gen_expr = self.generators[f"H_{i}"]
                    for w, c in gen_expr.words.items():
                        if w == tuple():
                            target[0] -= c * h_coeffs[i]
        
        if target[0] != 0:
            results.append({"Z": "K", "coeff": str(target[0])})
            
        return results

    def compute_all_structure_constants(self) -> List[Dict[str, Any]]:
        all_basis = self.basis_odd + self.basis_even
        results = []
        for i, name_x in enumerate(all_basis):
            for j, name_y in enumerate(all_basis):
                if i > j: continue
                expr_x, expr_y = self.generators[name_x], self.generators[name_y]
                expr_z = compute_bracket(expr_x, expr_y)
                if not expr_z.words: continue
                identities = self.identify_expression(expr_z)
                if not identities:
                    print(f"Warning: Bracket [{name_x}, {name_y}] = {expr_z} not identified")
                    continue
                for ident in identities:
                    results.append({"X": name_x, "Y": name_y, "Z": ident["Z"], "coeff": ident["coeff"], "sign_rule": "graded"})
        return results

    def to_json(self) -> Dict[str, Any]:
        data = {
            "schema_version": "5.0",
            "algebra": {
                "family": "C", "m": 1, "n": self.n, "cartan_type": f"C({self.n+1})",
                "alternative_notation": {"osp": f"osp(2|{2*self.n})", "dimension_formula": "osp(2m|2n) with m=1"},
                "dimension": {"total": 2*self.n**2 + 5*self.n + 1, "even": 2*self.n**2 + self.n + 1, "odd": 4*self.n}
            },
            "oscillator_generators": {
                "fermions": {"count": 2, "m": 1, "labels": ["a_1_p", "a_1_m"], "description": "Standard fermionic oscillators a_i^± with i=1,...,m (m=1 for C(n+1))"},
                "bosons": {"count": 2 * self.n, "n": self.n, "labels": [f"b_{i}_{s}" for i in range(1, self.n + 1) for s in ["p", "m"]], "description": "Bosonic oscillators b_i^± with i=1,...,n"}
            },
            "oscillator_relations": {
                "fermionic_anticommutators": {"description": "Canonical anticommutation relations for fermionic oscillators", "relations": {"same_type": "{a_i^±, a_j^±} = 0 for all i, j", "conjugate_pair": "{a_i^-, a_j^+} = δ_{ij}"}},
                "bosonic_commutators": {"description": "Canonical commutation relations for bosonic oscillators", "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
                "mixed_relations": {"boson_fermion": "[b_i^±, a_j^±] = 0"}
            },
            "central_elements": {
                "kappa": {"label": "kappa", "parity": 1, "description": "Nilpotent central element (kappa^2 = 0)"},
                "K": {"label": "K", "parity": 0, "description": "Central identity element (scalar 1)"}
            },
            "basis": {"even": self.basis_even, "odd": self.basis_odd, "ordering_convention": "PBW: κ < [odd] < [even]"},
            "parity": {name: (1 if name in self.basis_odd else 0) for name in self.basis_odd + self.basis_even},
            "generator_realization": {
                "description": "Standard form with PBW ordering",
                "ordering": "a_1_p, a_1_m, " + ", ".join(f"b_{i}_p, b_{i}_m" for i in range(1, self.n + 1)),
                "realizations": {name: {"standard_form": [{"words": [op.label for op in ops], "coeff": str(c)} for ops, c in expr.words.items()], "parity": expr.parity} for name, expr in self.generators.items()}
            },
            "structure_constants": self.compute_all_structure_constants(),
            "metadata": {"generated_by": "C_generators.py", "generation_date": "2026-05-18", "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"]}
        }
        return data

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        gen = CGenerator(n)
        data = gen.to_json()
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated data/C_{n}_structure.json")
