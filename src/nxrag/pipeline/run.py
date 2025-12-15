"""Top-level pipeline runner for the demo flow."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Sequence

from nxrag.corpus.chunking import chunk_markdown
from nxrag.corpus.ids import chunk_id
from nxrag.corpus.manifest.build import build_manifest
from nxrag.corpus.retrieve import retrieve_chunks
from nxrag.doc_types.part_description import assemble_part_description
from nxrag.llm.client import LLMClient
from nxrag.observability.artifacts import save_artifact
from nxrag.observability.tracing import timer
from nxrag.prompting.pack import build_prompt
from nxrag.prompting.sanitize import strip_trailing_whitespace
from nxrag.renderers.markdown import render_document
from nxrag.settings import load_settings
from nxrag.ir.schema_v1 import Chunk, build_chunk


def _load_request(input_path: Path) -> str:
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    return input_path.read_text(encoding="utf-8")


def _load_corpus(settings) -> Sequence[Chunk]:
    chunks: list[Chunk] = []
    manifest = build_manifest(settings.corpus_path)
    for entry in manifest:
        for idx, content in enumerate(chunk_markdown(entry.path)):
            chunks.append(
                build_chunk(
                    chunk_id(entry.path, idx, content),
                    content,
                    {"source": str(entry.path), "tags": ",".join(entry.tags)},
                )
            )
    return chunks


def _assemble_prompt(request_text: str, retrieved: Sequence[Chunk]) -> str:
    system_path = Path("configs/prompts/system.md")
    template_path = Path("configs/prompts/part_description.md")
    context = "\n\n".join(
        f"[{chunk.metadata.get('source', chunk.id)}]\n{chunk.content.strip()}" for chunk in retrieved
    )
    prompt = build_prompt(system_path, template_path).format(
        request=request_text.strip(), context=context
    )
    return strip_trailing_whitespace(prompt)


def run_pipeline(input_path: str | Path, config_path: str | Path) -> Path:
    settings = load_settings(config_path)
    input_path = Path(input_path)

    with timer("load request"):
        request_text = _load_request(input_path)

    with timer("load corpus"):
        corpus_chunks = _load_corpus(settings)

    with timer("retrieve"):
        top_chunks = retrieve_chunks(request_text, corpus_chunks, limit=settings.max_chunks)

    with timer("prompt+llm"):
        prompt = _assemble_prompt(request_text, top_chunks)
        llm_client = LLMClient(model=settings.default_model)
        llm_summary = llm_client.complete(prompt)

    with timer("assemble document"):
        title = request_text.splitlines()[0].strip() or "Part"
        document = assemble_part_description(title, request_text, top_chunks, llm_summary)
        rendered = render_document(document)

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    output_path = save_artifact(f"{document.id}-{timestamp}.md", rendered)
    print(f"Saved demo output to {output_path}")

    return output_path
