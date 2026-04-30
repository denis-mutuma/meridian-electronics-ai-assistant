# Backend

## Local run

```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Tests

```bash
uv sync
uv run pytest -q
```
