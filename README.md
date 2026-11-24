# apx-github

[GitHub](https://github.com) for [Action Platform](https://github.com/actionplatform/action-platform): access to a GitHub organization for the platform's service access, and read-only checks of its repositories. `apx-` is the prefix every Action Platform extension carries.

```bash
action-platform plugin install github
export AP_GITHUB_ORG=my-company AP_GITHUB_TOKEN=…      # or Plugins → GitHub → Configure on the platform
action-platform github branch-protection
action-platform github repo-settings
```

The access capability runs where the core runs service access: on a hosted platform whose API image carries this plugin, with the options filled under **Plugins** for the organization. It needs no personal token there: it uses the organization's GitHub connection (**Settings → Git**, core 0.34 or later). The tools and commands run on the machine that installed it.

## What it does

### Access

The plugin gives the core's service access the `github` service: the platform reads who has what in the organization, compares it with the members, roles and teams of the Action Platform organization, and applies the difference. It covers:

| Resource | Levels |
|---|---|
| `org` | `member`, `admin` — membership and role, pending invitations included |
| `team/<slug>` | `member`, `maintainer` — a team is created when a grant names one that does not exist |
| `repo/<name>` | `pull`, `triage`, `push`, `maintain`, `admin` — direct collaborators; a team's own permission on a repository is read as a grant of the account `team:<slug>` |

Accounts are GitHub logins. A team grant also brings organization membership, and the last organization admin is never removed or demoted. Access is configured only through the plugin's options (`org`, and optionally `token`, `api_url`) and the platform's GitHub connection; the environment is not read for it. See the platform's service access documentation for the operations (`access_who`, `access_audit`, `access_sync`, `access_grant`, `access_revoke`, `access_offboard`).

### Tools

Read-only; each is an MCP tool `github_<name>` and a command `action-platform github <name>`, answering JSON. Both take an optional repository name; without it they cover every repository of the organization.

| Tool | Command | Answers, per repository |
|---|---|---|
| `github_branch_protection` | `branch-protection` | default branch; whether a protection rule or an active ruleset applies to it; the ruleset rule types; required approving reviews; required status checks; whether force pushes are allowed. A repository whose protection GitHub does not return to the token (a private repository on a plan without protection, a token without admin on it) carries the reason in `note` and null values. |
| `github_repo_settings` | `repo-settings` | visibility, default branch, archived, delete branch on merge, allow auto-merge, secret scanning, secret scanning push protection, Dependabot alerts, Dependabot security updates. A value the token cannot see is null. |

## Options

| Option | Machine | Meaning |
|---|---|---|
| `org` | `AP_GITHUB_ORG` | the organization login |
| `token` | `AP_GITHUB_TOKEN` | optional on a hosted platform: when empty, access uses the organization's GitHub connection. A classic personal access token of an organization owner otherwise |
| `api_url` | `AP_GITHUB_API_URL` | only for GitHub Enterprise Server, e.g. `https://github.example.com/api/v3`; default `https://api.github.com` |

For the tools on a machine the environment variable wins over the plugin's options file; access reads the options only.

## The GitHub connection

On a hosted platform (core 0.34 or later) set only `org` under **Plugins → GitHub → Configure**. Access then uses the GitHub account the organization connected under **Settings → Git**, which must be an owner of the organization. The plugin declares what it needs, so connecting asks GitHub for it:

| The connection is | It needs | Where it is granted |
|---|---|---|
| a GitHub App (*Create GitHub App* on the platform) | Organization permission **Members: Read and write**, repository permission **Administration: Read and write**, the app installed on the organization | an app created after the plugin was installed carries them; for an older one, add them in the app's *Permissions & events* and accept the new permissions on the organization's installation |
| an OAuth App | scopes `admin:org` and `repo` | *Connect GitHub* again: connecting asks for them |

When something is missing, the audit names it, with the links to grant it — never a request for a token. The token option, when set, wins over the connection.

## Token permissions

| To | Scopes |
|---|---|
| change access (`access_sync`, `access_grant`, `access_revoke`, `access_offboard`) | `admin:org` and `repo` |
| read access (`access_who`, `access_audit`) | `read:org` and `repo` |
| `github_repo_settings` | `repo`; secret scanning and Dependabot settings are null where GitHub does not return them to the token |
| `github_branch_protection` | `repo`; where GitHub does not return a repository's protection to the token, the repository carries the reason in `note` |

The plugin talks only to the GitHub API host (`api.github.com`, or `api_url`).

## Develop

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check . && pytest -q
```

`tests/fake.py` answers the routes and fields GitHub sends. `tests/live/` runs the reads against a real organization and is skipped unless `AP_GITHUB_LIVE=1`:

```bash
AP_GITHUB_LIVE=1 AP_GITHUB_ORG=my-company AP_GITHUB_TOKEN=… pytest tests/live
```

Reference: [writing a plugin](https://github.com/actionplatform/action-platform/blob/master/docs/contribute_plugins.md).
