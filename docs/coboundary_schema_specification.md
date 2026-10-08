# C(n+1) Schema 4: Coboundary Structure

Schema 4 files are named `C_{n}_coboundary.json` and refer to
`C_{n}_structure.json`.

`odd_linear_map.parameters` contains one independent symbol
`phi_{target}_from_{source}` for every ordered pair of basis generators of
opposite parity. The map is
\(f(\text{source})=\sum_{\text{target}}\phi_{\text{target from source}}
\text{target}\); it is zero on same-parity target/source pairs.

Each sparse `coboundary.coefficients` row gives the coefficient of a basis
generator `Z` in \((\delta f)(X,Y)\), as a linear combination of `phi`
parameters. Coefficients are exact rational strings. Only one nonzero row is
stored per `(X,Y,Z)`, with `(X,Y)` in Schema 1 basis order. The formula is
\[
(\delta f)(X,Y)=(-1)^{p(X)}[X,f(Y)]
-(-1)^{(p(X)+1)p(Y)}[Y,f(X)]-f([X,Y]).
\]
