import json

for n in [1, 2, 3]:
    with open(f'data/C_{n}_gamma.json') as f:
        g = json.load(f)
    with open(f'data/C_{n}_structure.json') as f:
        s = json.load(f)
    basis_all = set(s['basis']['even'] + s['basis']['odd'])
    gc = g['inhomogeneous_deformation']['gamma_coefficients']
    errors = 0
    for entry in gc:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        if X not in basis_all:
            print(f'n={n}: X={X} not in basis'); errors += 1
        if Y not in basis_all:
            print(f'n={n}: Y={Y} not in basis'); errors += 1
        if Z not in basis_all:
            print(f'n={n}: Z={Z} not in basis'); errors += 1
        px = s['parity'].get(X, -1)
        py = s['parity'].get(Y, -1)
        pz = s['parity'].get(Z, -1)
        if (px + py) % 2 != 1:
            print(f'n={n}: gamma({X},{Y}): parity sum {px+py} should be odd'); errors += 1
        if pz != 0:
            print(f'n={n}: gamma target {Z} parity={pz} should be even'); errors += 1
    if errors == 0:
        print(f'n={n}: {len(gc)} gamma entries all consistent')
    else:
        print(f'n={n}: {errors} errors')
