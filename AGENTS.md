# COLA Cloud Python SDK

This is the public Python SDK for the COLA Cloud API. Keep this repo safe for public GitHub: do not add private workspace notes, credentials, customer data, or internal-only infrastructure details.

## Development

- Use `uv sync` to install dependencies.
- Run tests with `uv run pytest`.
- Run linting with `uv run ruff check .`.
- Run typing checks with `uv run mypy src`.
- Source code lives in `src/colacloud`; tests live in `tests`.

## API Work

- Unit tests should mock HTTP calls rather than hitting production services.
- Smoke tests may require `COLA_API_KEY`; do not hardcode API keys or tokens.
- Avoid accidental public API breaks. If a breaking change is intentional, make it explicit in the versioning/release notes.
