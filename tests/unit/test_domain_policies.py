"""Unit tests cho các Domain Policies thuần Python (kết hợp cả pytest và unittest)."""

import math
import unittest
from datetime import datetime, timezone

import pytest

from steam_reviews.domain.entities.dataset import DatasetLevel, RunId
from steam_reviews.domain.policies.labels import parse_recommended
from steam_reviews.domain.policies.metrics import (
    combined_rate,
    playtime_bucket,
    recommendation_rate,
)
from steam_reviews.domain.policies.quality import normalize_language
from steam_reviews.domain.policies.split import Split, SplitPolicy, normalize_text

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


# =====================================================================
# 1. Tests cho các policy xử lý dữ liệu lô (Huy - TV2)
# =====================================================================

@pytest.mark.parametrize(
    ("raw", "expected"),
    [("True", True), ("false", False), (" TRUE ", True), (None, None), ("", None), ("1", None), ("yes", None)],
)
def test_label_never_defaults_to_false(raw, expected):
    assert parse_recommended(raw) is expected


def test_rate_with_zero_denominator_is_none():
    assert recommendation_rate(0, 0) is None
    assert recommendation_rate(3, 4) == 0.75


def test_rate_rejects_impossible_counts():
    with pytest.raises(ValueError):
        recommendation_rate(5, 4)


def test_combined_rate_sums_before_dividing():
    # Averaging rates would give (1.0 + 0.0) / 2 = 0.5; the correct value is 1/101.
    assert combined_rate([(1, 1), (0, 100)]) == pytest.approx(1 / 101)
    assert combined_rate([]) is None


@pytest.mark.parametrize(
    ("minutes", "bucket"),
    [(0, "[0,2)"), (119.9, "[0,2)"), (120, "[2,10)"), (600, "[10,50)"), (2999, "[10,50)"),
     (3000, "[50,100)"), (6000, "[100,inf)"), (-1, "negative"), (None, "missing"), (math.nan, "missing")],
)
def test_playtime_buckets_are_half_open(minutes, bucket):
    assert playtime_bucket(minutes) == bucket


def test_language_normalization_keeps_unknown_group():
    assert normalize_language(" English ") == "english"
    assert normalize_language(None) == "unknown"
    assert normalize_language("  ") == "unknown"


def test_text_normalization_groups_whitespace_and_case():
    assert normalize_text("  Great   GAME\n10/10 ") == "great game 10/10"
    assert normalize_text(None) == ""


def test_split_policy_thresholds():
    policy = SplitPolicy()
    assert (policy.train_upper, policy.validation_upper) == (7000, 8500)
    assert policy.assign(0) is Split.TRAIN
    assert policy.assign(6999) is Split.TRAIN
    assert policy.assign(7000) is Split.VALIDATION
    assert policy.assign(8499) is Split.VALIDATION
    assert policy.assign(8500) is Split.TEST
    with pytest.raises(ValueError):
        policy.assign(10_000)


def test_split_policy_rejects_empty_test():
    with pytest.raises(ValueError):
        SplitPolicy(train_ratio=0.8, validation_ratio=0.2)


def test_run_id_is_level_and_utc_timestamp():
    run = RunId.new(DatasetLevel.SMOKE, datetime(2026, 10, 11, 8, 5, 0, tzinfo=timezone.utc))
    assert str(run) == "smoke-20261011T080500Z"


def test_binary_scores_macro_f1_is_unweighted_mean():
    from steam_reviews.domain.policies.classification import Confusion, binary_scores

    scores = binary_scores(Confusion(tp=90, fp=10, tn=0, fn=0))  # always predicts 1
    assert scores.f1[1] == pytest.approx(2 * 0.9 * 1.0 / 1.9)
    assert scores.f1[0] == 0.0
    assert scores.macro_f1 == pytest.approx(scores.f1[1] / 2)
    assert scores.accuracy == pytest.approx(0.9)


def test_class_weights_balance_classes():
    from steam_reviews.domain.policies.classification import class_weights

    weights = class_weights({1: 90, 0: 10})
    assert weights[1] * 90 == pytest.approx(weights[0] * 10)


# =====================================================================
# 2. Tests cho các policy thực thể đơn lẻ (Dev - TV1/TV2)
# =====================================================================

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
