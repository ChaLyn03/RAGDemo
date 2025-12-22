"""Command-line interface entrypoint for nxrag."""

from __future__ import annotations

import argparse

from nxrag.pipeline.run import run_pipeline

DEFAULT_INPUT = "assets/samples/nx_code/widget_housing_request.txt"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run nxrag pipeline")
    parser.add_argument("input", nargs="?", help="Path to input document (optional)")
    parser.add_argument("--config", default="configs/app.yaml", help="Path to app configuration")
    parser.add_argument(
        "--profile",
        choices=["demo", "user", "dev"],
        help="Preset defaults for common workflows",
    )
    parser.add_argument(
        "--provider",
        choices=["stub", "openai"],
        help="Override LLM provider (stub or openai)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Override max tokens for the LLM response",
    )
    parser.add_argument(
        "--distilled",
        action="store_true",
        help="Shortcut for a shorter response (sets --max-tokens 600)",
    )
    parser.add_argument(
        "--defense",
        action="store_true",
        help="Fail fast if validation fails (no retry)",
    )
    return parser


def main(argv: list[str] | None = None, *, default_profile: str | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    profile = args.profile or default_profile
    input_path = args.input

    if not input_path:
        input_path = DEFAULT_INPUT

    provider_override = args.provider
    max_tokens_override = args.max_tokens

    if args.distilled and max_tokens_override is None:
        max_tokens_override = 600

    if profile == "demo":
        provider_override = provider_override or "stub"
    elif profile == "dev":
        provider_override = provider_override or "stub"

    run_pipeline(
        input_path=input_path,
        config_path=args.config,
        provider_override=provider_override,
        max_tokens_override=max_tokens_override,
        defense_mode=args.defense,
    )
    return 0


def speed_rack(argv: list[str] | None = None) -> int:
    return main(argv, default_profile="demo")


if __name__ == "__main__":
    raise SystemExit(main())
