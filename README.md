# osp-schema-extension: AI-Driven Mathematical Research

This repository contains the computational artifacts and workflow logs for a human-AI collaborative research project. The primary goal of this project is to verify the triviality conditions for the inhomogeneous deformations of the Lie superalgebra C(n+1) = osp(2|2n).

This repository also serves as the public data source for the empirical case study presented in our paper on the **Issue-Driven Research Workflow**.

## Repository Structure and Branch Guide

To observe how different Large Language Models (LLMs) navigated this mathematical research task under various workflow constraints, please explore the specific branches listed below.

### Tier A: Iterative Workflow (The "Issue-Driven" Baseline)
These branches demonstrate the proposed workflow, where the task was broken down into 8 sequential issues requiring human approval at each stage.
- **`study/thm01-01`**: Gemini 3.1 Pro (Preview) - *Successfully completed via custom algebra engine.*
- **`study/thm01-02`**: Gemini 3 Flash (Preview) - *Successfully completed with minor normalization corrections.*
- **`study/thm01-03`**: Gemini 3.1 Flash-lite (Preview) - *Required significant human intervention but completed the pipeline.*

### Tier C: One-Shot Challenge
These branches simulate a traditional "zero-shot" environment where the agent was asked to solve the entire problem autonomously in a single session. They reveal a spectrum of AI behaviors, from rigorous synthesis to "aesthetic logic" and "sophistry".
- **`study/thm01-X-06`**: Claude 4.6 Opus - *Gold Standard. Built a rigorous rational engine and self-fixed a Grassmann property bug.*
- **`study/thm01-X-01`**: Gemini 3.1 Pro (Preview) - *Gold Standard. Exact algebraic proof via left nullspace tracing.*
- **`study/thm01-X-02`**: Gemini 3 Flash (Preview) - *Honest numerical execution via SVD.*
- **`study/thm01-X-04`**: Claude 4.6 Sonnet - *Aesthetic Logic. Wrote correct code but produced a flawed natural language proof (failed to recognize H_1 structure).*
- **`study/thm01-X-05`**: GPT-5.4 - *Sophistry. Claimed universal triviality using a flawed gauge transformation argument without performing the required computations.*
- **`study/thm01-X-03`**: Gemini 3.1 Flash-lite (Preview) - *Honest Failure. Admitted inability to perform the complex algebra required.*

## For AI Agents
If you are an AI agent continuing this project, please start by reading the instructions in the `handover/` directory:
- **[handover/README.md](handover/README.md)** (Start here)
