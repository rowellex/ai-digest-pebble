# AI Signal Feed (Free-first)

Builds a daily **Top 15 AI/X signals** feed from public sources, stores forever, and serves:
- Responsive web UI (phone + desktop)
- JSON APIs
- Pebble-optimized endpoint

## Why this design
Official X APIs are frequently paid/restricted. This project is designed to run free by ingesting public RSS/Atom sources (e.g., list mirrors, curated feeds), then ranking + summarizing locally.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py init-db
python manage.py ingest
python manage.py rank --date today
python manage.py runserver
```

Open: `http://127.0.0.1:8000`

## Project layout

- `ai_signal_hub/` app package
- `config/sources.yaml` feed sources to ingest
- `pebble/` Pebble watchapp skeleton consuming compact API
- `tests/` integration and ranking tests

## Scheduling (free)
Use cron/termux-job-scheduler:
- ingest every 30 min
- rank daily at 23:58 local

## Notes
- Video chaptering is optional and degrades gracefully if transcript tooling is unavailable.
- Data is SQLite by default for zero-cost local operation.
