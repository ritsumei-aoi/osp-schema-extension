import json
from fractions import Fraction

with open('data/C_1_structure.json') as f:
    schema = json.load(f)

sc_dict = {}
for entry in schema['structure_constants']:
    key = (entry['X'], entry['Y'])
    if key not in sc_dict:
        sc_dict[key] = {}
    z = entry['Z']
    sc_dict[key][z] = sc_dict[key].get(z, Fraction(0)) + Fraction(entry['coeff'])

parity = schema['parity']

def bracket(X, Y):
    return dict(sc_dict.get((X, Y), {}))

X = 'E_eps1_del1_pp'
Y = 'E_eps1_del1_pp'
Z = 'E_eps1_del1_mm'

print('YZ=bracket(Y,Z):', bracket(Y, Z))
print('ZX=bracket(Z,X):', bracket(Z, X))
print('XY=bracket(X,Y):', bracket(X, Y))

px, py, pz = parity[X], parity[Y], parity[Z]
print(f'parity: X={px}, Y={py}, Z={pz}')

sign1 = (-1)**(px*pz)
sign2 = (-1)**(py*px)
sign3 = (-1)**(pz*py)
print(f'signs: {sign1},{sign2},{sign3}')

result = {}
yz = bracket(Y, Z)
zx = bracket(Z, X)
xy = bracket(X, Y)

print('\nTerm1: sign1*[X,[Y,Z]]')
for W, c in yz.items():
    xw = bracket(X, W)
    print(f'  [X,[{W}:{c}]] = {xw}')
    for V, d in xw.items():
        val = sign1*c*d
        result[V] = result.get(V, Fraction(0)) + val
        print(f'    {sign1}*{c}*{d}={val} -> {V}')

print('\nTerm2: sign2*[Y,[Z,X]]')
for W, c in zx.items():
    yw = bracket(Y, W)
    print(f'  [Y,[{W}:{c}]] = {yw}')
    for V, d in yw.items():
        val = sign2*c*d
        result[V] = result.get(V, Fraction(0)) + val
        print(f'    {sign2}*{c}*{d}={val} -> {V}')

print('\nTerm3: sign3*[Z,[X,Y]]')
for W, c in xy.items():
    zw = bracket(Z, W)
    print(f'  [Z,[{W}:{c}]] = {zw}')
    for V, d in zw.items():
        val = sign3*c*d
        result[V] = result.get(V, Fraction(0)) + val

result = {k: v for k, v in result.items() if v != 0}
print('\nJacobi residual:', result)

print('\n--- Checking key brackets ---')
print('[pp,H_1]:', bracket('E_eps1_del1_pp','H_1'))
print('[pp,H_2]:', bracket('E_eps1_del1_pp','H_2'))
print('[pp,mm]:', bracket('E_eps1_del1_pp','E_eps1_del1_mm'))
