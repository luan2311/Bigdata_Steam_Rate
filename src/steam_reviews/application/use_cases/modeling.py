"""PrepareModelData, TrainRecommendationModel and EvaluateRecommendationModel.

Selection uses validation macro-F1 only. The test split is touched once, by
EvaluateRecommendationModel, after a model has been selected.
"""

from __future__ import annotations

from steam_reviews.application.dto.modeling import (
    BASELINE_NAME,
    EvaluateResult,
    SplitRequest,
    SplitSummary,
    TrainRequest,
    TrainResult,
)
from steam_reviews.application.ports.processing import ModelTrainer, RunRecorder
from steam_reviews.application.use_cases.run_state import to_payload
from steam_reviews.domain.policies.split import Split

MAX_CONFIGS = 4


class LeakageError(RuntimeError):
    """Train, validation and test share a review id or a text hash."""


class PrepareModelData:
    def __init__(self, trainer: ModelTrainer, recorder: RunRecorder) -> None:
        self._trainer = trainer
        self._recorder = recorder

    def execute(self, request: SplitRequest) -> SplitSummary:
        summary = self._trainer.prepare_splits(request)
        self._recorder.save(request.run_id, "split_manifest",
                            {"policy": to_payload(request.policy), "max_rows": request.max_rows,
                             "summary": to_payload(summary)})
        overlaps = {pair: n for pair, n in summary.leakage.items() if n}
        if overlaps:
            raise LeakageError(f"split overlap detected: {overlaps}")
        return summary


class TrainRecommendationModel:
    def __init__(self, trainer: ModelTrainer, recorder: RunRecorder) -> None:
        self._trainer = trainer
        self._recorder = recorder

    def execute(self, request: TrainRequest) -> TrainResult:
        if not 1 <= len(request.configs) <= MAX_CONFIGS:
            raise ValueError(f"run between 1 and {MAX_CONFIGS} configurations")
        names = [c.name for c in request.configs]
        if len(set(names)) != len(names) or BASELINE_NAME in names:
            raise ValueError("configuration names must be unique and not the baseline name")

        majority = self._trainer.majority_label(request.splits)
        baseline = self._trainer.score_baseline(request.splits, majority, Split.VALIDATION)

        fitted, validation = {}, {}
        for config in request.configs:
            model = self._trainer.fit(request.splits, config, request.models_uri)
            fitted[config.name] = model
            validation[config.name] = self._trainer.score(model, request.splits, Split.VALIDATION)
            self._recorder.save(request.run_id, f"validation_{config.name}",
                                {"config": to_payload(config), "metrics": to_payload(validation[config.name])})

        best = max(names, key=lambda n: (validation[n].macro_f1, -names.index(n)))
        result = TrainResult(request.run_id, baseline, validation, fitted[best], majority)
        self._recorder.save(request.run_id, "model_selection", to_payload(result))
        return result


class EvaluateRecommendationModel:
    def __init__(self, trainer: ModelTrainer, recorder: RunRecorder) -> None:
        self._trainer = trainer
        self._recorder = recorder

    def execute(self, splits: SplitSummary, trained: TrainResult, error_examples: int = 30) -> EvaluateResult:
        baseline = self._trainer.score_baseline(splits, trained.majority_label, Split.TEST)
        model = self._trainer.score(trained.selected, splits, Split.TEST)
        errors = self._trainer.error_examples(trained.selected, splits, Split.TEST, error_examples)
        errors_uri = self._recorder.save(trained.run_id, "test_error_examples", {"examples": errors})
        result = EvaluateResult(trained.run_id, baseline, model, errors_uri)
        self._recorder.save(trained.run_id, "test_metrics",
                            {"selected_config": to_payload(trained.selected.config),
                             "model_uri": trained.selected.model_uri, "result": to_payload(result)})
        return result
