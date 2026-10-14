"""Unit tests cho các Domain Entities thuần Python (Dùng unittest tiêu chuẩn)."""

import unittest
from datetime import datetime, timezone
from steam_reviews.domain.entities.game import GameSummary, LanguageMetric, PlaytimeMetric
from steam_reviews.domain.entities.review import AuthorInfo, Review, ReviewEngagement
from steam_reviews.domain.entities.run_metadata import RunMetadata


class TestDomainEntities(unittest.TestCase):
    def test_review_entity_creation_and_properties(self):
        author = AuthorInfo(
            steamid="76561198000000000",
            num_games_owned=15,
            num_reviews=3,
            playtime_forever_minutes=1500.0,
            playtime_at_review_minutes=1200.0,
        )
        engagement = ReviewEngagement(
            votes_helpful=10,
            votes_funny=2,
            weighted_vote_score=0.85,
            comment_count=1,
        )
        now = datetime.now(timezone.utc)
        review = Review(
            review_id=85184605,
            app_id=292030,
            app_name="The Witcher 3: Wild Hunt",
            language="english",
            review_text="One of the best RPGs of all time!",
            created_at=now,
            updated_at=now,
            recommended=True,
            author=author,
            engagement=engagement,
        )

        self.assertTrue(review.is_positive())
        self.assertTrue(review.has_content())
        self.assertEqual(review.label, 1.0)
        self.assertEqual(review.author.playtime_forever_minutes, 1500.0)
        self.assertEqual(review.engagement.votes_helpful, 10)

    def test_review_negative_and_empty_content(self):
        now = datetime.now(timezone.utc)
        review = Review(
            review_id=85184606,
            app_id=292030,
            app_name="The Witcher 3: Wild Hunt",
            language="english",
            review_text="",
            created_at=now,
            updated_at=now,
            recommended=False,
            author=AuthorInfo(),
            engagement=ReviewEngagement(),
        )

        self.assertFalse(review.is_positive())
        self.assertFalse(review.has_content())
        self.assertEqual(review.label, 0.0)

    def test_game_summary_entity(self):
        summary = GameSummary(
            app_id=292030,
            app_name="The Witcher 3: Wild Hunt",
            total_reviews=10000,
            recommended_count=9710,
            not_recommended_count=290,
            recommendation_rate=0.971,
            avg_playtime_hours=45.5,
            median_playtime_hours=32.0,
        )
        self.assertEqual(summary.total_reviews, 10000)
        self.assertEqual(summary.recommendation_rate, 0.971)

    def test_run_metadata_entity(self):
        meta = RunMetadata(
            run_id="run_20261010_001",
            dataset_version="v1.0",
            tier="core",
            total_records_read=1000000,
            valid_records_count=995000,
            created_at=datetime.now(timezone.utc),
        )
        self.assertEqual(meta.tier, "core")
        self.assertEqual(meta.total_records_read, 1000000)


if __name__ == "__main__":
    unittest.main()
