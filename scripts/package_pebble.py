#!/usr/bin/env python3
from __future__ import annotations
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
OUT.mkdir(exist_ok=True)

src_dir = ROOT / "pebble"
zip_path = OUT / "pebble-ai-digest-project.zip"

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in src_dir.rglob("*"):
        if p.is_file():
            zf.write(p, p.relative_to(ROOT))

print(zip_path)
