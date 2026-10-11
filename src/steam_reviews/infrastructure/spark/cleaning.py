"""Spark adapter for ReviewBatchProcessor: bronze CSV -> silver Parquet."""

from __future__ import annotations

import csv
from datetime import datetime, timezone

from pyspark import StorageLevel
from pyspark.sql import Column, DataFrame, SparkSession, Window
from pyspark.sql import functions as F

from steam_reviews.application.dto.pipeline import CleanRequest, CleanResult, QualityCounts
from steam_reviews.domain.policies.dedup import DEDUP_KEY, DEDUP_ORDER
from steam_reviews.domain.policies.labels import LABEL_MAPPING
from steam_reviews.domain.policies.quality import (
    QUARANTINE_ORDER,
    UNKNOWN_LANGUAGE,
    QuarantineReason,
)
from steam_reviews.infrastructure.spark.source_schema import (
    CORRUPT_COLUMN,
    CSV_OPTIONS,
    EXPECTED_HEADER,
    RAW_SCHEMA,
    SCHEMA_VERSION,
)

SILVER_SCHEMA_VERSION = "silver-v1"
_DIGITS = r"^[0-9]+$"
_NUMBER = r"^-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$"


class SourceHeaderError(ValueError):
    """File-level error: the header does not match the source contract."""


def _blank_to_null(column: str) -> Column:
    value = F.trim(F.col(column))
    return F.when(value == "", None).otherwise(value)


def _as_number(column: str, dtype: str) -> Column:
    value = _blank_to_null(column)
    return F.when(value.rlike(_NUMBER), value.cast(dtype))


def _as_bool(column: str) -> Column:
    value = F.lower(_blank_to_null(column))
    return F.when(value == "true", True).when(value == "false", False)


def _epoch_to_timestamp(column: str) -> Column:
    seconds = _as_number(column, "double")
    return F.when(seconds > 0, F.timestamp_seconds(seconds.cast("long")))


def _label() -> Column:
    value = F.lower(_blank_to_null("recommended"))
    expr = None
    for raw, flag in LABEL_MAPPING.items():
        expr = (F.when(value == raw, F.lit(flag)) if expr is None
                else expr.when(value == raw, F.lit(flag)))
    return expr


def _quarantine_reason() -> Column:
    review_id, app_id = _blank_to_null("review_id"), _blank_to_null("app_id")
    checks = {
        QuarantineReason.MALFORMED_RECORD: F.col(CORRUPT_COLUMN).isNotNull(),
        QuarantineReason.MISSING_REVIEW_ID: review_id.isNull(),
        QuarantineReason.INVALID_REVIEW_ID: ~review_id.rlike(_DIGITS),
        QuarantineReason.MISSING_APP_ID: app_id.isNull(),
        QuarantineReason.INVALID_APP_ID: ~app_id.rlike(_DIGITS),
        QuarantineReason.INVALID_LABEL: _label().isNull(),
    }
    expr = None
    for reason in QUARANTINE_ORDER:  # first matching reason wins, so counts never overlap
        expr = (F.when(checks[reason], reason.value) if expr is None
                else expr.when(checks[reason], reason.value))
    return expr


def _sort_column(key) -> Column:
    column = F.col(key.column)
    if key.descending:
        return column.desc_nulls_last() if key.nulls_last else column.desc_nulls_first()
    return column.asc_nulls_last() if key.nulls_last else column.asc_nulls_first()


def check_header(spark: SparkSession, uri: str) -> None:
    first_line = spark.read.text(uri).first()
    if first_line is None:
        raise SourceHeaderError(f"{uri} is empty")
    header = next(csv.reader([first_line.value.lstrip("﻿")]))
    if header != EXPECTED_HEADER:
        raise SourceHeaderError(f"{uri} header {header} != {SCHEMA_VERSION} {EXPECTED_HEADER}")


def read_raw(spark: SparkSession, uri: str) -> DataFrame:
    check_header(spark, uri)
    return spark.read.options(**CSV_OPTIONS).schema(RAW_SCHEMA).csv(uri)


def to_silver_columns(raw: DataFrame, dataset_version: str, batch_id: str, ingested_at: datetime) -> DataFrame:
    """Typed silver columns; `author_steamid` is dropped as a personal identifier."""
    language = F.lower(_blank_to_null("language"))
    return raw.select(
        _blank_to_null("review_id").alias("review_id"),
        _blank_to_null("app_id").alias("app_id"),
        _blank_to_null("app_name").alias("app_name"),
        F.coalesce(language, F.lit(UNKNOWN_LANGUAGE)).alias("language"),
        F.col("review").alias("review_text"),
        (F.coalesce(F.length(F.trim(F.col("review"))), F.lit(0)) == 0).alias("review_text_blank"),
        _label().alias("recommended"),
        _epoch_to_timestamp("timestamp_created").alias("created_at"),
        _epoch_to_timestamp("timestamp_updated").alias("updated_at"),
        _as_number("votes_helpful", "long").alias("votes_helpful"),
        _as_number("votes_funny", "long").alias("votes_funny"),
        _as_number("weighted_vote_score", "double").alias("weighted_vote_score"),
        _as_number("comment_count", "long").alias("comment_count"),
        _as_bool("steam_purchase").alias("steam_purchase"),
        _as_bool("received_for_free").alias("received_for_free"),
        _as_bool("written_during_early_access").alias("written_during_early_access"),
        _as_number("author_num_games_owned", "long").alias("author_num_games_owned"),
        _as_number("author_num_reviews", "long").alias("author_num_reviews"),
        _as_number("author_playtime_forever", "double").alias("playtime_forever_minutes"),
        _as_number("author_playtime_last_two_weeks", "double").alias("playtime_last_two_weeks_minutes"),
        _as_number("author_playtime_at_review", "double").alias("playtime_at_review_minutes"),
        _epoch_to_timestamp("author_last_played").alias("author_last_played_at"),
        F.lit(dataset_version).alias("dataset_version"),
        F.lit(batch_id).alias("batch_id"),
        F.input_file_name().alias("source_file"),
        _as_number("source_row", "long").alias("source_row"),
        F.lit(ingested_at).cast("timestamp").alias("ingested_at"),
    )


class SparkReviewCleaner:
    def __init__(self, spark: SparkSession, silver_partitions: int = 8) -> None:
        self._spark = spark
        self._silver_partitions = silver_partitions

    def clean(self, request: CleanRequest) -> CleanResult:
        source = request.source
        raw = read_raw(self._spark, source.uri)
        batch_id = f"{source.dataset_version}-{(source.sha256 or 'nochecksum')[:12]}-{source.level.value}"
        classified = raw.withColumn("quarantine_reason", _quarantine_reason()).persist(
            StorageLevel.MEMORY_AND_DISK)

        reason_rows = classified.groupBy("quarantine_reason").count().collect()
        by_reason = {r["quarantine_reason"]: r["count"] for r in reason_rows}
        valid_pre_dedup = by_reason.pop(None, 0)
        rows_parsed = valid_pre_dedup + sum(by_reason.values())

        (classified.where(F.col("quarantine_reason").isNotNull())
         .withColumn("run_id", F.lit(str(request.run_id)))
         .write.mode("overwrite").parquet(request.quarantine_uri))

        valid = to_silver_columns(
            classified.where(F.col("quarantine_reason").isNull()),
            source.dataset_version, batch_id, datetime.now(timezone.utc),
        )
        # Counted independently of the dedup window so check V4 can actually fail.
        duplicates = (valid.groupBy(DEDUP_KEY).count().where(F.col("count") > 1)
                      .agg(F.sum(F.col("count") - 1).alias("extra")).first()["extra"] or 0)
        window = Window.partitionBy(DEDUP_KEY).orderBy(*[_sort_column(k) for k in DEDUP_ORDER])
        silver = (valid.withColumn("_rank", F.row_number().over(window))
                  .where(F.col("_rank") == 1).drop("_rank")
                  .withColumn("created_month", F.date_format("created_at", "yyyy-MM"))
                  .withColumn("run_id", F.lit(str(request.run_id))))
        (silver.repartition(self._silver_partitions).write.mode("overwrite")
         .parquet(request.silver_uri))
        classified.unpersist()

        written = self._spark.read.parquet(request.silver_uri)
        stats = written.agg(
            F.count(F.lit(1)).alias("rows"),
            F.sum(F.col("review_text_blank").cast("int")).alias("blank_text"),
            F.sum(F.col("created_at").isNull().cast("int")).alias("missing_created_at"),
            F.sum(F.col("playtime_at_review_minutes").isNull().cast("int")).alias("missing_playtime"),
        ).first()
        silver_rows = stats["rows"]
        counts = QualityCounts(
            rows_parsed=rows_parsed,
            invalid_by_reason={k: int(v) for k, v in sorted(by_reason.items())},
            valid_pre_dedup=valid_pre_dedup,
            duplicates_removed=int(duplicates),
            silver_rows=silver_rows,
            blank_text=int(stats["blank_text"] or 0),
            missing_created_at=int(stats["missing_created_at"] or 0),
            missing_playtime_at_review=int(stats["missing_playtime"] or 0),
        )
        return CleanResult(request.run_id, request.silver_uri, request.quarantine_uri, counts)
