import asyncio
import importlib
import os
import unittest
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from unittest import mock

from action_platform.core.service_access import AccessError
from action_platform.plugins import Loaded, Plugins, PluginState, registry
from action_platform.plugins.options import FileOptions

from apx_github import GitHubPlugin
from apx_github.provider import GitHubProvider
from apx_github.settings import connect, setting

TOOLS = {"github_branch_protection", "github_repo_settings"}


class Opts(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class Connected(Opts):
    def __init__(self, found, **values):
        super().__init__(**values)
        self.found = found

    def credential(self, kind):
        return self.found if kind == "github" else None


@dataclass(frozen=True)
class Credential:
    kind: str
    token: str
    login: str = ""
    api_url: Optional[str] = None
    scopes: Optional[tuple] = None
    app: Optional[str] = None


HAS_CONNECTIONS = hasattr(importlib.import_module("action_platform.abc"), "Connection")


class AccessOptions(unittest.TestCase):
    def test_no_org_means_no_access(self):
        self.assertIsNone(GitHubPlugin().access(Opts()))
        self.assertIsNone(GitHubPlugin().access(Opts(token="t")))

    def test_without_token_nor_connection_it_says_to_connect(self):
        with self.assertRaisesRegex(AccessError, "connect GitHub under Settings → Git"):
            GitHubPlugin().access(Opts(org="acme"))

    def test_the_connection_is_used_when_the_token_option_is_empty(self):
        found = Credential("github", "gho-x", "ana", None, None, "ap-app")
        provider = GitHubPlugin().access(Connected(found, org="acme"))

        self.assertEqual(provider.http.headers["authorization"], "Bearer gho-x")
        self.assertEqual(provider.app, "ap-app")
        self.assertEqual(provider.http.base, "https://api.github.com")

    def test_the_token_option_wins_over_the_connection(self):
        found = Credential("github", "gho-x", "ana")
        provider = GitHubPlugin().access(Connected(found, org="acme", token="t"))

        self.assertEqual(provider.http.headers["authorization"], "Bearer t")
        self.assertIsNone(provider.app)

    @unittest.skipUnless(HAS_CONNECTIONS, "core without connections")
    def test_it_declares_the_github_connection(self):
        (declared,) = GitHubPlugin.connections

        self.assertEqual(declared.kind, "github")
        self.assertEqual(declared.scopes, ("admin:org", "repo"))
        self.assertIn(("members", "write"), declared.permissions)

    def test_the_provider_comes_from_the_options(self):
        provider = GitHubPlugin().access(
            Opts(org="acme", token="t", api_url="https://ghe.example.com/api/v3")
        )

        self.assertIsInstance(provider, GitHubProvider)
        self.assertEqual(provider.org, "acme")
        self.assertEqual(provider.http.base, "https://ghe.example.com/api/v3")

    def test_the_default_api_is_github_com(self):
        provider = GitHubPlugin().access(Opts(org="acme", token="t"))

        self.assertEqual(provider.http.base, "https://api.github.com")

    def test_the_environment_is_not_read(self):
        env = {"AP_GITHUB_ORG": "acme", "AP_GITHUB_TOKEN": "t"}

        with mock.patch.dict(os.environ, env):
            self.assertIsNone(GitHubPlugin().access(Opts()))


class Settings(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patch = mock.patch.dict(os.environ, {"AP_HOME": self.tmp.name})
        patch.start()
        self.addCleanup(patch.stop)

        for key in ("AP_GITHUB_ORG", "AP_GITHUB_TOKEN", "AP_GITHUB_API_URL"):
            os.environ.pop(key, None)

    def test_environment_first_then_options(self):
        options = FileOptions("github")
        options.set("org", "stored")

        self.assertEqual(setting("org"), "stored")

        with mock.patch.dict(os.environ, {"AP_GITHUB_ORG": "env"}):
            self.assertEqual(setting("org"), "env")

    def test_a_missing_setting_is_named(self):
        with mock.patch.dict(os.environ, {"AP_GITHUB_ORG": "acme"}):
            with self.assertRaisesRegex(AccessError, "AP_GITHUB_TOKEN") as raised:
                connect()

        self.assertNotIn("AP_GITHUB_ORG,", str(raised.exception))

    def test_connect_builds_the_client(self):
        env = {"AP_GITHUB_ORG": "acme", "AP_GITHUB_TOKEN": "t"}

        with mock.patch.dict(os.environ, env):
            org = connect()

        self.assertEqual(org.org, "acme")
        self.assertEqual(org.http.base, "https://api.github.com")


class Surface(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.plugins = Plugins(
            [Loaded(GitHubPlugin(), "apx-github", "0.1.0")],
            PluginState(file=Path(self.tmp.name) / "plugins.json"),
        )
        registry._current = self.plugins
        self.addCleanup(registry.reset)

    def tools(self):
        from action_platform.mcp import server

        mcp = server.build()

        return mcp, {t.name: t for t in asyncio.run(mcp.list_tools())}

    def test_the_tools_are_registered_read_only_with_schemas(self):
        _, tools = self.tools()

        self.assertTrue(TOOLS <= set(tools))

        for name in TOOLS:
            self.assertTrue(tools[name].output_schema, name)
            self.assertTrue(tools[name].annotations.read_only_hint, name)

    def test_a_disabled_plugin_refuses(self):
        mcp, _ = self.tools()
        self.plugins.disable("github")

        with self.assertRaisesRegex(Exception, "plugin github is disabled"):
            asyncio.run(mcp.call_tool("github_repo_settings", {}))

    def test_options_declare_the_token_as_a_secret(self):
        kinds = {o.key: o.kind for o in GitHubPlugin.options}

        self.assertEqual(kinds, {"org": "text", "token": "secret", "api_url": "url"})

    def test_the_plugin_declares_what_it_reaches(self):
        plugin = GitHubPlugin()

        self.assertEqual(
            (plugin.slug, plugin.name, plugin.min_core), ("github", "GitHub", "0.33")
        )
        self.assertTrue(any("api.github.com" in n for n in plugin.needs))
        self.assertTrue(any("AP_GITHUB_TOKEN" in n for n in plugin.needs))


class Cli(unittest.TestCase):
    def test_commands_print_the_models_as_json(self):
        import json

        from typer.testing import CliRunner

        from apx_github import cli
        from apx_github.checks import Org
        from tests.fake import FakeGitHub

        github = FakeGitHub()
        github.repo("api")

        with mock.patch.object(cli, "connect", return_value=Org(github, "acme")):
            runner = CliRunner()
            protection = runner.invoke(cli.app, ["branch-protection", "--repo", "api"])
            settings = runner.invoke(cli.app, ["repo-settings"])

        self.assertEqual(json.loads(protection.output)["repos"][0]["repo"], "api")
        self.assertEqual(
            json.loads(settings.output)["repos"][0]["visibility"], "public"
        )
