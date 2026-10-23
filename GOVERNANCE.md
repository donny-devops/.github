# Governance

Default community health files in this repository apply to every
[donny-devops](https://github.com/donny-devops) repository that does not
define its own copy.

This repository must stay **public**. GitHub only inherits default community
health files from a public `.github` repository.

## Roles

| Role | Who | Responsibility |
| :--- | :--- | :--- |
| Maintainer | [@donny-devops](https://github.com/donny-devops) | Reviews PRs, publishes releases, triages security reports |
| Contributor | Anyone with a PR | Follows [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Decision making

- Routine changes (docs, templates, workflow fixes) merge after CI is green and a maintainer review.
- Security-sensitive or breaking workflow changes require an explicit maintainer approval.
- Default community files are the source of truth. A repository overrides them by adding its own file of the same type.

## Protected defaults

The following files are the recommended GitHub community-standards set and
should remain present at the repository root or under `.github/`:

- `README.md`
- `LICENSE`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `GOVERNANCE.md`
- `.github/FUNDING.yml`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`

## Enforcement

Conduct issues are handled under [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
Vulnerability reports are handled under [`SECURITY.md`](SECURITY.md).
