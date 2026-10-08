# C(n+1) Schema 2: Gamma Structure

Schema 2 files are named `C_{n}_gamma.json` and refer to the corresponding
`C_{n}_structure.json` file.

## Parameter matrix

`gb_matrix` is a \(2\times2n\) matrix. Its rows are `a_1_p`, `a_1_m`; its
columns are `b_1_p`, `b_1_m`, through `b_n_p`, `b_n_m`. Each entry is a
distinct parameter label `gb_a1_{p|m}_b{k}_{p|m}`. `parameter_parity` records
the parity assigned to the parameters in
`docs/math/C_inhomogeneous_definition.md`.

## Deformation and gamma coefficients

The `inhomogeneous_deformation` object records the central symbol, source
exchange relation, bracket formula, coefficient convention, and sparse
nonzero gamma coefficients. Each coefficient row is:

```json
{
  "X": "H_1",
  "Y": "E_eps1_del1_pp",
  "Z": "H_1",
  "terms": [
    {"parameter": "gb_a1_p_b1_p", "coeff": "1"}
  ]
}
```

Rows represent \(\gamma(X,Y)\)'s coefficient of `Z` as a linear combination
of the independent gb parameters. Store one row per nonzero `(X,Y,Z)` in
Schema 1 basis order, with each gb parameter appearing at most once per row.
The bracket correction is \(\kappa\gamma(X,Y)\). First-order terms are
computed by rewriting \(b_j^s a_1^\sigma =
a_1^\sigma b_j^s-\mathrm{gb}_{\sigma,j,s}\kappa\); terms containing
\(\kappa^2\) are discarded. `Z` may be a Schema 1 basis generator or `K`
when an oscillator calculation produces the scalar identity. `K` is the
central identity already declared in Schema 1, not an added PBW generator.

## Source convention caveat

The inhomogeneous definition assigns odd parity to both \(\mathrm{gb}\) and
\(\kappa\), but its exchange relation has an odd left-hand side
\([b_{\bar 0},a_{\bar 1}]\) and an even right-hand side
\(\mathrm{gb}_{\bar 1}\kappa_{\bar 1}\). Thus the stated parities and exchange
relation are not parity-homogeneous simultaneously. Schema 2 preserves the
source's stated parameter parity and literal exchange relation as formal
first-order rewrite rules; it does not resolve that inconsistency.
