"""Spark MLlib adapter for ModelTrainer.

Pipeline: RegexTokenizer -> StopWordsRemover (negations kept) -> HashingTF -> IDF
-> LogisticRegression. Only `review_text` is a feature. IDF and the classifier are
fit on the train split; validation/test are only transformed.
"""

from __future__ import annotations

from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import IDF, HashingTF, RegexTokenizer, StopWordsRemover
from pyspark.ml.functions import vector_to_array
from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F

from steam_reviews.application.dto.modeling import (
    BASELINE_NAME,
    ClassificationMetrics,
    FittedModel,
    ModelConfig,
    SplitRequest,
    SplitSummary,
)
from steam_reviews.domain.policies.classification import Confusion, binary_scores, class_weights
from steam_reviews.domain.policies.split import ML_LANGUAGE, Split, SplitPolicy

NEGATIONS = {
    "no", "nor", "not", "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't",
    "won't", "wouldn't", "can't", "cannot", "couldn't", "shouldn't", "haven't", "hasn't",
    "hadn't", "mustn't", "needn't", "shan't", "ain't", "mightn't",
}
TOKEN_PATTERN = r"[^\p{L}\p{N}']+"  # split on anything except letters, digits and apostrophes


def normalized_text(column: str) -> Column:
    """Spark twin of domain.policies.split.normalize_text."""
    return F.lower(F.trim(F.regexp_replace(F.col(column), r"(?U)\s+", " ")))


def _bucket(value: Column, seed: str, buckets: int) -> Column:
    return F.pmod(F.xxhash64(F.lit(seed), value), F.lit(buckets))


def _split_column(policy: SplitPolicy) -> Column:
    bucket = F.col("split_bucket")
    return (F.when(bucket < policy.train_upper, Split.TRAIN.value)
            .when(bucket < policy.validation_upper, Split.VALIDATION.value)
            .otherwise(Split.TEST.value))


def _to_metrics(model: str, split: Split, predictions: DataFrame, score_column: str | None) -> ClassificationMetrics:
    cells = {(r["label"], r["prediction"]): r["count"]
             for r in predictions.groupBy("label", "prediction").count().collect()}
    confusion = Confusion(tp=cells.get((1, 1.0), 0), fp=cells.get((0, 1.0), 0),
                          tn=cells.get((0, 0.0), 0), fn=cells.get((1, 0.0), 0))
    scores = binary_scores(confusion)
    pr_auc = None
    if score_column and confusion.tp + confusion.fn and confusion.tn + confusion.fp:
        pr_auc = BinaryClassificationEvaluator(
            labelCol="label", rawPredictionCol=score_column, metricName="areaUnderPR"
        ).evaluate(predictions)
    return ClassificationMetrics(
        model=model, split=split, rows=confusion.total, precision=scores.precision,
        recall=scores.recall, f1=scores.f1, macro_f1=scores.macro_f1, accuracy=scores.accuracy,
        pr_auc_positive=pr_auc,
        confusion={"tp": confusion.tp, "fp": confusion.fp, "tn": confusion.tn, "fn": confusion.fn},
    )


class SparkModelTrainer:
    def __init__(self, spark: SparkSession) -> None:
        self._spark = spark

    def _split(self, splits: SplitSummary, split: Split) -> DataFrame:
        return self._spark.read.parquet(splits.splits_uri).where(F.col("split") == split.value)

    def prepare_splits(self, request: SplitRequest) -> SplitSummary:
        policy = request.policy
        silver = self._spark.read.parquet(request.silver_uri)
        english = silver.where(F.col("language") == ML_LANGUAGE)
        scoped = english.where(~F.col("review_text_blank") & F.col("recommended").isNotNull())
        excluded = {"silver_rows": silver.count(), "non_english": silver.count() - english.count(),
                    "english_blank_or_unlabeled": english.count() - scoped.count()}

        data = (scoped.select("review_id", "app_id", "review_text",
                              F.col("recommended").cast("int").alias("label"))
                .withColumn("text_norm", normalized_text("review_text"))
                .withColumn("text_hash", F.xxhash64(F.lit(policy.seed), F.col("text_norm")))
                .withColumn("split_bucket", _bucket(F.col("text_norm"), policy.seed, policy.buckets)))
        if request.max_rows:
            # Deterministic cap: keep the max_rows reviews with the smallest id hash.
            data = (data.withColumn("_order", F.xxhash64(F.lit(policy.seed + "-cap"), F.col("review_id")))
                    .orderBy("_order", "review_id").limit(request.max_rows).drop("_order"))
        data = data.withColumn("split", _split_column(policy)).drop("text_norm")
        data.repartition(8).write.mode("overwrite").parquet(request.splits_uri)

        written = self._spark.read.parquet(request.splits_uri)
        excluded["capped_out"] = scoped.count() - written.count()
        rows = {r["split"]: r["count"] for r in written.groupBy("split").count().collect()}
        label_counts: dict[str, dict[int, int]] = {}
        for r in written.groupBy("split", "label").count().collect():
            label_counts.setdefault(r["split"], {})[r["label"]] = r["count"]
        leakage = {}
        for key in ("review_id", "text_hash"):
            shared = (written.groupBy(key).agg(F.countDistinct("split").alias("n"))
                      .where(F.col("n") > 1).count())
            leakage[f"{key}_in_multiple_splits"] = shared
        return SplitSummary(request.splits_uri, rows, label_counts, excluded, leakage)

    def majority_label(self, splits: SplitSummary) -> int:
        train = splits.label_counts.get(Split.TRAIN.value, {})
        return max(sorted(train), key=lambda label: train[label])

    def score_baseline(self, splits: SplitSummary, label: int, split: Split) -> ClassificationMetrics:
        predictions = (self._split(splits, split)
                       .withColumn("prediction", F.lit(float(label)))
                       .withColumn("score", F.lit(float(label))))
        return _to_metrics(BASELINE_NAME, split, predictions, "score")

    def fit(self, splits: SplitSummary, config: ModelConfig, models_uri: str) -> FittedModel:
        train = self._split(splits, Split.TRAIN)
        stop_words = [w for w in StopWordsRemover.loadDefaultStopWords("english") if w not in NEGATIONS]
        lr = LogisticRegression(featuresCol="features", labelCol="label",
                                maxIter=config.max_iter, regParam=config.reg_param)
        if config.class_weighting:
            weights = class_weights(splits.label_counts[Split.TRAIN.value])
            expr = F.when(F.col("label") == 1, weights[1]).otherwise(weights[0])
            train = train.withColumn("weight", expr)
            lr.setWeightCol("weight")
        pipeline = Pipeline(stages=[
            RegexTokenizer(inputCol="review_text", outputCol="tokens", pattern=TOKEN_PATTERN,
                           toLowercase=True, minTokenLength=1),
            StopWordsRemover(inputCol="tokens", outputCol="filtered", stopWords=stop_words),
            HashingTF(inputCol="filtered", outputCol="tf", numFeatures=config.num_features),
            IDF(inputCol="tf", outputCol="features"),
            lr,
        ])
        model_uri = f"{models_uri}/{config.name}"
        pipeline.fit(train).write().overwrite().save(model_uri)
        return FittedModel(config, model_uri)

    def predict(self, model: FittedModel, splits: SplitSummary, split: Split) -> DataFrame:
        return PipelineModel.load(model.model_uri).transform(self._split(splits, split))

    def score(self, model: FittedModel, splits: SplitSummary, split: Split) -> ClassificationMetrics:
        predictions = self.predict(model, splits, split)
        return _to_metrics(model.config.name, split, predictions, "rawPrediction")

    def error_examples(self, model: FittedModel, splits: SplitSummary, split: Split, limit: int) -> list[dict]:
        wrong = (self.predict(model, splits, split)
                 .where(F.col("prediction") != F.col("label").cast("double"))
                 .withColumn("p_recommended", vector_to_array("probability")[1])
                 .orderBy(F.xxhash64(F.col("review_id")))
                 .select("review_id", "app_id", "label", "prediction", "p_recommended", "review_text")
                 .limit(limit))
        return [row.asDict() for row in wrong.collect()]
