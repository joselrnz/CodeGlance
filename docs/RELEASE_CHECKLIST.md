# Release Checklist

Use this before pushing or publishing Codeglance.

## Version

- Package version is static at `0.0.1` until intentionally changed.
- Keep these files aligned when changing the package version:
  - `pyproject.toml`
  - `src/codeglance/__init__.py`
  - README badge text
  - brand badge text

Note: `knowledge-graph.json` uses a graph schema version. That is separate from the PyPI package
version.

## Local Validation

Run from the repo root:

```bash
python -m pytest
python -m build
python -m codeglance generate . --out .codeglance/outputs --profile all --full
python -m codeglance review . -o .codeglance/outputs/review.md
```

Then serve locally:

```bash
python -m codeglance serve . --dir .codeglance/outputs --host 0.0.0.0 --watch --profile all
```

Open:

```text
http://127.0.0.1:8777/glance.html
```

## Installed Package Smoke Test

Create a temporary virtual environment and install the built wheel:

```bash
python -m venv .venv-release
.venv-release\Scripts\python -m pip install --upgrade pip
.venv-release\Scripts\python -m pip install --force-reinstall dist\codeglance-0.0.1-py3-none-any.whl
.venv-release\Scripts\codeglance --help
```

Smoke-test the main commands in a temporary repo:

```bash
.venv-release\Scripts\codeglance init
.venv-release\Scripts\codeglance generate . --out .codeglance/outputs --profile all
.venv-release\Scripts\codeglance review . -o .codeglance/outputs/review.md
```

## UI Validation

Check `glance.html` on desktop and mobile widths:

- Overview opens cleanly.
- Drill mode shows files/classes without function noise.
- Explore mode can show deeper graph detail.
- Tour opens without hiding the app chrome.
- Tools sidebar and Inspector sidebar remain reachable.
- Terminal opens at the bottom.
- Zoom controls stay bottom-center and do not overlap the terminal.
- Breadcrumbs go up one directory and back to Overview.
- Refresh is quiet: no pop-up banner; the toolbar Refresh button marks newer output.

## Generated Files

Expected `--profile all` outputs:

- `index.html`
- `glance.html`
- `graph.static.html`
- `wiki.html`
- `context.md`
- `agent.md`
- `processes.md`
- `processes.json`
- `onboarding.md`
- `impact.md`
- `review.md`
- `llms.txt`
- `llm-context.schema.json`
- `knowledge-graph.toon`
- `knowledge-graph.json`
- `meta.json`

## Commit Policy

Usually commit source, docs, tests, examples, and release notes.

Usually do not commit local generated output unless it is intentionally promoted:

- `.codeglance/outputs/`
- `.codeglance/screenshots/`
- temporary cloned repos
- release test virtual environments

Generated context that may be useful for teams:

- `llms.txt`
- `agent.md`
- `knowledge-graph.toon`
- `llm-context.schema.json`
- `review.md`

For this repo, keep generated outputs ignored unless the release process explicitly asks to include
them.
