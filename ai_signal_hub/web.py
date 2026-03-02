from __future__ import annotations

from datetime import date
from flask import Flask, jsonify, render_template, request

from .config import settings
from .models import make_engine, make_session, Base, DailyDigest, Post, Enrichment, VideoChapter


def create_app():
    app = Flask(__name__)
    engine = make_engine(settings.db_url)
    Session = make_session(engine)

    @app.get("/")
    def index():
        d = request.args.get("date") or str(date.today())
        s = Session()
        rows = (
            s.query(DailyDigest, Post, Enrichment)
            .join(Post, DailyDigest.post_id == Post.id)
            .outerjoin(Enrichment, Enrichment.post_id == Post.id)
            .filter(DailyDigest.digest_date == d)
            .order_by(DailyDigest.rank.asc())
            .all()
        )
        return render_template("index.html", rows=rows, day=d)

    @app.get("/api/digest/<day>")
    def api_digest(day):
        s = Session()
        rows = (
            s.query(DailyDigest, Post, Enrichment)
            .join(Post, DailyDigest.post_id == Post.id)
            .outerjoin(Enrichment, Enrichment.post_id == Post.id)
            .filter(DailyDigest.digest_date == day)
            .order_by(DailyDigest.rank.asc())
            .all()
        )
        out = []
        for d, p, e in rows:
            chapters = s.query(VideoChapter).filter(VideoChapter.post_id == p.id).order_by(VideoChapter.start_sec.asc()).all()
            out.append({
                "rank": d.rank,
                "score": d.score,
                "reason": d.reason,
                "title": p.title,
                "summary": (e.summary_long if e else p.text_content),
                "short": (e.summary_short if e else p.title),
                "tags": (e.tags.split(",") if e and e.tags else []),
                "link": p.link,
                "has_video": bool(p.has_video),
                "chapters": [{"start_sec": c.start_sec, "end_sec": c.end_sec, "label": c.label} for c in chapters],
            })
        return jsonify({"date": day, "items": out})

    @app.get("/api/pebble/<day>")
    def api_pebble(day):
        s = Session()
        rows = (
            s.query(DailyDigest, Post, Enrichment)
            .join(Post, DailyDigest.post_id == Post.id)
            .outerjoin(Enrichment, Enrichment.post_id == Post.id)
            .filter(DailyDigest.digest_date == day)
            .order_by(DailyDigest.rank.asc())
            .limit(15)
            .all()
        )
        return jsonify([
            {
                "t": f"#{d.rank} {((e.summary_short if e else p.title) or '')[:60]}",
                "u": p.link,
                "v": bool(p.has_video),
            }
            for d, p, e in rows
        ])

    @app.get("/health")
    def health():
        return {"ok": True}

    return app
