# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See the root `../CLAUDE.md` for full documentation. Key points for this subproject:

## Setup & Running

```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # testing
python app.py                        # dev server on http://127.0.0.1:5000
```

## Testing

```bash
pytest                               # all tests
pytest tests/unit/                   # fast, mocked (no API key needed)
pytest tests/regression/             # real API calls (requires ANTHROPIC_API_KEY)
pytest tests/unit/test_parser.py::test_get_extension_jpg  # single test
```

## Stack

Python 3.14, Flask 3.1 (Django>=5.0 noted as future target), Anthropic SDK, Gunicorn (production), pytest + pytest-mock + pytest-cov (testing).

## Architecture

`app.py` (factory) → `scanning_app/routes.py` (HTTP, blueprint) → `scanning_app/parser.py` (Claude API) with config in `scanning_app/config.py` (Claude model, system prompt, allowed file types).
