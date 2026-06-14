# PyPI Publishing

CodeGlance publishes through GitHub Actions and PyPI Trusted Publishing. The workflow does not need
a PyPI API token or GitHub secret.

## GitHub Actions

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `.github/workflows/ci.yml` | pushes to `main`, pull requests, manual runs | Run the test matrix and build distributions. |
| `.github/workflows/publish.yml` | GitHub releases, manual runs | Build distributions and publish them to PyPI. |

## PyPI Setup

Create a PyPI Trusted Publisher for the `codeglance` project:

| Field | Value |
| --- | --- |
| Owner | GitHub repository owner |
| Repository name | `CodeGlance` |
| Workflow filename | `publish.yml` |
| Environment name | `pypi` |

For a first PyPI release, use PyPI's pending publisher flow for a new project. After that, releases
can publish through the same workflow.

## Release Flow

1. Update the version in `pyproject.toml`, `src/codeglance/__init__.py`, the README badge, and brand badge text.
2. Commit and push to GitHub.
3. Confirm the CI workflow passes.
4. Create a GitHub release for the version tag, such as `v0.0.1`.
5. The `Publish to PyPI` workflow builds `dist/` and uploads it through Trusted Publishing.

Manual runs of `publish.yml` are enabled for recovery, but release-triggered publishing should be the
normal path.
