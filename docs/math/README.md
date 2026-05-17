# Mathematical Reference for the Prospective Case Study

This directory contains self-contained mathematical reference documents
for the prospective case study on C(n+1) = osp(2|2n) schema extension.
All documents are in English and use LaTeX notation for mathematical expressions.

## Purpose

These documents provide the minimum necessary mathematical background
so that an AI agent working in the `osp-schema-extension` repository can
produce correct, self-contained output without accessing external resources.

## Files

| File | Contents |
|---|---|
| `B0n_definition.md` | Root system, oscillator realization, central extension κ, and deformation parameters for B(0,n) = osp(1\|2n) |
| `B0n_schema_v5.md` | The v5.0 JSON schema specification for B(0,n) — the base schema to be extended for C(n+1) |
| `Cn1_definition.md` | Root system and oscillator realization for C(n+1) = osp(2\|2n); differences from B(0,n) |

## How to Use

1. Read `B0n_definition.md` to understand the algebraic structure of the base case.
2. Read `B0n_schema_v5.md` to understand the JSON schema format used for B(0,n).
3. Read `Cn1_definition.md` to understand the new structure for C(n+1).
4. Produce a **complete** C(n+1) schema: start from the B(0,n) v5.0 schema and apply the C(n+1) modifications to every relevant field.

## Primary Reference

Frappat, L., Sciarrino, A., and Sorba, P.,
*Dictionary on Lie Algebras and Superalgebras*,
Academic Press (2000); see also arXiv:hep-th/9607161.

The κ central extension follows Bakalov and Sullivan (2017) and
the conventions in: H. Aoi, *On the triviality of inhomogeneous deformations
of osp(1|2n)*, preprint 2026 (see `docs/drafts/aoi2026_triviality_osp1_2n.tex`).
