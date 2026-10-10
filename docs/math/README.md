# Mathematical Reference for the C(n+1) Case Study

This directory contains self-contained reference documents for the C(n+1) = osp(2|2n) schema extension.
All documents are in English and use LaTeX notation.

## Files

| File | Contents |
|---|---|
| `Cn1_definition.md` | Root system and oscillator realization for C(n+1) = osp(2\|2n) |
| `C_inhomogeneous_definition.md` | Inhomogeneous (gb) deformation of C(n+1) |
| `C_coboundary_definition.md` | Coboundary operator and the triviality condition |
| `B0n_definition.md` | Root system, oscillator realization, central extension κ, and deformation parameters for B(0,n) = osp(1\|2n) (reference case) |
| `B0n_schema_v5.md` | The v5.0 JSON schema specification for B(0,n), to be extended for C(n+1) |

## How to Use

1. Read `B0n_definition.md` and `B0n_schema_v5.md` to understand the base case and its JSON schema.
2. Read `Cn1_definition.md`, `C_inhomogeneous_definition.md`, and `C_coboundary_definition.md` for C(n+1).
3. Produce a complete C(n+1) schema by extending the B(0,n) v5.0 schema, following the issues.

## Primary Reference

Frappat, L., Sciarrino, A., and Sorba, P., *Dictionary on Lie Algebras and Superalgebras*,
Academic Press (2000); see also arXiv:hep-th/9607161.
