"""End-to-end ML adapter check on a small synthetic silver table.

Text is clearly separable ("love"/"great" vs "hate"/"not"), so a working pipeline
must beat the majority baseline. Ten copies of one text test group splitting.
"""

from datetime import datetime

import pytest

from steam_reviews.application.dto.modeling import ModelConfig, SplitRequest, TrainRequest
from steam_reviews.application.use_cases.modeling import (
    EvaluateRecommendationModel,
    PrepareModelData,
    TrainRecommendationModel,
)
from steam_reviews.domain.entities.dataset import RunId
from steam_reviews.domain.policies.split import SplitPolicy
from steam_reviews.infrastructure.ml.trainer import SparkModelTrainer
from steam_reviews.infrastructure.storage.json_recorder import JsonRunRecorder

pytestmark = pytest.mark.spark

POSITIVE = ["love this game {}", "great fun {} hours", "amazing story {}", "best game {} ever"]
NEGATIVE = ["hate this game {}", "not fun {} at all", "boring and broken {}", "don't buy {}"]


@pytest.fixture
def silver_uri(spark, tmp_path):
    rows, review_id = [], 0
    for i in range(150):
        for template, label in [(POSITIVE[i % 4], True)] * 2 + [(NEGATIVE[i % 4], False)]:
            review_id += 1
            rows.append((str(review_id), "10", "english", template.format(i), False, label))
    for _ in range(10):  # identical texts must share one split
        review_id += 1
        rows.append((str(review_id), "10", "english", "Same   TEXT  everywhere", False, True))
    rows.append((str(review_id + 1), "10", "german", "sehr gut", False, True))
    rows.append((str(review_id + 2), "10", "english", "   ", True, True))
    df = spark.createDataFrame(rows, "review_id string, app_id string, language string, "
                                     "review_text string, review_text_blank boolean, recommended boolean")
    path = str(tmp_path / "silver")
    df.write.parquet(path)
    return path


def test_prepare_train_evaluate(spark, silver_uri, tmp_path):
    run = RunId("ml-test")
    trainer = SparkModelTrainer(spark)
    recorder = JsonRunRecorder(tmp_path / "metrics")

    splits = PrepareModelData(trainer, recorder).execute(
        SplitRequest(run, silver_uri, str(tmp_path / "splits"), SplitPolicy(), None))
    assert splits.excluded["non_english"] == 1
    assert splits.excluded["english_blank_or_unlabeled"] == 1
    assert sum(splits.rows.values()) == 460
    assert all(v == 0 for v in splits.leakage.values())
    same = spark.read.parquet(splits.splits_uri).where("review_text = 'Same   TEXT  everywhere'")
    assert same.select("split").distinct().count() == 1

    configs = (ModelConfig("lr_a", num_features=2**10, max_iter=20),
               ModelConfig("lr_b", num_features=2**10, max_iter=20, class_weighting=True))
    trained = TrainRecommendationModel(trainer, recorder).execute(
        TrainRequest(run, splits, str(tmp_path / "models"), configs))
    assert trained.majority_label == 1
    assert trained.validation[trained.selected.config.name].macro_f1 > trained.baseline_validation.macro_f1

    result = EvaluateRecommendationModel(trainer, recorder).execute(splits, trained, error_examples=5)
    assert result.model_test.macro_f1 > result.baseline_test.macro_f1
    assert result.baseline_test.f1[0] == 0.0
    assert result.model_test.rows == result.baseline_test.rows
    assert (tmp_path / "metrics" / "ml-test" / "test_metrics.json").exists()
