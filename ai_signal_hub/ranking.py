from __future__ import annotations

from datetime import date, datetime
from collections import Counter

from .models import Post, Enrichment, DailyDigest, Source, VideoChapter

KEYWORDS = {
    "research": ["paper", "arxiv", "study", "preprint"],
    "release": ["release", "launched", "now available", "ship"],
    "benchmark": ["benchmark", "sota", "eval", "mt-bench", "mmlu"],
    "tooling": ["github", "open source", "repo", "sdk", "framework"],
    "llm": ["llm", "transformer", "neural", "agent", "inference", "fine-tune"],
}


def _score_text(text: str):
    low = (text or "").lower()
    tags = []
    points = 0
    for tag, kws in KEYWORDS.items():
        hit = sum(1 for kw in kws if kw in low)
        if hit:
            tags.append(tag)
            points += hit
    return tags, float(points)


def summarize(text: str, limit=180):
    t = " ".join((text or "").split())
    return t[: limit - 1] + "…" if len(t) > limit else t


def chapterize(post: Post):
    # Free fallback: heuristic chapter marks based on sentence positions
    text = post.text_content or ""
    chunks = [c.strip() for c in text.split(".") if c.strip()][:4]
    out = []
    for i, c in enumerate(chunks):
        out.append((i * 45, i * 45 + 45, summarize(c, 70)))
    return out


def rank_for_day(session, target: date):
    session.query(DailyDigest).filter(DailyDigest.digest_date == target).delete()
    rows = (
        session.query(Post, Source)
        .join(Source, Source.id == Post.source_id)
        .filter(Post.published_at >= datetime.combine(target, datetime.min.time()))
        .filter(Post.published_at < datetime.combine(target, datetime.max.time()))
        .all()
    )

    scored = []
    for post, source in rows:
        tags, rel = _score_text(f"{post.title} {post.text_content}")
        impact = (source.weight * 2.0) + (1.0 if "arxiv" in (post.link or "") else 0.0)
        novelty = 1.0
        final = 0.5 * rel + 0.35 * impact + 0.15 * novelty
        enr = session.query(Enrichment).filter_by(post_id=post.id).first() or Enrichment(post_id=post.id)
        enr.tags = ",".join(sorted(set(tags)))
        enr.relevance_score = rel
        enr.impact_score = impact
        enr.novelty_score = novelty
        enr.final_score = final
        enr.summary_short = summarize(post.title or post.text_content, 90)
        enr.summary_long = summarize(post.text_content or post.title, 300)
        session.merge(enr)

        if post.has_video:
            session.query(VideoChapter).filter_by(post_id=post.id).delete()
            for st, en, label in chapterize(post):
                session.add(VideoChapter(post_id=post.id, start_sec=st, end_sec=en, label=label))

        scored.append((final, post.id, Counter(tags).most_common(1)[0][0] if tags else "general"))

    scored.sort(reverse=True)
    for idx, (score, post_id, reason) in enumerate(scored[:15], start=1):
        session.add(DailyDigest(digest_date=target, rank=idx, post_id=post_id, score=score, reason=reason))
    session.commit()
    return len(scored[:15])
