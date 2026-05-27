# The C(n+1) Inhomogeneous Deformation Task

This document outlines the background and the specific 8-stage iterative workflow used to evaluate Large Language Models (LLMs) in our case study.

## Mathematical Background

The core mathematical task is to verify the triviality conditions for the inhomogeneous deformations of the Lie superalgebra C(n+1) = osp(2|2n). 

The deformation is defined by modifying the canonical (anti)commutation relations between the fermionic and bosonic oscillators using a set of parity-1 parameters (the "gb matrix") and an odd central element kappa. 

The goal is to computationally prove whether this deformation gamma_gb is a coboundary (gamma_gb = delta f) for some odd linear map f: g -> g, using exact rational arithmetic to avoid floating-point approximations.

## The 8-Stage Iterative Workflow (Tier A)

To safely manage this complex derivation, the "Issue-Driven Research Workflow" decomposed the problem into 8 sequential tasks. AI agents were required to produce and verify structured JSON artifacts at each step before proceeding.

### 1. Basis and Root System Design (I01)
- **Task**: Define the even and odd basis lists for C(n+1) (n=1, 2, 3) and determine the PBW ordering.
- **Output**: A finalized notation document mapping oscillators to Lie algebra generators.

### 2. Schema 1 (Algebra Structure) Specification (I02)
- **Task**: Design the JSON schema to store the undeformed algebra structure.
- **Output**: `json_schema_specification.md` defining the exact data contract.

### 3. Structure Constant Generation (I03)
- **Task**: Implement a Python engine to compute the exact structure constants using Weyl-Clifford normal ordering.
- **Output**: `C_n_structure.json` files containing the baseline Lie superalgebra bracket data.

### 4. Super Jacobi Identity Verification (I04)
- **Task**: Write a script to verify that the generated structure constants satisfy the graded anti-symmetry and Super Jacobi identities for all generator triples.

### 5. Schema 2 (Symbolic Gamma Structure) (I05)
- **Task**: Extend the normal ordering engine to compute the first-order deformation symbolically in terms of the gb parameters.
- **Output**: `C_n_gamma.json` recording the symbolic cocycle components.

### 6. Schema 3 (Evaluated Structure) (I06)
- **Task**: Substitute a specific non-zero numerical profile (e.g., all gb=1) into the symbolic gamma matrix.
- **Output**: `C_n_evaluated.json` representing a concrete deformed algebra instance.

### 7. Schema 4 (Coboundary Structure) (I07)
- **Task**: Implement the formal coboundary operator delta f for a generic odd, parity-reversing linear map f.
- **Output**: `C_n_coboundary.json` detailing the linear system spanning the coboundary image.

### 8. Triviality Condition Search (I08)
- **Task**: Solve the linear system using exact rational arithmetic to determine if the evaluated deformation lies within the coboundary image.
- **Output**: The final mathematical proof of triviality/non-triviality based on the rank analysis.

