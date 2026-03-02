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
- rank + digest daily at 8:00 local (or your preferred time)

Example cron lines:

```cron
*/30 * * * * cd /data/data/com.termux/files/home/.openclaw/workspace && . .venv/bin/activate && python manage.py ingest >> data/cron.log 2>&1
0 8 * * * cd /data/data/com.termux/files/home/.openclaw/workspace && . .venv/bin/activate && python manage.py rank --date today && python manage.py digest --date today --out data/digest-today.txt >> data/cron.log 2>&1
```

## Run + view

```bash
cd /data/data/com.termux/files/home/.openclaw/workspace
source .venv/bin/activate
python manage.py runserver
```

View in browser:
- Phone (same network): `http://<computer-ip>:8000`
- Local device/browser: `http://127.0.0.1:8000`
- JSON API: `/api/digest/YYYY-MM-DD`
- Pebble compact API: `/api/pebble/YYYY-MM-DD`

## Notes
- Video chaptering is optional and degrades gracefully if transcript tooling is unavailable.
- Data is SQLite by default for zero-cost local operation.
