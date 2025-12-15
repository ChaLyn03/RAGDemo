"""Command-line interface entrypoint for nxrag."""

from __future__ import annotations

import argparse

from nxrag.pipeline.run import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run nxrag pipeline")
    parser.add_argument("input", help="Path to input document or folder")
    parser.add_argument("--config", default="configs/app.yaml", help="Path to app configuration")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_pipeline(input_path=args.input, config_path=args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
