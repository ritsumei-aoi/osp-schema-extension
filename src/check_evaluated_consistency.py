import json

for n in [1, 2, 3]:
    with open(f'data/C_{n}_evaluated.json') as f:
        ev = json.load(f)
    with open(f'data/C_{n}_structure.json') as f:
        s = json.load(f)
    basis_all = set(s['basis']['even'] + s['basis']['odd'])
    gc = ev['evaluated_gamma']['gamma_coefficients']
    errors = 0
    for entry in gc:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        if X not in basis_all:
            print(f'n={n}: X={X} not in basis'); errors += 1
        if Y not in basis_all:
            print(f'n={n}: Y={Y} not in basis'); errors += 1
        if Z not in basis_all:
            print(f'n={n}: Z={Z} not in basis'); errors += 1
        if entry['gamma_coeff'] == '0':
            print(f'n={n}: zero gamma entry for ({X},{Y},{Z})'); errors += 1
    if errors == 0:
        print(f'n={n}: {len(gc)} evaluated entries all consistent (gb=+1)')
    else:
        print(f'n={n}: {errors} errors')
