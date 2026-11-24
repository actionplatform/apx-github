"""The plugin: access to a GitHub organization for the core's service access, and read-only checks of its repositories."""

from __future__ import annotations

from typing import Optional

from action_platform.abc import Option, Plugin, Surface
from action_platform.core.service_access import AccessError, AccessProvider
from action_platform.plugins.options import Options

from apx_github import cli
from apx_github.client import API_URL
from apx_github.provider import GitHubProvider
from apx_github.tools import register_tools


class GitHubPlugin(Plugin):
    slug = "github"
    name = "GitHub"
    description = "Access to a GitHub organization (members, teams, repository permissions) and read-only checks of branch protection and repository settings"
    min_core = "0.33"
    needs = [
        "net: api.github.com (or the api_url option on GitHub Enterprise Server)",
        "env: AP_GITHUB_ORG, AP_GITHUB_TOKEN, AP_GITHUB_API_URL (or the same keys in the plugin's options)",
    ]
    options = [
        Option(
            "org",
            "Organization",
            "text",
            help="The organization login, e.g. my-company.",
        ),
        Option(
            "token",
            "Token",
            "secret",
            help="Classic token from an organization owner: admin:org and repo to change access, read:org and repo to read.",
        ),
        Option(
            "api_url",
            "API URL",
            "url",
            help=f"Only for GitHub Enterprise Server: https://github.example.com/api/v3. Default {API_URL}.",
        ),
    ]

    def register(self, surface: Surface) -> None:
        if surface.mcp is not None:
            register_tools(surface.mcp, surface.options)

        if surface.cli is not None:
            cli.options = surface.options
            surface.cli.add_typer(cli.app, name="github")

    def access(self, options: Options) -> Optional[AccessProvider]:
        org = options.get("org")

        if not org:
            return None

        token = options.get("token")

        if not token:
            raise AccessError("github: set the token option to manage the organization")

        return GitHubProvider(
            str(org), str(token), str(options.get("api_url") or API_URL)
        )
