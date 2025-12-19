# RAGDemo

RAGDemo is a small, self-contained retrieval‑augmented generation (RAG) reference project. It shows how to glue together a deterministic retriever, a templated prompt, an LLM client (stub or OpenAI), and a lightweight validator while keeping every run traceable on disk.

## What the pipeline does
The end-to-end runner (`nxrag` CLI) performs the following steps:

1. **Load settings** from `configs/app.yaml` (paths, model, provider, limits).
2. **Create a run folder** under `var/runs/` with a UTC timestamp.
3. **Snapshot the input** into the run folder for traceability.
4. **Write a placeholder IR** (`ir.json`) to represent the future structured layer.
5. **Retrieve context** deterministically from the corpus in `assets/corpus/`:
   - picks the first template, up to two exemplars, one style guide, and one glossary entry.
   - concatenates them into a prompt-ready context and writes a detailed retrieval log (`retrieved.json`).
6. **Pack the prompt** using `configs/prompts/part_description.md`, binding `{request}` and `{context}` into `prompt.txt` (plus `prompt_retry_1.txt` if a retry is needed).
7. **Call the LLM** via `src/nxrag/llm/client.py`:
   - `stub` provider (default): deterministic, no API key required.
   - `openai` provider: uses `OPENAI_API_KEY` and the `openai` Python package when available.
8. **Validate exemplar inclusion** and retry once with corrective instructions if exemplar-backed details were omitted.
9. **Write outputs** (`output.md`, `generation.json`) alongside the input snapshot.

## Repository layout

- `configs/` – application, prompt, and retrieval defaults (`app.yaml`, `prompts/part_description.md`).
- `assets/corpus/` – deterministic corpus used by the retriever (templates, exemplars, style rules, glossary).
- `assets/samples/` – example inputs (`nx_code/widget_housing_request.txt`) and expected outputs for demos.
- `src/nxrag/` – pipeline implementation (CLI, retrieval, LLM client, validation, rendering stubs).
- `var/runs/` – per-run artifacts (ignored by Git) created by the pipeline.
- `tools/` – utility scripts and helpers for development.
- `SETUP.md` – setup and run guide for different environments.

## Quickstart
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   pip install -r requirements.txt
   ```
2. (Optional) Switch to the real provider:
   ```bash
   pip install -r requirements-openai.txt
   export NX_RAG_LLM_PROVIDER=openai  # requires OPENAI_API_KEY
   ```
3. Run the sample request using the stubbed defaults:
   ```bash
   nxrag assets/samples/nx_code/widget_housing_request.txt
   ```
4. Inspect the generated run folder under `var/runs/` (e.g., `var/runs/20251215T082627Z_widget_housing_request/`) to review `retrieved.json`, `prompt.txt`, `generation.json`, and `output.md`.

## Offline / secure-environment setup
If you cannot access the public internet from your environment, the pipeline still runs with the stub provider and a minimal dependency set.

1. Copy the repo into your environment (including `assets/`, `configs/`, and `src/`).
2. Install only the core runtime requirement:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
3. Run with the default stub provider (no API key required):
   ```bash
   nxrag assets/samples/nx_code/widget_housing_request.txt
   ```

Optional extras:
- For the real OpenAI provider, pre-download the wheel and install it offline with `pip install -r requirements-openai.txt`.
- For linting/testing in the secure environment, install `pip install -r requirements-dev.txt`.

## Configuration reference
`configs/app.yaml` drives most runtime behavior:

- `paths.assets` / `paths.corpus` / `paths.outputs` – where inputs, corpus docs, and run artifacts live.
- `app.default_model` – model name passed to the LLM client.
- `llm.provider` – `stub` (deterministic placeholder) or `openai` (real API calls). Override with `NX_RAG_LLM_PROVIDER`.
- `limits.max_tokens` – passed directly to the provider; controls response length.

## Contributing
- Install tooling with `pip install -r requirements-dev.txt`.
- Formatting, linting, and type checks run via `pre-commit`. Install hooks with `pre-commit install`.
- The codebase favors small, composable modules. Keep new components focused and document their artifacts in the run folder for traceability.
