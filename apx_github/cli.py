"""`action-platform github …` — the same reads as the tools, JSON on stdout."""

from __future__ import annotations

from typing import Any, Optional

import typer
from pydantic import BaseModel

from apx_github.settings import connect

app = typer.Typer(
    help="GitHub: branch protection and settings of the organization's repositories.",
    no_args_is_help=True,
)
options: Any = None


def _print(model: BaseModel) -> None:
    typer.echo(model.model_dump_json(indent=2))


@app.command("branch-protection")
def branch_protection(
    repo: Optional[str] = typer.Option(None, help="Only this repository"),
) -> None:
    """Protection of each repository's default branch."""
    _print(connect(options).branch_protection(repo))


@app.command("repo-settings")
def repo_settings(
    repo: Optional[str] = typer.Option(None, help="Only this repository"),
) -> None:
    """Settings of each repository."""
    _print(connect(options).repo_settings(repo))
