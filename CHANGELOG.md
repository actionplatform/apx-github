# Changelog

## v0.2.0 — 2026-11-24

### Features
- **access:** use the organization's GitHub connection when no token is set

### Bug Fixes
- **access:** read with the read scopes; the connection's token stays on its own host

### Docs
- what reading and changing access each need
- the GitHub connection replaces the token on a hosted platform
- blank line
- where the access capability runs
- install from the tag until the package is on PyPI; where access runs

## v0.1.0 — 2026-11-24

### Features
- **plugin:** GitHubPlugin with options, access and the github tools and commands
- **tools:** read-only branch protection and repository settings checks
- **access:** GitHub access provider for the core's service access

### Bug Fixes
- **access:** compare admin accounts case-insensitively in the last-admin guard

### Docs
- README and AGENTS for apx-github

### Tests
- **live:** read-only suite against a real organization

### Build
- package as apx-github with the github entry point

### Chores
- remove the example target, overlay, release strategy, skill and manifests
