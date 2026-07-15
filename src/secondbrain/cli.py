"""Command-line entry point."""

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="secondbrain",
        description="Ask questions grounded in your Notion workspace.",
    )
    parser.add_argument("question", nargs="+", help="natural-language question to ask")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse the CLI contract while the agent integration is being built."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.error("the Notion MCP and agent integrations are not configured yet")
    return 2  # pragma: no cover - argparse.error exits
