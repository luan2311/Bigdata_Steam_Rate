"""Unit tests cho các Domain Policies thuần Python (Dùng unittest tiêu chuẩn)."""

import unittest
from steam_reviews.domain.policies.cleaning_policy import (
    clean_review_text,
    is_review_eligible_for_ml,
    is_valid_app_id,
    is_valid_review_id,
)
from steam_reviews.domain.policies.playtime_policy import (
    BUCKET_LESS_THAN_2H,
    BUCKET_2H_TO_10H,
    BUCKET_10H_TO_50H,
    BUCKET_50H_TO_100H,
    BUCKET_MORE_THAN_100H,
    BUCKET_UNKNOWN,
    categorize_playtime_bucket,
    get_playtime_bucket_order,
    minutes_to_hours,
)
from steam_reviews.domain.policies.recommendation_policy import (
    aggregate_recommendation_rate,
    label_to_numeric,
    parse_recommended_label,
    safe_recommendation_rate,
)


class TestRecommendationPolicy(unittest.TestCase):
    def test_safe_recommendation_rate_normal(self):
        self.assertEqual(safe_recommendation_rate(80, 100), 0.8)
        self.assertEqual(safe_recommendation_rate(9710, 10000), 0.971)
        self.assertEqual(safe_recommendation_rate(0, 50), 0.0)

    def test_safe_recommendation_rate_zero_denominator(self):
        self.assertIsNone(safe_recommendation_rate(0, 0))
        self.assertIsNone(safe_recommendation_rate(10, 0))
        self.assertIsNone(safe_recommendation_rate(5, -1))

    def test_safe_recommendation_rate_bounds(self):
        self.assertEqual(safe_recommendation_rate(-5, 100), 0.0)
        self.assertEqual(safe_recommendation_rate(150, 100), 1.0)

    def test_parse_recommended_label_positive(self):
        self.assertTrue(parse_recommended_label(True))
        self.assertTrue(parse_recommended_label("True"))
        self.assertTrue(parse_recommended_label("true"))
        self.assertTrue(parse_recommended_label("1"))
        self.assertTrue(parse_recommended_label(1))

    def test_parse_recommended_label_negative(self):
        self.assertFalse(parse_recommended_label(False))
        self.assertFalse(parse_recommended_label("False"))
        self.assertFalse(parse_recommended_label("false"))
        self.assertFalse(parse_recommended_label("0"))
        self.assertFalse(parse_recommended_label(0))

    def test_parse_recommended_label_invalid(self):
        with self.assertRaises(ValueError):
            parse_recommended_label("invalid_label")

    def test_label_to_numeric(self):
        self.assertEqual(label_to_numeric(True), 1.0)
        self.assertEqual(label_to_numeric(False), 0.0)

    def test_aggregate_recommendation_rate(self):
        batches = [(90, 100), (80, 100), (0, 0)]
        self.assertEqual(aggregate_recommendation_rate(batches), 0.85)
        self.assertIsNone(aggregate_recommendation_rate([]))


class TestCleaningPolicy(unittest.TestCase):
    def test_is_valid_review_id(self):
        self.assertTrue(is_valid_review_id(85185598))
        self.assertTrue(is_valid_review_id("85185598"))
        self.assertFalse(is_valid_review_id(0))
        self.assertFalse(is_valid_review_id(-1))
        self.assertFalse(is_valid_review_id("abc"))
        self.assertFalse(is_valid_review_id(None))

    def test_is_valid_app_id(self):
        self.assertTrue(is_valid_app_id(292030))
        self.assertTrue(is_valid_app_id("292030"))
        self.assertFalse(is_valid_app_id(-5))
        self.assertFalse(is_valid_app_id(None))

    def test_clean_review_text(self):
        self.assertEqual(clean_review_text("  Great   game!  "), "Great game!")
        self.assertEqual(clean_review_text("Bad\x00game"), "Badgame")
        self.assertIsNone(clean_review_text(""))
        self.assertIsNone(clean_review_text("   "))
        self.assertIsNone(clean_review_text(None))

    def test_is_review_eligible_for_ml(self):
        self.assertTrue(is_review_eligible_for_ml("Awesome RPG masterpiece!", "english"))
        self.assertFalse(is_review_eligible_for_ml("Good", "english", min_length=5))
        self.assertFalse(is_review_eligible_for_ml("Tuyệt vời", "schinese"))
        self.assertFalse(is_review_eligible_for_ml(None, "english"))
        self.assertFalse(is_review_eligible_for_ml("   ", "english"))


class TestPlaytimePolicy(unittest.TestCase):
    def test_categorize_playtime_bucket(self):
        self.assertEqual(categorize_playtime_bucket(50.0), BUCKET_LESS_THAN_2H)
        self.assertEqual(categorize_playtime_bucket(119.9), BUCKET_LESS_THAN_2H)
        self.assertEqual(categorize_playtime_bucket(120.0), BUCKET_2H_TO_10H)
        self.assertEqual(categorize_playtime_bucket(300.0), BUCKET_2H_TO_10H)
        self.assertEqual(categorize_playtime_bucket(1200.0), BUCKET_10H_TO_50H)
        self.assertEqual(categorize_playtime_bucket(4500.0), BUCKET_50H_TO_100H)
        self.assertEqual(categorize_playtime_bucket(8000.0), BUCKET_MORE_THAN_100H)
        self.assertEqual(categorize_playtime_bucket(None), BUCKET_UNKNOWN)
        self.assertEqual(categorize_playtime_bucket(-10.0), BUCKET_UNKNOWN)

    def test_bucket_order(self):
        self.assertEqual(get_playtime_bucket_order(BUCKET_LESS_THAN_2H), 1)
        self.assertEqual(get_playtime_bucket_order(BUCKET_2H_TO_10H), 2)
        self.assertEqual(get_playtime_bucket_order(BUCKET_MORE_THAN_100H), 5)
        self.assertEqual(get_playtime_bucket_order("unknown"), 6)

    def test_minutes_to_hours(self):
        self.assertEqual(minutes_to_hours(120.0), 2.0)
        self.assertEqual(minutes_to_hours(90.0), 1.5)
        self.assertIsNone(minutes_to_hours(None))
        self.assertIsNone(minutes_to_hours(-50.0))


if __name__ == "__main__":
    unittest.main()
