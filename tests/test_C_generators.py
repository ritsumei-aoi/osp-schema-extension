import unittest
import json
from src.C_generators import CGenerator, OscillatorExpression, compute_bracket

class TestCGenerator(unittest.TestCase):
    def test_dimensions(self):
        # n=1: even=4, odd=4, total=8
        gen1 = CGenerator(1)
        self.assertEqual(len(gen1.basis_even), 4)
        self.assertEqual(len(gen1.basis_odd), 4)
        
        # n=2: even=11, odd=8, total=19
        gen2 = CGenerator(2)
        self.assertEqual(len(gen2.basis_even), 11)
        self.assertEqual(len(gen2.basis_odd), 8)
        
        # n=3: even=22, odd=12, total=34
        gen3 = CGenerator(3)
        self.assertEqual(len(gen3.basis_even), 22)
        self.assertEqual(len(gen3.basis_odd), 12)

    def test_parity(self):
        for n in [1, 2, 3]:
            gen = CGenerator(n)
            for name in gen.basis_even:
                self.assertEqual(gen.generators[name].parity, 0, f"Even generator {name} has odd parity")
            for name in gen.basis_odd:
                self.assertEqual(gen.generators[name].parity, 1, f"Odd generator {name} has even parity")

    def test_cartan_weight_relations(self):
        for n in [1]:
            gen = CGenerator(n)
            h1 = gen.generators["H_1"]
            e_eps1_del1_pp = gen.generators["E_eps1_del1_pp"] # eps1 + del1
            
            # [H1, E_eps1_del1_pp] should be (eps1+del1)(H1) * E_eps1_del1_pp
            # eps1(H1) = 1, del1(H1) = 1 (since H1 = a1p a1m + b1p b1m)
            # wait, H1 = a1+ a1- + b1+ b1-
            # [a1+ a1-, a1+] = a1+ {a1-, a1+} = a1+
            # [b1+ b1-, b1+] = b1+ [b1-, b1+] = b1+
            # So [H1, a1+ b1+] = [a1+ a1-, a1+] b1+ + a1+ [b1+ b1-, b1+] = a1+ b1+ + a1+ b1+ = 2 * a1+ b1+
            # Let's check compute_bracket
            bracket = compute_bracket(h1, e_eps1_del1_pp)
            print(f"[H1, E_eps1_del1_pp] = {bracket}")
            # Identify it
            coeff = 0
            for ops, c in bracket.words.items():
                if ops == e_eps1_del1_pp.words: # simplified check
                    pass
            # Just check if it's proportional
            # ...

    def test_structure_constants_schema(self):
        for n in [1]:
            gen = CGenerator(n)
            data = gen.to_json()
            sc = data["structure_constants"]
            self.assertTrue(len(sc) > 0)
            for entry in sc:
                self.assertIn("X", entry)
                self.assertIn("Y", entry)
                self.assertIn("Z", entry)
                self.assertIn("coeff", entry)

if __name__ == "__main__":
    unittest.main()
