"""Composition root: the only place that knows both use cases and adapters."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from steam_reviews.application.use_cases.modeling import (
    EvaluateRecommendationModel,
    PrepareModelData,
    TrainRecommendationModel,
)
from steam_reviews.application.use_cases.pipeline import BuildAnalytics, CleanReviews
from steam_reviews.bootstrap.config import AppConfig
from steam_reviews.infrastructure.storage.json_recorder import JsonRunRecorder


@dataclass
class Container:
    config: AppConfig

    @cached_property
    def spark(self):
        from steam_reviews.infrastructure.spark.session import SparkSettings, create_spark

        return create_spark(SparkSettings(
            master=self.config.spark_master,
            driver_memory=self.config.driver_memory,
            shuffle_partitions=self.config.shuffle_partitions,
        ))

    @cached_property
    def recorder(self) -> JsonRunRecorder:
        return JsonRunRecorder(self.config.artifacts_root / "metrics")

    @cached_property
    def _trainer(self):
        from steam_reviews.infrastructure.ml.trainer import SparkModelTrainer

        return SparkModelTrainer(self.spark)

    def clean_reviews(self) -> CleanReviews:
        from steam_reviews.infrastructure.spark.cleaning import SparkReviewCleaner

        return CleanReviews(SparkReviewCleaner(self.spark), self.recorder)

    def build_analytics(self) -> BuildAnalytics:
        from steam_reviews.infrastructure.spark.analytics import SparkAnalyticsBuilder

        return BuildAnalytics(SparkAnalyticsBuilder(self.spark), self.recorder)

    def prepare_model_data(self) -> PrepareModelData:
        return PrepareModelData(self._trainer, self.recorder)

    def train_model(self) -> TrainRecommendationModel:
        return TrainRecommendationModel(self._trainer, self.recorder)

    def evaluate_model(self) -> EvaluateRecommendationModel:
        return EvaluateRecommendationModel(self._trainer, self.recorder)

    def close(self) -> None:
        if "spark" in self.__dict__:
            self.spark.stop()
