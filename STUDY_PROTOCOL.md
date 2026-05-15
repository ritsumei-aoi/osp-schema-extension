# Study Protocol: Prospective Validation of the Issue-Driven Research Workflow

**Version**: 1.0
**Created**: 2026-05-15
**Target repository**: https://github.com/ritsumei-aoi/osp-schema-extension (to be created)

## 1. Study Design

This is a **prospective, single-case validation study** designed to test the
reusability of the Issue-Driven Research Workflow described in the companion
manuscript. The workflow was originally developed retrospectively during the
osp(1|2n) triviality project; this study applies it to a new project from
scratch, with pre-defined metrics and a public audit trail.

### Research Questions Addressed

| RQ | How this study provides evidence |
|---|---|
| RQ1 (Continuity) | Session count × handover updates, measured prospectively |
| RQ2 (Delegation) | AI correction records from trust policy enforcement |
| RQ3 (Schema/Verification) | Schema change frequency over time |
| RQ4 (Reusability) | Reuse rate of B(0,n) components for C(n+1) |

## 2. Task Description

**Primary task (T1)**: Extend the 4-layer JSON schema from B(0,n) = osp(1|2n)
to C(n+1) = osp(2|2n), for n = 1, 2, 3.

**Secondary task (T2)**: Compare rational arithmetic libraries
(`fractions.Fraction` vs `sympy.Rational` vs `gmpy2`) and tensor-based
numerical verification (PyTorch) for the verification pipeline.

## 3. Pre-Defined Metrics

| Metric | Definition | Source | Granularity |
|---|---|---|---|
| session_count | Number of completed ai/ branches merged to main | Git branch history | Project |
| issue_count | Number of issue files in docs/issues/ | File count | Project |
| items_addressed | Numbered items within all issue files | Issue file parse | Per issue |
| schema_changes | Number of schema_version bumps | Git log on schema files | Project |
| ai_corrections | Correction/rejection tags in issue responses | Issue file tags | Per issue |
| session_duration | Wall time from branch creation to merge | Git timestamps | Per session |
| test_failures | pytest FAIL count per commit | Test logs | Per session |
| handover_updates | Updates to handover_memo_latest.md | Git log | Per session |
| reuse_rate | Components reused from B(0,n) vs newly created | Manual count | Project |

## 4. Data Collection

At the end of each session, record the following in `metrics/session_log.csv`:

```
session_id,branch_name,start_time,end_time,issues_created,issues_closed,items_addressed,schema_changes,ai_corrections,test_failures,handover_updates,notes
```

## 5. Analysis Plan

- **RQ1**: Report session count, handover update frequency, and any reopened issues.
- **RQ2**: Classify AI corrections by type (schema design, implementation, verification).
  Report frequency and resolution pattern.
- **RQ3**: Plot schema change frequency over time. Compare with B(0,n) v1–v5 history.
- **RQ4**: Count reused vs new components. Report which workflow mechanisms transferred
  and which required adaptation.

## 6. Limitations (Pre-Declared)

- Single author (same as the primary case study)
- Same mathematical domain (Lie superalgebras), though different type
- No external users or independent replication
- Retrospective bias is reduced but not eliminated (author designed the workflow)

## 7. Artifact Auditability

| Artifact | Location | Verification |
|---|---|---|
| Workflow template | ai-research-workflow-template repo | Inspect templates |
| Issue files | docs/issues/ in osp-schema-extension | Full lifecycle visible |
| Schema files | data/ in osp-schema-extension | Schema validation |
| Session metrics | metrics/session_log.csv | Cross-check with Git log |
| Test results | pytest output in Git history | Re-run tests from any commit |
| Handover history | handover/ in Git history | Inspect diffs |
