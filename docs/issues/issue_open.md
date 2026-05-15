Created: 2026-05-15
Category: proposal

## I01-1. C(n+1) basis and root system design

### Background

C(n+1) = osp(2|2n) is a type-C basic classical Lie superalgebra.
Unlike B(0,n) = osp(1|2n) which uses a supplementary real fermion a_0
with {a_0, a_0} = 1, C(n+1) uses a standard fermionic pair (a_1_p, a_1_m)
with {a_1_p, a_1_m} = 1.

This changes the basis structure, introduces ε-roots (absent in B(0,n)),
and requires a new PBW ordering decision.

The mathematical reference is Frappat, Sciarrino, Sorba,
*Dictionary on Lie Algebras and Superalgebras* (2000), Chapter on C(n+1).

### Requirements

1. Define the even and odd basis elements for C(n+1) for n = 1, 2, 3,
   following the oscillator realization in Frappat et al.
2. Enumerate all root vectors (even: ε-roots, 2δ-roots, δ±δ-roots;
   odd: ε±δ-roots) and Cartan generators
3. Determine the PBW ordering convention for C(n+1), compatible with
   the existing B(0,n) v5.0 ordering where possible
4. Update `handover/notation.md` with the finalized conventions

### Supplementary Information

#### Deliverable Format
document (updated `handover/notation.md` + summary in Response section)

#### Related Folders/Files
- handover/notation.md
- (reference) https://github.com/ritsumei-aoi/osp-triviality — B(0,n) notation

#### Related Issues
none (first issue)

### Completion Criteria

- [ ] Even and odd basis lists defined for C(1), C(2), C(3) with explicit
      element counts matching the expected dimensions
- [ ] PBW ordering decided, documented, and justified
- [ ] `handover/notation.md` updated with finalized conventions
