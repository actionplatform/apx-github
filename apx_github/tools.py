"""`github_*` MCP tools: read-only checks of the organization's repositories."""

from __future__ import annotations

from typing import Annotated, Any, Optional

from action_platform.mcp.annotations import READ_ONLY
from pydantic import Field

from apx_github.models import BranchProtection, OrgSettings
from apx_github.settings import connect

Repo = Annotated[
    Optional[str], Field(description="Only this repository; every repository if empty")
]


def register_tools(mcp: Any, options: Any) -> None:
    @mcp.tool(annotations=READ_ONLY)
    def branch_protection(repo: Repo = None) -> BranchProtection:
        """Protection of each repository's default branch, from branch protection rules and rulesets: whether it is protected, required approving reviews, required status checks, whether force pushes are allowed."""
        return connect(options).branch_protection(repo)

    @mcp.tool(annotations=READ_ONLY)
    def repo_settings(repo: Repo = None) -> OrgSettings:
        """Settings of each repository: visibility, default branch, archived, delete branch on merge, auto-merge, secret scanning, push protection, Dependabot alerts and security updates. A value is null when the token cannot see it."""
        return connect(options).repo_settings(repo)
