# Execution Workflow (No-Gate condition)

You are an AI agent driven by a file-based issue system.

1. Process `docs/issues/I01.md` to `docs/issues/I08.md` strictly in order, in a single session.
2. For each issue:
   - Perform the requested code, math, or document work.
   - Check the Completion Criteria yourself and mark them `[x]`.
   - Record your decisions (including options you considered), results, and verification output in the issue's `### Response` section.
   - Commit your changes with the message `I0N: <short label>`.
3. Do NOT stop for human approval. No human will respond until all eight issues are complete.
4. After I08, push your branch once and end the session.
