# Supplementary Session Metrics

**Run ID**: study/thm01-R-gemini38f-b12-C
**Model**: Gemini 3.8 Flash

Please provide the following information from your gemini-cli session statistics:

- **Total Execution Time (Wall clock)**: ~7 minutes
- **Total Thinking Time**: ~2.5 minutes
- **Token Usage (if known)**: Context window within standard limits; full exact symbolic verification completed locally.
- **Any other session-level statistics available in your interface**:
  - Python version: 3.14.8
  - SymPy version: 1.14.0
  - NumPy version: 2.4.4
  - Verified algebras: $C(2) = \mathfrak{osp}(2|2)$, $C(3) = \mathfrak{osp}(2|4)$, $C(4) = \mathfrak{osp}(2|6)$
  - Tested Jacobi identities: 120 triples ($n=1$), 1330 triples ($n=2$), 7140 triples ($n=3$) — all 0 errors.
  - Linear system equations solved: 111 ($n=1$), 1392 ($n=2$), 7027 ($n=3$).
  - Rank differences ($\operatorname{rank}(M_{\text{all}}) - \operatorname{rank}(M_\phi)$): 4 ($n=1$), 8 ($n=2$), 12 ($n=3$), matching $4n$ exactly.
