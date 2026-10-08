import json
import pytest

def test_C_schema_generation():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json", "r") as f:
            schema = json.load(f)
            
        dim_even = 2*n**2 + n + 1
        dim_odd = 4*n
        
        assert schema["algebra"]["dimension"]["total"] == dim_even + dim_odd
        assert schema["algebra"]["dimension"]["even"] == dim_even
        assert schema["algebra"]["dimension"]["odd"] == dim_odd
        
        even_basis = schema["basis"]["even"]
        odd_basis = schema["basis"]["odd"]
        
        assert len(even_basis) == dim_even
        assert len(odd_basis) == dim_odd
        
        # Parity check
        for gen in even_basis:
            assert schema["parity"][gen] == 0
        for gen in odd_basis:
            assert schema["parity"][gen] == 1
            
        # Structure constants
        sc = schema["structure_constants"]
        assert len(sc) > 0
        
        # Verify closure (Z must be in basis + K)
        all_basis = set(even_basis + odd_basis + ["K"])
        for const in sc:
            assert const["X"] in all_basis
            assert const["Y"] in all_basis
            assert const["Z"] in all_basis
            
            # Graded parity check
            pX = schema["parity"].get(const["X"], 0)
            pY = schema["parity"].get(const["Y"], 0)
            pZ = schema["parity"].get(const["Z"], 0)
            
            assert (pX + pY) % 2 == pZ
