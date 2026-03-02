from __future__ import annotations

import hashlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import yaml
from bs4 import BeautifulSoup

from .models import Source, Post


def _text(el, tag):
    node = el.find(tag)
    return node.text.strip() if node is not None and node.text else ""


def load_sources(path: str):
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    return doc.get("sources", [])


def sync_sources(session, sources_cfg):
    existing = {s.name: s for s in session.query(Source).all()}
    for item in sources_cfg:
        s = existing.get(item["name"])
        if s:
            s.url = item["url"]
            s.weight = float(item.get("weight", 1.0))
            s.active = 1 if item.get("active", True) else 0
            s.kind = item.get("kind", "rss")
        else:
            session.add(Source(
                name=item["name"], url=item["url"], weight=float(item.get("weight", 1.0)),
                active=1 if item.get("active", True) else 0, kind=item.get("kind", "rss")
            ))
    session.commit()


def parse_rss(url: str):
    with urllib.request.urlopen(url, timeout=30) as resp:
        xml_data = resp.read()
    root = ET.fromstring(xml_data)
    items = root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry")
    out = []
    for it in items:
        title = _text(it, "title") or _text(it, "{http://www.w3.org/2005/Atom}title")
        desc = _text(it, "description") or _text(it, "summary") or _text(it, "{http://www.w3.org/2005/Atom}summary")
        link = _text(it, "link")
        if not link:
            ln = it.find("{http://www.w3.org/2005/Atom}link")
            if ln is not None:
                link = ln.attrib.get("href", "")
        pub = _text(it, "pubDate") or _text(it, "published") or _text(it, "{http://www.w3.org/2005/Atom}published")
        try:
            dt = parsedate_to_datetime(pub) if pub else datetime.now(timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        author = _text(it, "author") or _text(it, "{http://www.w3.org/2005/Atom}author")
        txt = BeautifulSoup(desc, "html.parser").get_text(" ", strip=True)
        out.append({"title": title, "text": txt, "link": link, "published": dt, "author": author})
    return out


def ingest_all(session):
    sources = session.query(Source).filter(Source.active == 1).all()
    inserted = 0
    for source in sources:
        if source.kind != "rss":
            continue
        try:
            entries = parse_rss(source.url)
        except Exception:
            continue
        for e in entries:
            ext_id = hashlib.sha1((source.name + "|" + (e["link"] or e["title"])) .encode()).hexdigest()
            if session.query(Post).filter_by(ext_id=ext_id).first():
                continue
            has_video = 1 if any(v in (e["text"] + " " + e["link"]).lower() for v in ["youtu", "video", "mp4", "x.com/i/status"] ) else 0
            session.add(Post(
                ext_id=ext_id,
                source_id=source.id,
                author=e["author"] or source.name,
                title=e["title"],
                text_content=e["text"],
                link=e["link"],
                published_at=e["published"].replace(tzinfo=None),
                has_video=has_video,
            ))
            inserted += 1
    session.commit()
    return inserted
