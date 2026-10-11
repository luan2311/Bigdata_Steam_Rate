import pytest

from steam_reviews.application.dto.modeling import (
    ClassificationMetrics,
    FittedModel,
    ModelConfig,
    SplitRequest,
    SplitSummary,
    TrainRequest,
)
from steam_reviews.application.dto.pipeline import CleanRequest, CleanResult, QualityCounts
from steam_reviews.application.use_cases.modeling import (
    EvaluateRecommendationModel,
    LeakageError,
    PrepareModelData,
    TrainRecommendationModel,
)
from steam_reviews.application.use_cases.pipeline import CleanReviews, ReconciliationError
from steam_reviews.domain.entities.dataset import DatasetLevel, DatasetReference, RunId
from steam_reviews.domain.policies.split import Split, SplitPolicy

RUN = RunId("smoke-test")


class FakeRecorder:
    def __init__(self):
        self.saved = {}

    def save(self, run_id, name, payload):
        self.saved[name] = payload
        return f"mem://{run_id}/{name}"


def counts(**overrides):
    values = dict(rows_parsed=10, invalid_by_reason={"invalid_label": 2}, valid_pre_dedup=8,
                  duplicates_removed=1, silver_rows=7, blank_text=0, missing_created_at=0,
                  missing_playtime_at_review=0)
    values.update(overrides)
    return QualityCounts(**values)


class FakeProcessor:
    def __init__(self, quality):
        self.quality = quality

    def clean(self, request):
        return CleanResult(request.run_id, request.silver_uri, request.quarantine_uri, self.quality)


def clean_request():
    source = DatasetReference("file:///x.csv", "v1", DatasetLevel.SMOKE)
    return CleanRequest(source, RUN, "silver", "quarantine")


def test_clean_accepts_reconciled_counts():
    recorder = FakeRecorder()
    result = CleanReviews(FakeProcessor(counts()), recorder).execute(clean_request())
    assert result.counts.silver_rows == 7
    assert recorder.saved["quality_counts"]["errors"] == []


def test_clean_rejects_counts_that_do_not_add_up():
    recorder = FakeRecorder()
    with pytest.raises(ReconciliationError):
        CleanReviews(FakeProcessor(counts(silver_rows=8)), recorder).execute(clean_request())
    assert recorder.saved["quality_counts"]["errors"], "failed checks must still be recorded"


def metrics(model, split, macro_f1):
    return ClassificationMetrics(model, split, 10, {}, {}, {}, macro_f1, 0.0, None, {})


def summary(leakage=None):
    return SplitSummary("splits", {"train": 7}, {}, {}, leakage or {"train_test_text": 0})


class FakeTrainer:
    def __init__(self, scores, leakage=None):
        self.scores = scores
        self.leakage = leakage
        self.scored_splits = []

    def prepare_splits(self, request):
        return summary(self.leakage)

    def majority_label(self, splits):
        return 1

    def score_baseline(self, splits, label, split):
        self.scored_splits.append(("baseline", split))
        return metrics("baseline_majority", split, 0.45)

    def fit(self, splits, config, models_uri):
        return FittedModel(config, f"{models_uri}/{config.name}")

    def score(self, model, splits, split):
        self.scored_splits.append((model.config.name, split))
        return metrics(model.config.name, split, self.scores[model.config.name])

    def error_examples(self, model, splits, split, limit):
        self.scored_splits.append((f"errors:{model.config.name}", split))
        return [{"review_id": "1"}]


CONFIGS = (ModelConfig("lr_a", reg_param=0.01), ModelConfig("lr_b", reg_param=0.1),
           ModelConfig("lr_c", class_weighting=True))


def test_prepare_rejects_leakage():
    trainer = FakeTrainer({}, leakage={"train_test_text": 3})
    request = SplitRequest(RUN, "silver", "splits", SplitPolicy(), 1000)
    with pytest.raises(LeakageError):
        PrepareModelData(trainer, FakeRecorder()).execute(request)


def test_training_selects_by_validation_and_never_scores_test():
    trainer = FakeTrainer({"lr_a": 0.70, "lr_b": 0.80, "lr_c": 0.75})
    result = TrainRecommendationModel(trainer, FakeRecorder()).execute(
        TrainRequest(RUN, summary(), "models", CONFIGS))
    assert result.selected.config.name == "lr_b"
    assert all(split is Split.VALIDATION for _, split in trainer.scored_splits)


def test_training_tie_keeps_first_config():
    trainer = FakeTrainer({"lr_a": 0.8, "lr_b": 0.8, "lr_c": 0.1})
    result = TrainRecommendationModel(trainer, FakeRecorder()).execute(
        TrainRequest(RUN, summary(), "models", CONFIGS))
    assert result.selected.config.name == "lr_a"


def test_training_limits_number_of_configs():
    five = tuple(ModelConfig(f"lr_{i}") for i in range(5))
    with pytest.raises(ValueError):
        TrainRecommendationModel(FakeTrainer({}), FakeRecorder()).execute(
            TrainRequest(RUN, summary(), "models", five))


def test_evaluation_scores_baseline_and_selected_on_test():
    trainer = FakeTrainer({"lr_a": 0.7, "lr_b": 0.9, "lr_c": 0.8})
    recorder = FakeRecorder()
    trained = TrainRecommendationModel(trainer, recorder).execute(
        TrainRequest(RUN, summary(), "models", CONFIGS))
    trainer.scored_splits.clear()
    result = EvaluateRecommendationModel(trainer, recorder).execute(summary(), trained)
    assert trainer.scored_splits == [("baseline", Split.TEST), ("lr_b", Split.TEST),
                                     ("errors:lr_b", Split.TEST)]
    assert recorder.saved["test_error_examples"]["examples"] == [{"review_id": "1"}]
    assert result.model_test.model == "lr_b"
    assert recorder.saved["test_metrics"]["selected_config"]["name"] == "lr_b"
