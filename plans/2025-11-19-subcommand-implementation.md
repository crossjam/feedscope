# Subcommand Implementation Plan

**Plan timestamp:** 2025-11-19 18:28 UTC

**Plan update timestamp:** 2025-11-19 18:32 UTC

**Plan update timestamp:** 2025-11-19 18:33 UTC

## Scope
- Deliver the Feedbin-aligned subcommands outlined in `plans/2025-11-19-agents-preferences.md`, starting with entries retrieval, state management (unread/starred/updated/recently read), saved searches/tags, imports/pages/icons, and support utilities such as feed metadata and the full-content extractor.

## Infrastructure tasks
- [ ] Introduce new Typer sub-app modules (e.g., `entries.py`, `state.py`, `searches.py`, `utils.py`) so the main `feedscope` app can keep concerns separate while still using Click under the hood.
- [ ] Add `loguru` via `uv add` and use it consistently for debug/info messages inside the new command modules; keep user-facing output via `typer.echo`.
- [ ] Create a `tests/` directory (per AGENTS) and populate it with CLI-focused pytest files that use Typer’s `CliRunner` to simulate commands.
- [ ] Document `uv run pytest`, `uv run ruff`, and `uv run ty` in README/CONTRIBUTING if needed (so future contributors remember AGENTS requirements).
- [ ] Add the `stamina` retry/backoff library via `uv add` and wrap `httpx` requests with its policies so the CLI gracefully handles transient errors for GET/DELETE requests, logging retries through `loguru`.
- [ ] Ensure the cached `CacheClient` from `hishel` is configured to store responses for safe GET-like requests; make cache-control decisions explicit so stale data isn't re-used for write operations.

## Phase 1: Entries & feed metadata
- [ ] Build `feedscope entries list` with support for `--since`, `--page`, `--per-page`, `--read/--starred`, `--mode`, `--include-original`, `--include-enclosure`, and `--include-content-diff`, matching `content/entries.md`.
- [ ] Add `feedscope entries show <entry-id>` to fetch `GET /v2/entries/<id>.json` along with error handling for status codes listed in `content/entries.md`.
- [ ] Implement `feedscope entries feed <feed-id>` (or similar) to wrap `GET /v2/feeds/<id>/entries.json` and honor the same filters.
- [ ] Write tests verifying query parameter serialization and response handling (mock `httpx.Client` via `respx` or similar) for each command.

## Phase 2: Entry state management
- [ ] Provide `feedscope unread list` plus `mark-read`/`mark-unread` commands that POST/DELETE `unread_entries` per `content/unread-entries.md`, enforcing the 1,000-entry limit with validation.
- [ ] Mirror that behavior for `feedscope starred list/star/unstar` to match `content/starred-entries.md`.
- [ ] Add `feedscope updated list` and `feedscope updated mark-read` using `content/updated-entries.md`, reusing the entry-fetch helpers from Phase 1 to display diffs when `--include-diff` is requested.
- [ ] Create `feedscope recently-read list/create` per `content/recently-read-entries.md`.
- [ ] Cover these commands with dedicated tests that mock the ID arrays and confirm the right HTTP verb/payload is sent.

## Phase 3: Saved searches, tags & taggings
- [ ] Add `feedscope saved-search list`, `get`, `create`, `update`, and `delete` commands following `content/saved-searches.md`, including `--include-entries` and pagination options.
- [ ] Provide `feedscope tags rename`/`delete` and `feedscope taggings list/create/delete` inspired by `content/tags.md` and `content/taggings.md`.
- [ ] Ensure CLI output exposes the relevant JSON arrays (e.g., after rename/delete the updated taggings array) and write pytest coverage for success/failure paths.

## Phase 4: Supporting APIs
- [ ] Implement `feedscope imports create|list|status` that uploads OPML, sets `Content-Type: text/xml`, and re-uses the client cache.
- [ ] Provide `feedscope pages save` to POST URLs/titles (`content/pages.md`) and return the created entry payload.
- [ ] Add `feedscope icons list` for `GET /v2/icons.json` and consider caching or optional JSONL output for scripting.
- [ ] Create an `extract` command that, given credentials stored in config (new `extract.username`/`extract.secret` entries), builds the HMAC-SHA1 signature as in `content/extract-full-content.md` before fetching parse results.
- [ ] Ensure each API helper has a test that mocks `httpx` responses and validates that required headers/payloads are constructed correctly.

## Phase 5: Workflow & polishing
- [ ] Update the README (or add CLI docs) to describe the new commands, referencing the content docs as the API source of truth.
- [ ] Run `uv run ruff format`, `uv run ty`, and `uv run pytest` after implementing each phase to keep the codebase clean.
- [ ] Optional: expose `feedscope auth status` improvements or helper `feedscope config show` if needed to expose additional configuration fields (e.g., Extract credentials).
