# Publish Checklist (Pebble/Rebble)

## 0) Pre-flight (already prepared)
- App source in `pebble/`
- Import bundle: `pebble-ai-digest-project.tar.gz`
- Listing copy: `pebble/STORE_LISTING.md`
- Privacy policy draft: `pebble/PRIVACY.md`

## 1) Build final package (.pbw)
In CloudPebble/Rebble IDE:
1. Import project files from `pebble/`
2. Set `SERVER` in `src/pkjs/index.js`
3. Build for target platform(s)
4. Download generated `.pbw`

## 2) Prepare store assets
Minimum recommended:
- App icon (48x48 and 144x144)
- 3–5 screenshots (watch display)
- Optional banner/hero image

## 3) Listing fields
Use content from `STORE_LISTING.md`:
- Name
- Short description
- Full description
- Category/tags
- Support URL
- Privacy policy URL
- Release notes

## 4) Final 2–3 clicks to publish
After upload + metadata are filled:
1. **Save Draft**
2. **Submit for Review** (or Publish, depending on portal flow)
3. **Confirm** final dialog

---

## Quick sanity checks before clicking publish
- `.pbw` installs and launches on your watch
- App loads at least 1 item from `/api/pebble/<today>`
- Selecting an item opens link on phone
