---
name: "DoD: Definition of Done"
description: Run the full Definition of Done checks and report evidence
category: Workflow
tags: [workflow, quality-gates, verification]
---

Run the Definition of Done checks for this repository and report the result as evidence.

Execute exactly:

```
pytest -q && ruff check . && mypy && bash .claude/check-arch.sh
```

Rules:
- The command output IS the evidence — "parece funcionar" is not accepted.
- If any step fails, report which one and the relevant error lines.
- Do NOT mark a group as concluded until all steps pass.
- The command must be identical to the one in AGENTS.md "Definition of Done" section.
