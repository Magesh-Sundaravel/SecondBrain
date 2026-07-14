# SecondBrain

A company second-brain agent that answers natural-language questions using a Notion workspace as its only knowledge source, via the Notion MCP server.

Project status: scaffold only. Specification and implementation are in progress — see `docs/` once available.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync

# Install the pre-commit hook
uv run pre-commit install

# Run tests
uv run pytest

# Lint and format check
uv run ruff check .
uv run ruff format --check .

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```
