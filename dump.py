import json

def dump_data(n):
    even_basis = [("A",)]
    for j in range(1, n+1):
        for k in range(j, n+1):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    if j == k and s1 < s2: continue
                    even_basis.append(("B", j, s1, k, s2))
                    
    odd_basis = []
    for sigma in [1, -1]:
        for j in range(1, n+1):
            for s in [1, -1]:
                odd_basis.append(("O", sigma, j, s))
                
    basis = even_basis + odd_basis
    
    with open("docs/math/structure_constants.json", "w") as f:
        json.dump({"basis": basis}, f)
        
if __name__ == "__main__":
    dump_data(1)
