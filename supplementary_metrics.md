# Supplementary Session Metrics

**Run ID**: study/thm01-R-gemini38f-b04-C  
**Model**: Gemini 3.8 Flash  

- **Total Execution Time (Wall clock)**: ~8 minutes
- **Total Thinking Time**: ~3 minutes
- **Token Usage (if known)**: Context length ~45k tokens
- **Verification Coverage**:
  - $n=1$ ($C(2)$): 8 dimensions, 4 $gb$ parameters, rank 4/4
  - $n=2$ ($C(3)$): 19 dimensions, 8 $gb$ parameters, rank 8/8
  - $n=3$ ($C(4)$): 34 dimensions, 12 $gb$ parameters, rank 12/12
- **Any other session-level statistics available in your interface**:
  - Zero external tool / web access required.
  - All tests passed with 0 Super-Jacobi errors and full rank constraints on $\mathrm{gb}$.
