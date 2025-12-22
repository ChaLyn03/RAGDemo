# Roadmap

This list captures likely next steps and optional enhancements. It is a living document.

## Near term
- Add input folder support and batch runs with a summary index.
- Surface validation failures as structured exit codes.
- Make retrieval deterministic but configurable per run (max exemplars, per-doc size).
- Add a compact run manifest (`run.json`) that links every artifact.

## Mid term
- Add BM25 and vector retrieval as selectable retrievers.
- Expand IR extraction to support richer CAD metadata and materials.
- Add a golden sample suite and regression tests.
- Provide a lightweight web viewer for `var/runs/`.

## Long term
- Add policy-based validators (style, completeness, risk rules).
- Support multiple document types and prompt templates.
- Add a plugin system for custom retrievers, validators, and renderers.
