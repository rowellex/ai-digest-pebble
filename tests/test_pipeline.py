import unittest
from datetime import datetime, date

from ai_signal_hub.models import Base, make_engine, make_session, Source, Post
from ai_signal_hub.ranking import rank_for_day


class PipelineTest(unittest.TestCase):
    def test_rank_top15(self):
        engine = make_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = make_session(engine)
        s = Session()

        src = Source(name="src", url="http://example.com", kind="rss", weight=1.0, active=1)
        s.add(src)
        s.commit()

        for i in range(20):
            s.add(Post(
                ext_id=f"id-{i}", source_id=src.id, author="a", title=f"LLM release {i}",
                text_content="New benchmark and arxiv paper release", link=f"http://x/{i}",
                published_at=datetime(2026, 3, 1, 10, 0, 0), has_video=0
            ))
        s.commit()

        n = rank_for_day(s, date(2026, 3, 1))
        self.assertEqual(n, 15)


if __name__ == "__main__":
    unittest.main()
