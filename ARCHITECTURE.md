# Architecture Overview

This project is a small, deterministic RAG reference pipeline. The core goal is traceability: every run writes the artifacts needed to understand how an output was produced.

## Data flow at a glance
```
input file
  -> IR extraction (truth layer)
  -> deterministic corpus retrieval
  -> prompt packing
  -> LLM generation (stub or OpenAI)
  -> validation + optional retry
  -> output + run artifacts
```

## Pipeline stages
1. Input snapshot
   - The input file is copied into the run folder so outputs remain auditable.
2. IR extraction
   - `src/nxrag/ir/extract.py` parses either plain text or NXOpen Python scripts.
   - The IR is conservative: only values backed by line evidence are emitted.
3. Retrieval
   - `src/nxrag/corpus/retrieve.py` selects the first template, exemplars, style rules, and glossary entries by sorted filename.
   - Retrieval is deterministic and does not use embeddings.
4. Prompt packing
   - `src/nxrag/prompting/pack.py` binds `{request}`, `{facts}`, `{approved_defaults}`, and `{context}` into the prompt template.
5. Generation
   - `src/nxrag/llm/client.py` calls a stub provider by default.
   - OpenAI is available when `NX_RAG_LLM_PROVIDER=openai` and `OPENAI_API_KEY` are set.
6. Validation + retry
   - `src/nxrag/validate/require_exemplars.py` checks exemplar inclusion.
   - `src/nxrag/validate/style_lint.py` blocks new claims outside the prompt text.
   - One corrective retry is allowed.
7. Output artifacts
   - `output.md` and `generation.json` are written alongside the run metadata.

## Key modules
- `src/nxrag/pipeline/run.py` orchestrates the full run.
- `src/nxrag/settings.py` loads `configs/app.yaml` and applies env overrides.
- `src/nxrag/ir/` holds IR schema and extraction helpers.
- `src/nxrag/corpus/` holds the deterministic retriever and index stubs.
- `src/nxrag/prompting/` is responsible for prompt sanitization and packing.
- `src/nxrag/llm/` implements the stub and OpenAI provider wiring.
- `src/nxrag/validate/` implements lexical validators.
- `src/nxrag/renderers/` holds output renderers (markdown, docx).

## Configuration and overrides
- Default config lives in `configs/app.yaml`.
- Provider can be overridden with `NX_RAG_LLM_PROVIDER`.
- OpenAI requires `OPENAI_API_KEY` and `requirements-openai.txt`.

## Extension points
- Retrieval: replace `retrieve_context` with BM25 or vector indexes in `src/nxrag/corpus/index/`.
- IR: extend `src/nxrag/ir/extract.py` to parse new inputs or richer evidence.
- Prompting: add new templates in `configs/prompts/` and new doc types in `src/nxrag/doc_types/`.
- Validators: add new checks in `src/nxrag/validate/` to enforce stricter policies.
