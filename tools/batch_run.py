"""Run the pipeline for multiple inputs."""

from __future__ import annotations

from pathlib import Path

from nxrag.pipeline.run import run_pipeline


def main(inputs_dir: str, config_path: str) -> None:
    for path in Path(inputs_dir).iterdir():
        if path.is_file():
            run_pipeline(input_path=path, config_path=config_path)
