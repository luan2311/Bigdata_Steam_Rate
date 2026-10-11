import math
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
