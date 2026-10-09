import json

for n in [1, 2, 3]:
    with open(f'data/C_{n}_coboundary.json') as f:
        cb = json.load(f)
    with open(f'data/C_{n}_structure.json') as f:
        s = json.load(f)
    basis_all = set(s['basis']['even'] + s['basis']['odd'])
    entries = cb['coboundary']['entries']
    errors = 0
    for entry in entries:
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
        # (delta_f)(X,Y) has parity p(X)+p(Y)+p(f)=p(X)+p(Y)+1 since f is odd
        if (px + py + 1) % 2 != pz % 2:
            print(f'n={n}: parity violation ({X},{Y})->{Z}: expected pz={(px+py+1)%2}, got {pz}')
            errors += 1
    if errors == 0:
        print(f'n={n}: {len(entries)} coboundary entries all consistent')
    else:
        print(f'n={n}: {errors} errors')
