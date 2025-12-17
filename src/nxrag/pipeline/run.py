"""Top-level pipeline runner (MVP).

Performs:
- per-run folder under outputs_path (default var/runs/)
- snapshots input
- writes IR extraction outputs
- deterministic corpus retrieval (no embeddings yet)
- packs a final prompt (template bound with {request}/{facts}/{approved_defaults}/{context})
- writes prompt.txt for traceability
- calls LLM
- validates:
    * exemplar-backed details are included when present
    * no-new-claims lint (simple lexical guard)
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
from nxrag.prompting.pack import pack_part_description_prompt
from nxrag.settings import load_settings
from nxrag.validate.require_exemplars import validate_exemplar_inclusion
from nxrag.validate.style_lint import validate_no_new_claims


def _utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _format_ir_facts(ir: dict[str, Any]) -> str:
    """Compact, human-readable facts block derived from IR."""
    part = ir.get("part") or {}
    materials = ir.get("materials") or []
    tolerances = ir.get("tolerances") or []
    features = ir.get("features") or []

    lines = [
        f"- Part name: {part.get('name') or 'Not detected'}",
        f"- Units: {part.get('units') or 'Not detected'}",
    ]

    if materials:
        for m in materials:
            lines.append(f"- Material: {m.get('value')}  [evidence: {m.get('evidence')}]")
    else:
        lines.append("- Material: Not detected")

    if tolerances:
        for t in tolerances:
            lines.append(f"- Tolerance: {t.get('value')}  [evidence: {t.get('evidence')}]")
    else:
        lines.append("- Tolerance: Not detected")

    if features:
        for f in features:
            lines.append(f"- Feature: {f.get('kind')}  [evidence: {f.get('evidence')}]")
    else:
        lines.append("- Feature: Not detected")

    return "\n".join(lines)


def _combined_missing(*items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for lst in items:
        for x in lst:
            if x not in seen:
                out.append(x)
                seen.add(x)
    return out


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

    # --- Step 1: IR extraction (truth layer) ---
    from nxrag.ir.extract import extract_ir, render_ir_summary

    raw_input_text = _read_text(in_path)
    ir = extract_ir(
        raw_input_text,
        source_path=str(in_path),
        source_type="nxopen_python_text",
    )
    (run_dir / "ir.json").write_text(json.dumps(ir, indent=2), encoding="utf-8")
    (run_dir / "ir_summary.txt").write_text(render_ir_summary(ir), encoding="utf-8")

    # --- Step 2: Retrieval (deterministic; no embeddings yet) ---
    corpus_root = repo_root / settings.corpus_path
    context_text, approved_defaults_text, retrieval_log = retrieve_context(
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

    packed = pack_part_description_prompt(
        template_text=template_text,
        request_text=raw_input_text.strip(),
        facts_text=_format_ir_facts(ir),
        approved_defaults_text=approved_defaults_text,
        context_text=context_text,
    )
    (run_dir / "prompt.txt").write_text(packed.prompt_text, encoding="utf-8")

    # --- Step 4: Generation ---
    client = LLMClient(
        model=settings.default_model,
        max_tokens=settings.max_tokens,
        provider=settings.llm_provider,
    )
    completion = client.complete(packed.prompt_text).strip()

    # --- Step 5: Validation + one retry ---
    exemplar_v = validate_exemplar_inclusion(exemplar_text=packed.exemplar_text, output_text=completion)
    style_v = validate_no_new_claims(output_text=completion, sources_text=packed.prompt_text)

    ok = exemplar_v.ok and style_v.ok
    missing = _combined_missing(exemplar_v.missing, style_v.missing)

    attempts = 1
    retry_prompt_path: Path | None = None

    if not ok:
        corrective = (
            "\n\n---\n\n"
            "CORRECTION REQUIRED:\n"
            "Your previous answer violated one or more constraints.\n"
            "Revise the answer to fix the following issues (only using facts present in the prompt above):\n"
            f"{chr(10).join([f'* {m}' for m in missing])}\n"
            "Do not add any new facts beyond the prompt. Keep exactly 3 sections with the required headings.\n"
        )
        retry_prompt = packed.prompt_text + corrective
        retry_prompt_path = run_dir / "prompt_retry_1.txt"
        retry_prompt_path.write_text(retry_prompt, encoding="utf-8")

        completion_retry = client.complete(retry_prompt).strip()
        attempts += 1

        exemplar_v2 = validate_exemplar_inclusion(exemplar_text=packed.exemplar_text, output_text=completion_retry)
        style_v2 = validate_no_new_claims(output_text=completion_retry, sources_text=packed.prompt_text)

        completion = completion_retry
        exemplar_v = exemplar_v2
        style_v = style_v2
        ok = exemplar_v.ok and style_v.ok
        missing = _combined_missing(exemplar_v.missing, style_v.missing)

    # --- Step 6: Write artifacts ---
    generation_log: dict[str, Any] = {
        "provider": settings.llm_provider,
        "model": settings.default_model,
        "max_tokens": settings.max_tokens,
        "attempts": attempts,
        "retry_used": attempts > 1,
        "retry_prompt_path": str(retry_prompt_path) if retry_prompt_path else None,
        "validation": {
            "ok": ok,
            "missing": missing,
            "exemplar": {"ok": exemplar_v.ok, "missing": exemplar_v.missing},
            "no_new_claims": {"ok": style_v.ok, "missing": style_v.missing},
        },
        "notes": "Validators are lexical MVP: exemplar inclusion + no-new-claims lint.",
    }
    (run_dir / "generation.json").write_text(json.dumps(generation_log, indent=2), encoding="utf-8")
    (run_dir / "output.md").write_text(completion + "\n", encoding="utf-8")

    print(f"Running pipeline for {in_path} with model {settings.default_model}")
    print(f"Wrote run artifacts to: {run_dir}")
    print(f"- {run_dir / 'ir.json'}")
    print(f"- {run_dir / 'ir_summary.txt'}")
    print(f"- {run_dir / 'retrieved.json'}")
    print(f"- {run_dir / 'prompt.txt'}")
    if retry_prompt_path:
        print(f"- {retry_prompt_path}")
    print(f"- {run_dir / 'generation.json'}")
    print(f"- {run_dir / 'output.md'}")
    print(f"- {input_snapshot}")
