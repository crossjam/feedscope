# AGENTS Preferences Action Plan

**Plan timestamp:** 2025-11-19 18:26 UTC

## Objectives
- Align all upcoming work with the development preferences documented in `AGENTS.md`.

## Checklist
- [x] Run all Python-related commands via `uv run` (tests, linting, CLI invocation) and prefer `uv sync`/`uv add` when changing dependencies. Documented test execution in `tests/README.md` to reinforce the usage pattern.
- [x] Add the missing dev tooling (`ruff`, `ty`, `pytest`, `poethepoet`) via `uv add --dev` so the repo follows the suggested stack. Added them to the `dev` dependency group in `pyproject.toml` (manual edit due to offline `uv add` failures).
- [x] Use Typer/Click when extending the CLI (the existing Typer app already satisfies the preference) and rely on `loguru` for any new logging output, adding it via `uv add` if it isn’t already a dependency. `loguru` is now part of the base dependencies for future logging work.
- [x] Create a `tests/` directory for future pytest coverage and treat every new feature (notably CLI subcommands) as a candidate for automated tests. Seeded the directory with a README that calls out `uv run pytest`.
- [ ] Keep `poe` (if present) in mind for task automation and document any added UI tasks or commands in the plan.
- [x] After surveying the `content/` markdowns, translate Feedbin API capabilities into CLI subcommand ideas, then plan how to implement them. The ideas below remain the basis for future sessions.

## Feedbin API Subcommand Ideas
**Plan update timestamp:** 2025-11-19 18:28 UTC

- `feedscope entries list` (per [`content/entries.md`](content/entries.md)) to wrap `GET /v2/entries.json` with filters for `--page`, `--since`, `--read`, `--starred`, `--per-page`, `--mode=extended`, and `--include-*` flags.
- `feedscope entries show` for `GET /v2/entries/<id>.json` so the CLI can inspect the entry plus the `original`/`content_diff`/`images` metadata described in the same file.
- `feedscope unread list|mark-read|mark-unread` following [`content/unread-entries.md`](content/unread-entries.md) for fetching unread IDs and toggling them via `POST`/`DELETE`.
- `feedscope starred list|star|unstar` based on [`content/starred-entries.md`](content/starred-entries.md), including the 1,000-id request limit and optional follow-up `GET /v2/entries.json?ids=...`.
- `feedscope saved-search list|create|update|delete` mirroring [`content/saved-searches.md`](content/saved-searches.md) to manage named queries and optionally show entry IDs or full entry JSON.
- `feedscope imports create|list|status` implementing the OPML import lifecycle from [`content/imports.md`](content/imports.md).
- `feedscope pages save` to post URLs (and optional titles) to `POST /v2/pages.json` as outlined in [`content/pages.md`](content/pages.md).
- `feedscope tags rename|delete` plus `feedscope taggings list|create|delete` to cover [`content/tags.md`](content/tags.md) and [`content/taggings.md`](content/taggings.md).
- `feedscope icons list` for `GET /v2/icons.json` so the CLI can dump favicon mappings per [`content/icons.md`](content/icons.md).
- `feedscope extract full-content <url>` referencing [`content/extract-full-content.md`](content/extract-full-content.md) to sign Mercury Parser requests and surface the JSON response.
- `feedscope recently-read list|create` to expose the history described in [`content/recently-read-entries.md`](content/recently-read-entries.md).
- `feedscope updated list|mark-read` following [`content/updated-entries.md`](content/updated-entries.md) so users can iterate updated entry IDs and fetch diffs via `GET /v2/entries.json?include_original=true&include_content_diff=true`.
- `feedscope feeds get` to fetch feed metadata (`content/feeds.md`) and the per-feed entries endpoint (`GET /v2/feeds/<id>/entries.json`), handling `404`/`403`.
