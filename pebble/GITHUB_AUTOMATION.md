# GitHub Automation Setup (Pebble)

This repo now includes a GitHub Actions workflow that automatically:

1. Packages `pebble/` into `pebble-ai-digest-project.zip`
2. Uploads the ZIP as a workflow artifact on every push
3. Attaches the ZIP to GitHub Releases when you publish a release tag

## What this gives you
- I can keep updating the Pebble app code in git
- You can always download a fresh import ZIP from Actions/Release
- You only do the account-bound store actions (upload/publish)

## One-time setup
1. Create a GitHub repo and push this workspace.
2. In GitHub repo settings, ensure Actions are enabled.
3. (Optional) Create a release tag (e.g. `v1.0.1`) to auto-attach ZIP.

## Where to download
- **Actions run artifact**: `pebble-import-zip`
- **Release asset**: `pebble-ai-digest-project.zip`

## Store upload path
- Import ZIP into CloudPebble (`Import Existing Project -> Upload Zip`)
- Build `.pbw` in CloudPebble
- Upload `.pbw` + screenshots in app store form
- Publish

## Note on `.pbw` in CI
The legacy Pebble SDK is not reliably available on modern GitHub runners, so CI packages the import ZIP (reliable) and CloudPebble handles final `.pbw` build.
