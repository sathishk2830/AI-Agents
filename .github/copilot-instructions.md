# AI Agent Instructions — TP_Creator_AIAgentWithJira_1

Purpose: Short, actionable guidance for AI coding agents working in this workspace.

## Quick discovery steps
- Look for a top-level `README.md` and language manifests (`package.json`, `pyproject.toml`, `requirements.txt`, `setup.py`) before running commands.
- Inspect top-level folders: `src/`, `app/`, `services/`, `tests/`, `infra/` to understand boundaries.

## Code style and formatting
- Prefer existing project config files if present: `.prettierrc`, `pyproject.toml`, `.editorconfig`.
- If none exist, keep edits minimal and follow common idiomatic style for the language (Black for Python, Prettier for JS/TS).

## Build & test commands (try these if language detected)
- Node: `npm ci` then `npm test` (if `package.json` exists).
- Python: `python -m pip install -r requirements.txt` then `pytest` (if `requirements.txt` or `pyproject.toml` exist).
- If no manifest detected, ask before running install/build commands.

## Repository conventions (what to follow)
- Make small, focused changes that touch the fewest files necessary.
- Preserve public interfaces; add migration notes when changing APIs.
- Add or update unit tests for behavior changes and run existing test suites.

## Integration points & secrets
- Search for `.env`, `config/`, `infra/`, or `.github/workflows` to find integrations.
- Never print or commit secrets. If you find secrets, redact them and notify the user immediately.

## PRs and commits
- Create concise commits with descriptive messages and a short PR summary.
- Include verification steps and any environment variables needed to run locally.

## When to ask the user
- For large refactors, architectural changes, or any action that may affect external systems (Jira, production deploy), ask before proceeding.

If you'd like, I can now (a) run detection commands to auto-detect project language, or (b) update these instructions with references to specific files if you point me to key source files. Which would you prefer? 
