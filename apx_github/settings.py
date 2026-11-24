"""Where a setting comes from on a machine, in order: the process environment (`AP_GITHUB_<KEY>`), then the plugin's options store."""

from __future__ import annotations

import os
from typing import Any, Optional

from action_platform.core.service_access import AccessError
from action_platform.plugins.options import FileOptions

from apx_github.checks import Org
from apx_github.client import API_URL, client

SLUG = "github"


def setting(key: str, options: Any = None) -> Optional[str]:
    found = os.environ.get(f"AP_{SLUG}_{key}".upper())

    if not found:
        found = (options or FileOptions(SLUG)).get(key)

    return str(found) if found else None


def connect(options: Any = None) -> Org:
    org = setting("org", options)
    token = setting("token", options)
    missing = [
        f"AP_GITHUB_{k.upper()}" for k, v in (("org", org), ("token", token)) if not v
    ]

    if missing:
        raise AccessError(
            f"github: set {', '.join(missing)} (or the plugin's options) to read the organization"
        )

    return Org(client(str(token), setting("api_url", options) or API_URL), str(org))
