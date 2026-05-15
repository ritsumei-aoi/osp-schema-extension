# osp-schema-extension

A prospective case study applying the
[Issue-Driven Research Workflow](https://github.com/ritsumei-aoi/ai-research-workflow-template)
to extend the 4-layer JSON schema from B(0,n) = osp(1|2n) to C(n+1) = osp(2|2n).

## Purpose

This repository was created from scratch to prospectively validate the workflow
described in the companion manuscript:

> H. Aoi, *A collaborative workflow for human-AI research in pure mathematics*,
> submitted to IPSJ JIP Special Issue on Software Engineering, 2026.

The entire Git history — from the first commit to the final results — is publicly
auditable. All issue files, handover documents, schema evolution, and AI session
records are preserved as evidence of the workflow in action.

## Study Design

- **Primary task (T1)**: Extend the 4-layer JSON schema for C(n+1) = osp(2|2n), n=1,2,3
- **Secondary task (T2)**: Compare arithmetic/numerical libraries for the verification pipeline
- **Pre-defined metrics**: See [STUDY_PROTOCOL.md](STUDY_PROTOCOL.md)
- **Measurement period**: May–June 2026

## Theme-based Branching Strategy

This repository uses persistent theme branches that act as the primary working branches for specific case studies:
- **T1: C(n+1) Schema Extension**: `ai/t1-schema-extension`
- **T2: Numerical Libraries**: `ai/t2-numerical-libraries`

All issues, commits, and merges related to a theme must target its respective branch instead of the repository's `main` branch.

## Related Repositories

| Repository | Role |
|---|---|
| [ai-research-workflow-template](https://github.com/ritsumei-aoi/ai-research-workflow-template) | Workflow template (source of handover/, trust policy) |
| [osp-triviality](https://github.com/ritsumei-aoi/osp-triviality) | Primary case study (retrospective, B(0,n)) |
| This repository | Prospective validation study (C(n+1)) |

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for how to set up a new project using the
workflow template from scratch.

## Repository Structure

```
├── STUDY_PROTOCOL.md          # Pre-defined metrics and analysis plan
├── QUICKSTART.md              # Setup guide for new users
├── handover/                  # Workflow and session management
│   ├── workflow_common.md     # Common rules
│   ├── workflow_method_b.md   # Method B (AI agent)
│   ├── handover_memo_latest.md
│   └── notation.md            # C(n+1) notation
├── ai_trust_policy.md         # AI delegation boundaries
├── docs/
│   ├── issues/                # Issue files (created during study)
│   └── json_schema_specification.md  # Schema spec (evolves during study)
├── src/                       # Source code (generated during study)
├── tests/                     # Tests (generated during study)
├── data/                      # Output data (generated during study)
└── metrics/
    └── session_log.csv        # Session-level metrics
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
