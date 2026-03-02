#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd /data/data/com.termux/files/home/.openclaw/workspace

if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  exit 0
fi

source .venv/bin/activate
nohup env ASH_HOST=0.0.0.0 python manage.py runserver >> data/server.log 2>&1 &
