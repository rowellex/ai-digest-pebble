# Pebble AI Digest App

This app shows the daily Top 15 AI items from your backend.

## What it does
- Loads compact feed from `GET /api/pebble/YYYY-MM-DD`
- Displays ranked items on the watch
- On select, opens link on phone

## Configure
Edit `src/pkjs/index.js`:
```js
var SERVER = 'http://YOUR_SERVER:8000';
```
Use your server LAN IP so your phone can reach it.

## Build/install options

### Option A: CloudPebble/Rebble web IDE (recommended)
1. Create/import project with files from this `pebble/` folder.
2. Build for your watch platform.
3. Install to connected watch.

### Option B: Local Pebble SDK (if installed)
```bash
cd pebble
pebble build
pebble install --phone <PHONE_IP>
```

## Test backend first
```bash
curl http://<SERVER_IP>:8000/api/pebble/2026-03-01
```
Should return JSON list of items.
