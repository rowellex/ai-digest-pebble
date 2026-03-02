from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Text,
    DateTime,
    Date,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    url: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(30), default="rss")
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    active: Mapped[int] = mapped_column(Integer, default=1)


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    ext_id: Mapped[str] = mapped_column(String(255), unique=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped[Source] = relationship()
    author: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(Text, default="")
    text_content: Mapped[str] = mapped_column(Text)
    link: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    has_video: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Enrichment(Base):
    __tablename__ = "enrichment"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    tags: Mapped[str] = mapped_column(Text, default="")
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    novelty_score: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[float] = mapped_column(Float, default=0.0)
    summary_short: Mapped[str] = mapped_column(Text, default="")
    summary_long: Mapped[str] = mapped_column(Text, default="")


class VideoChapter(Base):
    __tablename__ = "video_chapters"
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    start_sec: Mapped[int] = mapped_column(Integer)
    end_sec: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(Text)


class DailyDigest(Base):
    __tablename__ = "daily_digest"
    __table_args__ = (UniqueConstraint("digest_date", "rank", name="uq_digest_rank"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    digest_date: Mapped[date] = mapped_column(Date)
    rank: Mapped[int] = mapped_column(Integer)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    score: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text, default="")


def make_engine(db_url: str):
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, connect_args=connect_args)


def make_session(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
