import sympy as sp
from sympy import symbols, Matrix, zeros, Eq, solve
from itertools import product, combinations_with_replacement

def get_basis(n):
    # Basis for C(n+1)
    # Even: a1+ a1-, bk+ bl+ (k<=l), bk- bl- (k<=l), bk+ bl- (all k,l)
    # Odd: a1+ bk+, a1+ bk-, a1- bk+, a1- bk-
    basis = []
    labels = []
    
    # Even
    labels.append(('E', 'a+', 'a-'))
    
    for k in range(1, n+1):
        for l in range(k, n+1):
            labels.append(('E', f'b+{k}', f'b+{l}'))
            labels.append(('E', f'b-{k}', f'b-{l}'))
    
    for k in range(1, n+1):
        for l in range(1, n+1):
            labels.append(('E', f'b+{k}', f'b-{l}'))
            
    # Odd
    for k in range(1, n+1):
        labels.append(('O', 'a+', f'b+{k}'))
        labels.append(('O', 'a+', f'b-{k}'))
        labels.append(('O', 'a-', f'b+{k}'))
        labels.append(('O', 'a-', f'b-{k}'))
        
    return labels

def print_basis(n):
    labels = get_basis(n)
    print(f"n={n}, dim={len(labels)}")
    print("Even:", len([l for l in labels if l[0]=='E']))
    print("Odd:", len([l for l in labels if l[0]=='O']))

if __name__ == '__main__':
    print_basis(1)
    print_basis(2)
