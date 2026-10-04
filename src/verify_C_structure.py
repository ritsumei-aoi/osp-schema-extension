import json
from fractions import Fraction
from typing import Dict, Tuple, List

class StructureConstantVerifier:
    def __init__(self, json_path: str):
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        self.n = self.data["algebra"]["n"]
        self.basis_even = self.data["basis"]["even"]
        self.basis_odd = self.data["basis"]["odd"]
        self.basis = self.basis_odd + self.basis_even
        self.parity = self.data["parity"]
        
        # Build bracket map: (X, Y) -> Dict[Z, Fraction]
        self.bracket_map: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
        for sc in self.data["structure_constants"]:
            x, y, z = sc["X"], sc["Y"], sc["Z"]
            coeff = Fraction(sc["coeff"])
            if (x, y) not in self.bracket_map:
                self.bracket_map[(x, y)] = {}
            self.bracket_map[(x, y)][z] = self.bracket_map[(x, y)].get(z, Fraction(0)) + coeff

    def get_bracket(self, x: str, y: str) -> Dict[str, Fraction]:
        return self.bracket_map.get((x, y), {})

    def evaluate_nested_bracket(self, x: str, y: str, z: str) -> Dict[str, Fraction]:
        r"""
        Computes [X, [Y, Z]] = sum_W coeff(Y,Z,W) [X, W]
        """
        inner = self.get_bracket(y, z)
        res = {}
        for w, c_w in inner.items():
            xw = self.get_bracket(x, w)
            for u, c_u in xw.items():
                res[u] = res.get(u, Fraction(0)) + c_w * c_u
                if res[u] == 0:
                    del res[u]
        return res

    def check_antisymmetry(self) -> Tuple[bool, List[str]]:
        errors = []
        for x in self.basis:
            px = self.parity[x]
            for y in self.basis:
                py = self.parity[y]
                # [X, Y\} = - (-1)^{px py} [Y, X\}
                xy = self.get_bracket(x, y)
                yx = self.get_bracket(y, x)
                expected_sign = -1 if (px == 1 and py == 1) else -1  # Wait!
                # Super-anti-symmetry: [Y, X\} = - (-1)^{px py} [X, Y\}
                # So [X, Y\} + (-1)^{px py} [Y, X\} = 0
                sign = -1 if (px == 1 and py == 1) else 1
                
                # Check for each basis element z if xy[z] + sign * yx[z] == 0
                all_z = set(xy.keys()).union(yx.keys())
                for z in all_z:
                    val_xy = xy.get(z, Fraction(0))
                    val_yx = yx.get(z, Fraction(0))
                    if val_xy + sign * val_yx != 0:
                        errors.append(f"Anti-symmetry failed for pair ({x}, {y}) on element {z}: {val_xy} + ({sign})*{val_yx} != 0")
        return len(errors) == 0, errors

    def check_super_jacobi(self) -> Tuple[bool, List[str]]:
        errors = []
        num_basis = len(self.basis)
        for i in range(num_basis):
            x = self.basis[i]
            px = self.parity[x]
            for j in range(i, num_basis):
                y = self.basis[j]
                py = self.parity[y]
                for k in range(j, num_basis):
                    z = self.basis[k]
                    pz = self.parity[z]

                    # Term 1: (-1)^{px pz} [X, [Y, Z\} \}
                    s1 = -1 if (px == 1 and pz == 1) else 1
                    t1 = self.evaluate_nested_bracket(x, y, z)

                    # Term 2: (-1)^{py px} [Y, [Z, X\} \}
                    s2 = -1 if (py == 1 and px == 1) else 1
                    t2 = self.evaluate_nested_bracket(y, z, x)

                    # Term 3: (-1)^{pz py} [Z, [X, Y\} \}
                    s3 = -1 if (pz == 1 and py == 1) else 1
                    t3 = self.evaluate_nested_bracket(z, x, y)

                    # Sum: s1 * t1 + s2 * t2 + s3 * t3
                    all_w = set(t1.keys()).union(t2.keys()).union(t3.keys())
                    for w in all_w:
                        v1 = t1.get(w, Fraction(0)) * s1
                        v2 = t2.get(w, Fraction(0)) * s2
                        v3 = t3.get(w, Fraction(0)) * s3
                        if v1 + v2 + v3 != 0:
                            errors.append(f"Super-Jacobi failed for triple ({x}, {y}, {z}) on element {w}: {v1} + {v2} + {v3} != 0")
        return len(errors) == 0, errors

    def verify_all(self) -> Dict[str, Any]:
        anti_pass, anti_errs = self.check_antisymmetry()
        jacobi_pass, jacobi_errs = self.check_super_jacobi()
        return {
            "n": self.n,
            "total_dimension": len(self.basis),
            "antisymmetry_pass": anti_pass,
            "antisymmetry_errors": anti_errs,
            "super_jacobi_pass": jacobi_pass,
            "super_jacobi_errors": jacobi_errs,
            "overall_pass": anti_pass and jacobi_pass
        }

if __name__ == "__main__":
    for n in [1, 2, 3]:
        verifier = StructureConstantVerifier(f"data/C_{n}_structure.json")
        res = verifier.verify_all()
        print(f"C({n+1}) Verification (dim {res['total_dimension']}):")
        print(f"  Anti-symmetry: {'PASS' if res['antisymmetry_pass'] else 'FAIL'}")
        print(f"  Super-Jacobi : {'PASS' if res['super_jacobi_pass'] else 'FAIL'}")
        if not res["overall_pass"]:
            print("  Errors:", res["antisymmetry_errors"] + res["super_jacobi_errors"])
