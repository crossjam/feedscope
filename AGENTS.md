## 🧭 Quick Start

You should never need to activate a virtualenv for this project
directly. Let uv handle it. Almost everything package or Python
related should start with ‘uv run‘ . There may be named tasks provided
by the ‘poe‘ package that simplify some things like running linting or
type checking.

If they are not included in the project for development install as
development dependencies
- ruff: for linting
- ty: for type checking
- pytest: for testing
- poethepoet: for task running

```bash
# set up environment from pyproject + uv.lock
uv sync

# run the test suite (quiet, stop on first failure)
uv run pytest -q -x

# run tests with coverage reporting
uv run pytest --cov=./src/feedscope --cov-report=html

# run type checks & lint (if dev deps are present)
uv run ty src/feedscope
uv run ruff check src tests
uv run ruff format src tests

# run the package (replace with your module/CLI)
uv run python -m feedscope --help

# poe is Poe the Poet, a Python task runner
# poe integrates well with pyproject.toml

# list tasks
poe
```

## Python tooling

- Rely on the uv cli tool for packaging
- Prefer uv sync over uv pip where possible
- Use the `uv add` to add new dependencies to the project

## Python testing

- Make a tests dir to hold tests if it doesn’t exits
- Add pytest as a dev dependency of the project using
- Write tests you implement into the tests dir
- Run test with `uv run pytest`

## Python modules

- For cli implementations, prefer click if nothing exists in the
  project
- For logging, prefer loguru

## Planning

When asked, generate plans for work in markdown format. 

Include a timestamp in the plan each time you create a new plan or add
updates to a plan.

Unless directed otherwise add newly created plans to a directory
`plans`. Create that directory if it doesn’t exist.

Usually you should add a markdown checklist for work that needs to be
done. 

Typically creating new tests is added as a task when new functionality
is part of the plan.

If links to project issues are given, try to link to them within the
plan.

