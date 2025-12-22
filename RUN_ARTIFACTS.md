# Run Artifacts Guide

Each pipeline run creates a folder under `var/runs/` named like:

```
var/runs/20251215T082627Z_widget_housing_request/
```

These files are written for traceability and debugging.

## Standard artifacts
- `input.txt` (or `input.<ext>`)
  - Snapshot of the original request file.
- `ir.json`
  - Intermediate representation (IR) extracted from the input.
- `ir_summary.txt`
  - Human-readable summary of the IR.
- `retrieved.json`
  - Retrieval log: which corpus files were selected and why.
- `prompt.txt`
  - Final prompt sent to the LLM (includes request, facts, defaults, and context).
- `generation.json`
  - Metadata about the LLM call and validation results.
- `output.md`
  - Final response text written by the pipeline.

## Conditional artifacts
- `prompt_retry_1.txt`
  - Written only when validation fails and a retry is triggered.

## How to use the artifacts
- Start with `output.md` for the final result.
- If the result is missing facts, check `generation.json` for validation failures.
- Inspect `prompt.txt` to confirm what the model saw.
- Use `retrieved.json` to verify the template, exemplars, style rules, and glossary in play.
- Use `ir.json` and `ir_summary.txt` to confirm which facts were extracted from the input.
