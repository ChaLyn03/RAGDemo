"""Top-level pipeline runner (MVP).

Now performs:
- per-run folder under outputs_path (default var/runs/)
- snapshots input
- writes placeholder IR
- deterministic corpus retrieval (no embeddings yet)
- packs a final prompt (template bound with {request} and {context})
- writes prompt.txt for traceability
- calls LLM
- validates that exemplar-backed details are included when present
- if validation fails: regenerates once with a corrective instruction
- writes output.md + generation.json (incl. validation outcome)
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from nxrag.corpus.retrieve import retrieve_context
from nxrag.llm.client import LLMClient
from nxrag.settings import load_settings
from nxrag.validate.require_exemplars import validate_exemplar_inclusion


def _utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _pack_prompt(template_text: str, request_text: str, context_text: str) -> str:
    # Strict substitution (template should contain both placeholders)
    return template_text.replace("{request}", request_text).replace("{context}", context_text)


def run_pipeline(input_path: str | Path, config_path: str | Path) -> None:
    settings = load_settings(config_path)
    in_path = Path(input_path)

    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    repo_root = Path.cwd()
    runs_root = _ensure_dir(repo_root / settings.outputs_path)

    run_id = f"{_utc_stamp()}_{in_path.stem}"
    run_dir = _ensure_dir(runs_root / run_id)

    # Snapshot input for traceability
    input_snapshot = run_dir / f"input{in_path.suffix or '.txt'}"
    shutil.copyfile(in_path, input_snapshot)

    # --- Step 1: IR placeholder (truth layer) ---
    ir: dict[str, Any] = {
        "ir_version": "v1",
        "source": {"type": "nxopen_python_text", "path": str(in_path)},
        "part": {"name": None, "units": None},
        "features": [],
        "parameters": [],
        "evidence": {
            "notes": "IR extraction not implemented yet; placeholder created by MVP runner."
        },
    }
    (run_dir / "ir.json").write_text(json.dumps(ir, indent=2), encoding="utf-8")

    # --- Step 2: Retrieval (deterministic; no embeddings yet) ---
    corpus_root = repo_root / settings.corpus_path
    context_text, retrieval_log = retrieve_context(
        corpus_root,
        repo_root=repo_root,
        max_exemplars=2,
        max_chars_per_doc=2000,
    )
    (run_dir / "retrieved.json").write_text(
        json.dumps(retrieval_log, indent=2), encoding="utf-8"
    )

    # --- Step 3: Prompt packing ---
    template_path = repo_root / "configs" / "prompts" / "part_description.md"
    template_text = _read_text(template_path)

    request_text = _read_text(in_path).strip()
    packed_prompt = _pack_prompt(template_text, request_text, context_text)
    (run_dir / "prompt.txt").write_text(packed_prompt, encoding="utf-8")

    # --- Step 4: Generation ---
    client = LLMClient(
        model=settings.default_model,
        max_tokens=settings.max_tokens,
        provider=settings.llm_provider,
    )

    completion = client.complete(packed_prompt).strip()

    # --- Step 5: Validate exemplar inclusion and retry once if needed ---
    validation = validate_exemplar_inclusion(context_text=context_text, output_text=completion)
    attempts = 1
    retry_prompt_path: Path | None = None

    if not validation.ok:
        # Add a corrective instruction, but keep the same packed prompt content for traceability.
        corrective = (
            "\n\n---\n\n"
            "CORRECTION REQUIRED:\n"
            "Your previous answer failed to incorporate exemplar-backed details.\n"
            "Revise the answer to include the following missing items (only if present in excerpts):\n"
            f"- {chr(10).join([f'* {m}' for m in validation.missing])}\n"
            "Do not add any new facts beyond the excerpts. Keep exactly 3 sections with the required headings.\n"
        )
        retry_prompt = packed_prompt + corrective
        retry_prompt_path = run_dir / "prompt_retry_1.txt"
        retry_prompt_path.write_text(retry_prompt, encoding="utf-8")

        completion_retry = client.complete(retry_prompt).strip()
        attempts += 1

        validation_retry = validate_exemplar_inclusion(
            context_text=context_text, output_text=completion_retry
        )
        if validation_retry.ok:
            completion = completion_retry
            validation = validation_retry
        else:
            # Keep the retry output anyway (best effort), but record failure.
            completion = completion_retry
            validation = validation_retry

    # --- Step 6: Write artifacts ---
    generation_log: dict[str, Any] = {
        "provider": settings.llm_provider,
        "model": settings.default_model,
        "max_tokens": settings.max_tokens,
        "attempts": attempts,
        "validation": {
            "ok": validation.ok,
            "missing": validation.missing,
        },
        "notes": (
            "Validator is lexical MVP: it requires exemplar-backed details when present in retrieved context. "
            "See prompt.txt (and prompt_retry_1.txt if created)."
        ),
    }
    (run_dir / "generation.json").write_text(
        json.dumps(generation_log, indent=2), encoding="utf-8"
    )

    (run_dir / "output.md").write_text(completion + "\n", encoding="utf-8")

    print(f"Running pipeline for {in_path} with model {settings.default_model}")
    print(f"Wrote run artifacts to: {run_dir}")
    print(f"- {run_dir / 'ir.json'}")
    print(f"- {run_dir / 'retrieved.json'}")
    print(f"- {run_dir / 'prompt.txt'}")
    if retry_prompt_path:
        print(f"- {retry_prompt_path}")
    print(f"- {run_dir / 'generation.json'}")
    print(f"- {run_dir / 'output.md'}")
    print(f"- {input_snapshot}")
