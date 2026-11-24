# AGENTS.md

Rules an AI agent (or a new contributor) follows in this repository.

## What this is

`apx-github`, an Action Platform plugin: the `github` access provider for the core's service access, `github_*` read tools and `action-platform github` commands. The contract every plugin follows is `SPEC.md` in [apx-example](https://github.com/actionplatform/apx-example); read it before changing the shape of anything here.

## Layout

- `plugin.py`: the `Plugin`; `access(options)` reads only `options` and returns `None` without an `org`, an `AccessError` without a `token`.
- `provider.py`: `GitHubProvider`, the `AccessProvider` over the REST API.
- `checks.py`: `Org`, the read-only checks behind the tools and commands; `models.py` their answers.
- `settings.py`: `AP_GITHUB_<KEY>`, then the plugin's options file, for the tools on a machine.
- `tools.py`, `cli.py`: the same reads as MCP tools and CLI commands.

## Code

- Python 3.11+, `ruff check . && ruff format --check .`, `pytest` green before a commit.
- No comments inside function bodies; no test docstrings. Module docstrings say what the module is for.
- `register` declares only — no I/O at import or in `register`.
- Never monkey-patch `action_platform.*`.
- Talk to GitHub through the core's `Http` only; tests drive `tests/fake.py`, which answers only what the real API answers, never the network.
- A tool ships only after `tests/live/` has run it against a real organization.
- `needs` lists every host and environment variable the plugin touches.

## Commits and branches

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `type(scope): description`; one commit per concern; stage files explicitly. Git-flow: `<kind>/<issue>-<slug>` from `master`, kinds `feature bugfix hotfix release chore docs refactor test ci perf`; never commit on `master`. One pull request per issue.

## Release

`action-platform release <level>`; the tag publishes to PyPI; then a PR to `plugins-index` with the new `latest`.
