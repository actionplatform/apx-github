"""Against the real GitHub API, read only: set AP_GITHUB_LIVE=1, AP_GITHUB_ORG and AP_GITHUB_TOKEN. Nothing here changes the organization."""

import os
import unittest

from apx_github.provider import GitHubProvider
from apx_github.settings import connect, setting

LIVE = os.environ.get("AP_GITHUB_LIVE") == "1"


@unittest.skipUnless(
    LIVE, "AP_GITHUB_LIVE=1, AP_GITHUB_ORG and AP_GITHUB_TOKEN run this suite"
)
class LiveRead(unittest.TestCase):
    def test_access_reads_the_organization(self):
        provider = GitHubProvider(
            str(setting("org")),
            str(setting("token")),
            setting("api_url") or "https://api.github.com",
        )

        grants = provider.read()

        self.assertTrue(grants)
        self.assertTrue(all(g.service == "github" for g in grants))
        self.assertEqual(len({g.key for g in grants}), len(grants))
        self.assertTrue(any(g.resource == "org" and g.level == "admin" for g in grants))
        self.assertTrue(
            all(
                provider.valid(g.resource, g.level) == ""
                for g in grants
                if not g.account.startswith("team:")
            )
        )

    def test_repo_settings_read_every_repository(self):
        org = connect()

        listed = {r["name"] for r in org.repos()}
        out = org.repo_settings()

        self.assertTrue(listed)
        self.assertEqual({r.repo for r in out.repos}, listed)

        for r in out.repos:
            self.assertIn(r.visibility, ("public", "private", "internal"), r.repo)
            self.assertTrue(r.default_branch, r.repo)
            self.assertIsInstance(r.delete_branch_on_merge, bool, r.repo)
            self.assertIsInstance(r.dependabot_alerts, bool, r.repo)

    def test_branch_protection_reads_every_repository(self):
        org = connect()

        listed = {r["name"] for r in org.repos()}
        out = org.branch_protection()

        self.assertEqual({r.repo for r in out.repos}, listed)

        for r in out.repos:
            if r.note:
                self.assertIsNone(r.protected, r.repo)
            else:
                self.assertIsInstance(r.protected, bool, r.repo)
                self.assertIsInstance(r.required_reviews, int, r.repo)
                self.assertIsInstance(r.force_pushes_allowed, bool, r.repo)

        self.assertTrue(any(not r.note for r in out.repos))

    def test_one_repository(self):
        org = connect()
        name = org.repos()[0]["name"]

        self.assertEqual([r.repo for r in org.repo_settings(name).repos], [name])
        self.assertEqual([r.repo for r in org.branch_protection(name).repos], [name])
