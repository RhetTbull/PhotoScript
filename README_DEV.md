# Developer Notes for PhotoScript

These notes are so that I can remember how to build and test PhotoScript.

## Setup the environment

- Change to the project directory
- Install [uv](https://github.com/astral-sh/uv): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Create the virtual environment: `uv venv` or `uv venv --python 3.13` to specify a specific version
- Activate the virtual environment: `source .venv/bin/activate`
- Install package dependencies: `uv pip install -r pyproject.toml --extra dev`

## Testing

Tests are written with `pytest`. You must use the `-s` flag when running tests to see the interactive prompts requireed for running the tests.
To test, run `pytest -vv -s`.

## Docs

Build docs with `mkdocs build` then deploy to GitHub pages with `mkdocs gh-deploy`


## Building

To build the project:

- `rm -rf dist; rm -rf build`
- `uv build`

## Versioning

Use [bump2version](https://github.com/c4urself/bump2version):

- `bump2version patch --verbose [--dry-run]`
- `bump2version minor --verbose [--dry-run]`
- `bump2version major --verbose [--dry-run]`

## Change Log

The `CHANGELOG.md` is created with [auto-changelog](https://github.com/cookpete/auto-changelog):

- `git pull`
- `auto-changelog --ignore-commit-pattern CHANGELOG -l 5`
- `git add CHANGELOG.md; git commit -m"Updated CHANGELOG.md [skip ci]"; git push`

## Publishing

To publish to PyPI:

- `uv publish`
