# Developer Notes for photoscript

These notes are so that I can remember how to build and test photoscript.

## Setup the environment

- Install poetry: `pip install poetry`
- Run `poetry install` to install the dependencies
- Run `poetry shell` to enter the virtual environment

## Testing

To test, run `poetry run pytest`.

## Building Docs

- `cd docsrc`
- `make github`

## Building

To build the project:

- `rm -rf dist; rm -rf build`
- `poetry build`
