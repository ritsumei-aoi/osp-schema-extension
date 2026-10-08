# C(n+1) Schema 3: Evaluated Structure

Schema 3 files are named `C_{n}_evaluated.json`. They combine the Schema 1
undeformed structure constants with Schema 2 gamma coefficients evaluated at
a concrete assignment of the gb parameters.

The `evaluation` object records the selected profile, central symbol, and
complete parameter assignment. `evaluated_structure_constants` is the
nonzero union of the Schema 1 and evaluated Schema 2 entries. Each row has
`X`, `Y`, and `Z` generator labels (or central identity `K`), plus exact
rational-string fields `base_coeff` and `evaluated_gamma_coeff`. These encode
\([X,Y]_0+\kappa\gamma(X,Y)\); the gamma coefficient is the numeric value
after substitution, with \(\kappa\) left formal. A zero coefficient is
written as `"0"`, and rows for which both coefficients vanish are omitted.

The default reproducible profile is `uniform_plus_one`: every gb parameter
is assigned the integer \(+1\).
