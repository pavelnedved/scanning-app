# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Early-stage Python Flask web application. The project comments in `requirements.txt` suggest Django is the intended framework when network access is available; Flask is currently used as a lightweight alternative.

## Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

The server starts on `http://127.0.0.1:5000` by default.

## Tech Stack

- Python 3.14.3
- Flask 3.1.2 (current; Django>=5.0 is the planned framework)

## Architecture

Single-file application (`app.py`) with one route. No database, templates, or static files yet.