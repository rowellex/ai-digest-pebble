#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd /data/data/com.termux/files/home/.openclaw/workspace
source .venv/bin/activate
python manage.py ingest
python manage.py rank --date today
python manage.py digest --date today --out data/digest-today.txt
