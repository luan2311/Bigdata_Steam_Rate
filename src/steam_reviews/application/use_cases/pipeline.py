"""CleanReviews and BuildAnalytics use cases."""

from __future__ import annotations

from steam_reviews.application.dto.pipeline import (
    AnalyticsRequest,
    AnalyticsResult,
    CleanRequest,
    CleanResult,
)
from steam_reviews.application.ports.processing import (
    AnalyticsProcessor,
    ReviewBatchProcessor,
    RunRecorder,
)
from steam_reviews.application.use_cases.run_state import to_payload


class ReconciliationError(RuntimeError):
    """Counts do not add up; the run must not be handed to gold or the dashboard."""


class CleanReviews:
    def __init__(self, processor: ReviewBatchProcessor, recorder: RunRecorder) -> None:
        self._processor = processor
        self._recorder = recorder

    def execute(self, request: CleanRequest) -> CleanResult:
        result = self._processor.clean(request)
        errors = result.counts.reconciliation_errors()
        self._recorder.save(
            request.run_id,
            "quality_counts",
            {"source": to_payload(request.source), "result": to_payload(result), "errors": errors},
        )
        if errors:
            raise ReconciliationError("; ".join(errors))
        return result


class BuildAnalytics:
    def __init__(self, processor: AnalyticsProcessor, recorder: RunRecorder) -> None:
        self._processor = processor
        self._recorder = recorder

    def execute(self, request: AnalyticsRequest) -> AnalyticsResult:
        result = self._processor.build(request)
        self._recorder.save(request.run_id, "gold_summary", to_payload(result))
        if result.check_errors:
            raise ReconciliationError("; ".join(result.check_errors))
        return result
