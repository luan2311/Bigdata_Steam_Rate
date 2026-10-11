"""Spark adapter for AnalyticsProcessor: silver -> gold summary tables.

Grains (schemas/gold/gold_v1.md):
- game_summary:     app_id
- monthly_summary:  app_id x created_month x language   (rows with created_at only)
- language_summary: language
- playtime_summary: app_id x language x playtime_bucket
- quality_summary:  metric (one row per count)
Every table stores counts, not only rates, so filtered views can re-aggregate.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F

from steam_reviews.application.dto.pipeline import AnalyticsRequest, AnalyticsResult
from steam_reviews.domain.policies.metrics import (
    MINUTES_PER_HOUR,
    PLAYTIME_BUCKETS,
    PLAYTIME_MISSING,
    PLAYTIME_NEGATIVE,
)

GOLD_SCHEMA_VERSION = "gold-v1"
GOLD_TABLES = ("game_summary", "monthly_summary", "language_summary", "playtime_summary", "quality_summary")


def _counts() -> list[Column]:
    return [
        F.count(F.lit(1)).alias("review_count"),
        F.sum(F.col("recommended").cast("int")).alias("recommended_count"),
    ]


def _with_rate(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "recommended_rate",
        F.when(F.col("review_count") > 0, F.col("recommended_count") / F.col("review_count")),
    )


def _playtime_bucket() -> Column:
    minutes = F.col("playtime_at_review_minutes")
    hours = minutes / MINUTES_PER_HOUR
    expr = F.when(minutes.isNull() | F.isnan(minutes), PLAYTIME_MISSING).when(minutes < 0, PLAYTIME_NEGATIVE)
    for label, lower, upper in PLAYTIME_BUCKETS:
        condition = hours >= lower if upper == float("inf") else (hours >= lower) & (hours < upper)
        expr = expr.when(condition, label)
    return expr


def build_tables(silver: DataFrame, request: AnalyticsRequest) -> dict[str, DataFrame]:
    spark = silver.sparkSession
    game = _with_rate(silver.groupBy("app_id").agg(
        F.max("app_name").alias("app_name"), *_counts(),
        F.min("created_at").alias("first_review_at"), F.max("created_at").alias("last_review_at")))
    monthly = _with_rate(silver.where(F.col("created_at").isNotNull())
                         .groupBy("app_id", "created_month", "language").agg(*_counts()))
    language = _with_rate(silver.groupBy("language").agg(*_counts()))
    playtime = _with_rate(silver.withColumn("playtime_bucket", _playtime_bucket())
                          .groupBy("app_id", "language", "playtime_bucket").agg(*_counts()))

    c = request.counts
    metrics = [("rows_parsed", c.rows_parsed), ("invalid_records", c.invalid_records),
               ("valid_pre_dedup", c.valid_pre_dedup), ("duplicates_removed", c.duplicates_removed),
               ("silver_rows", c.silver_rows), ("blank_text", c.blank_text),
               ("missing_created_at", c.missing_created_at),
               ("missing_playtime_at_review", c.missing_playtime_at_review)]
    metrics += [(f"invalid_{reason}", n) for reason, n in c.invalid_by_reason.items()]
    quality = spark.createDataFrame(metrics, "metric string, value long")

    tables = {"game_summary": game, "monthly_summary": monthly, "language_summary": language,
              "playtime_summary": playtime, "quality_summary": quality}
    return {name: df.withColumn("run_id", F.lit(str(request.run_id)))
            .withColumn("schema_version", F.lit(GOLD_SCHEMA_VERSION)) for name, df in tables.items()}


def reconcile(gold: dict[str, DataFrame], silver_rows: int, dated_rows: int) -> list[str]:
    """Each additive table must sum back to silver (monthly: to rows with a date)."""
    expected = {"game_summary": silver_rows, "language_summary": silver_rows,
                "playtime_summary": silver_rows, "monthly_summary": dated_rows}
    errors = []
    for name, total in expected.items():
        actual = gold[name].agg(F.sum("review_count")).first()[0] or 0
        if actual != total:
            errors.append(f"{name} sums to {actual}, expected {total}")
    return errors


class SparkAnalyticsBuilder:
    def __init__(self, spark: SparkSession) -> None:
        self._spark = spark

    def build(self, request: AnalyticsRequest) -> AnalyticsResult:
        silver = self._spark.read.parquet(request.silver_uri)
        for name, df in build_tables(silver, request).items():
            df.coalesce(1).write.mode("overwrite").parquet(f"{request.gold_uri}/{name}")

        gold = {name: self._spark.read.parquet(f"{request.gold_uri}/{name}") for name in GOLD_TABLES}
        silver_rows = silver.count()
        dated_rows = silver.where(F.col("created_at").isNotNull()).count()
        errors = reconcile(gold, silver_rows, dated_rows)
        if silver_rows != request.counts.silver_rows:
            errors.append(f"silver has {silver_rows} rows, clean step reported {request.counts.silver_rows}")
        return AnalyticsResult(request.run_id, request.gold_uri,
                               {name: df.count() for name, df in gold.items()}, errors)
