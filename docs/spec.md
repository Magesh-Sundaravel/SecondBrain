# SecondBrain — Specification

## Problem Statement

Company knowledge lives scattered across many Notion pages, databases, and nested blocks.
Finding an answer today means manually searching, opening pages, and reading through
content that may or may not be relevant. SecondBrain is a natural-language agent that
answers questions by reading directly from the company's Notion workspace through the
Notion MCP server — with no separate copy, index, or embedding of that content. Every
answer must be traceable back to the Notion page(s) it came from.

## Goals

- Accept a natural-language question from a user (via CLI) and return a grounded answer.
- Answer using only information retrieved live from Notion via Notion MCP tools at query time.
- Cite the source Notion page(s) for every answer.
- Explicitly say the information could not be found, rather than guessing, when the
  workspace does not contain an answer.
- Keep the agent a thin reasoning/orchestration layer: it decides which Notion MCP
  read tools to call and synthesizes their results, and does nothing else.

## Non-Goals

- No custom RAG pipeline, embeddings, vector database, or custom indexing of Notion content.
- No write access to Notion — the agent may only call Notion MCP **read** tools.
- No persistent storage or caching of Notion content beyond a single query's execution.
- No web UI — a CLI is the only supported interface for this scope.
- No multi-workspace or multi-tenant support — one Notion workspace per deployment.
- No support for non-Notion data sources.
- No custom authentication/authorization system beyond what the Notion MCP server itself requires.

## Tech Stack

- **Language:** Python 3.13, managed with `uv`.
- **Agent framework:** LangGraph, for orchestrating the reasoning loop and Notion MCP tool calls.
- **MCP integration:** Notion's official MCP server, connected as a tool provider to the agent.
- **CLI:** Typer (or equivalent lightweight CLI framework).
- **Testing:** pytest, with `slow`/`integration` markers for tests requiring live Notion access.
- **Linting/formatting:** Ruff.
- **Packaging/CI:** uv-managed `pyproject.toml`; GitHub Actions running Ruff + pytest on every PR.

## Tool Contract

The agent connects to Notion as an MCP client and may invoke **read-only** Notion MCP tools
only, for example (exact tool names depend on the Notion MCP server's exposed surface):

- Search the workspace for pages/databases matching a query.
- Retrieve a page's content and properties.
- Retrieve a database's schema and query/filter its entries.
- Retrieve block children (to read nested content: sub-pages, toggles, nested lists, etc.).
- List/browse pages a user has access to.

The agent **must not** call any Notion MCP tool that creates, updates, deletes, or archives
content. If the connected MCP server exposes write tools, the agent's tool selection must
exclude them by construction (e.g., an explicit allow-list of read tool names), not by
prompting alone.

## Definition of Done

The MVP is considered done when:

1. A user can run a CLI command with a natural-language question and receive an answer.
2. The agent retrieves all supporting information from Notion via MCP read tools at
   query time — no hardcoded or pre-indexed content.
3. Every answer cites the specific Notion page(s) (title and/or URL) it was derived from.
4. When the workspace does not contain the answer, the agent states that explicitly
   instead of fabricating a response.
5. All 8 acceptance-test queries below behave as described against a configured demo
   Notion workspace.
6. `ruff check`, `ruff format --check`, and `pytest` (excluding slow/integration) all
   pass in CI on every PR.
7. Setup and usage are documented in the README.

## Acceptance-Test Queries

These are run against a demo Notion workspace configured locally (see Phase 3 setup).
Exact wording/content depends on that workspace, but each query exercises a distinct
capability the agent must demonstrate.

1. **Single-page factual lookup** — e.g. "What is our PTO / vacation policy?"
   Expect a direct answer citing the one page it came from.
2. **Search-driven lookup** — e.g. "Who is the point of contact for the Marketing team?"
   Expect the agent to search the workspace to locate the right page before answering.
3. **Database aggregation** — e.g. "List all open action items assigned to \<person>."
   Expect the agent to query a Notion database and return matching rows with the
   source database cited.
4. **Project status lookup** — e.g. "What is the current status of \<project name>?"
   Expect an answer reflecting the latest status recorded in Notion, with citation.
5. **Meeting notes / decision lookup** — e.g. "What did we decide in the last \<team> sync?"
   Expect the agent to locate and summarize the relevant meeting notes page.
6. **Out-of-scope / unknown question** — e.g. "What is our company's stock ticker symbol?"
   (assuming this is not documented in the workspace). Expect the agent to state the
   information was not found, not guess or hallucinate.
7. **Nested-content lookup** — e.g. "What are the steps in our incident response runbook?"
   Expect the agent to read nested/child blocks (sub-pages, toggles, numbered lists) to
   assemble the full answer, not just top-level page text.
8. **Broad/summarization question** — e.g. "Summarize what we know about \<topic>."
   Expect the agent to draw from multiple relevant pages, citing each one used.
