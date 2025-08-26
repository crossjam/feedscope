## Python tooling

- Rely on the uv cli tool for packaging
- Prefer uv sync over uv pip where possible
- Use the `uv add` to add new dependencies to the project

## Python testing

- Make a tests dir to hold tests if it doesn’t exits
- Add pytest as a dev dependency of the project using
- Write tests you implement into the tests dir
- Run test with `uv run pytest`


