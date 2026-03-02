#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, datetime

from ai_signal_hub.config import settings
from ai_signal_hub.models import Base, make_engine, make_session
from ai_signal_hub.ingest import load_sources, sync_sources, ingest_all
from ai_signal_hub.ranking import rank_for_day
from ai_signal_hub.web import create_app


def cmd_init_db(args):
    engine = make_engine(settings.db_url)
    Base.metadata.create_all(engine)
    Session = make_session(engine)
    s = Session()
    cfg = load_sources(args.sources)
    sync_sources(s, cfg)
    print("db initialized")


def cmd_ingest(args):
    engine = make_engine(settings.db_url)
    Session = make_session(engine)
    s = Session()
    n = ingest_all(s)
    print(f"ingested {n} new posts")


def cmd_rank(args):
    engine = make_engine(settings.db_url)
    Session = make_session(engine)
    s = Session()
    d = date.today() if args.date == "today" else datetime.strptime(args.date, "%Y-%m-%d").date()
    n = rank_for_day(s, d)
    print(f"ranked {n} posts for {d}")


def cmd_runserver(args):
    app = create_app()
    app.run(host=settings.host, port=settings.port, debug=False)


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(required=True)

    p0 = sp.add_parser("init-db")
    p0.add_argument("--sources", default="config/sources.yaml")
    p0.set_defaults(func=cmd_init_db)

    p1 = sp.add_parser("ingest")
    p1.set_defaults(func=cmd_ingest)

    p2 = sp.add_parser("rank")
    p2.add_argument("--date", default="today")
    p2.set_defaults(func=cmd_rank)

    p3 = sp.add_parser("runserver")
    p3.set_defaults(func=cmd_runserver)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
