"""Expected results for tests/fixtures/reviews_edge_cases.csv (16 source rows).

Quarantine: 1005 and 1006 (invalid label), one missing id, "abc", one missing app.
Duplicates: 1008 keeps the newer update; 1009 has equal timestamps and keeps the
lower source_row. Silver keeps 9 unique reviews.
"""

import pytest

from steam_reviews.application.dto.pipeline import CleanRequest
from steam_reviews.domain.entities.dataset import DatasetLevel, DatasetReference, RunId
from steam_reviews.infrastructure.spark.cleaning import SourceHeaderError, SparkReviewCleaner

pytestmark = pytest.mark.spark


@pytest.fixture
def cleaned(spark, edge_cases_csv, tmp_path):
    request = CleanRequest(
        DatasetReference(edge_cases_csv, "v1", DatasetLevel.SMOKE, "f" * 64),
        RunId("test-run"),
        str(tmp_path / "silver"),
        str(tmp_path / "quarantine"),
    )
    result = SparkReviewCleaner(spark, silver_partitions=1).clean(request)
    silver = {r["review_id"]: r for r in spark.read.parquet(result.silver_uri).collect()}
    return result, silver


def test_counts_reconcile(cleaned):
    counts = cleaned[0].counts
    assert counts.rows_parsed == 16
    assert counts.invalid_by_reason == {
        "invalid_label": 2, "invalid_review_id": 1, "missing_app_id": 1, "missing_review_id": 1}
    assert counts.valid_pre_dedup == 11
    assert counts.duplicates_removed == 2
    assert counts.silver_rows == 9
    assert counts.blank_text == 1
    assert counts.missing_created_at == 1
    assert counts.reconciliation_errors() == []


def test_multiline_quotes_and_unicode_survive(cleaned):
    silver = cleaned[1]
    assert silver["1002"]["review_text"] == "Line one\nLine two, with comma"
    assert silver["1003"]["review_text"] == 'He said "bad" game'
    assert silver["1004"]["app_name"] == "Trò chơi B ★"
    assert silver["1004"]["review_text"] == "Hay quá 🎮"


def test_dedup_keeps_latest_then_first_source_row(cleaned):
    silver = cleaned[1]
    assert silver["1008"]["review_text"] == "new version"
    assert silver["1008"]["recommended"] is True
    assert silver["1009"]["review_text"] == "tie first"


def test_types_language_and_lineage(cleaned):
    silver = cleaned[1]
    assert silver["1011"]["language"] == "unknown"
    assert silver["1011"]["created_at"] is None
    assert silver["1012"]["language"] == "english"
    assert silver["1012"]["playtime_at_review_minutes"] == -5.0
    assert silver["1001"]["created_month"] == "2020-09"
    assert silver["1001"]["batch_id"] == "v1-ffffffffffff-smoke"
    assert "author_steamid" not in silver["1001"].asDict()


def test_quarantine_keeps_reason(spark, cleaned):
    rows = spark.read.parquet(cleaned[0].quarantine_uri).collect()
    assert sorted(r["quarantine_reason"] for r in rows) == [
        "invalid_label", "invalid_label", "invalid_review_id", "missing_app_id", "missing_review_id"]


def test_wrong_header_is_a_file_level_error(spark, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n", encoding="utf-8")
    request = CleanRequest(DatasetReference(str(bad), "v1", DatasetLevel.SMOKE), RunId("x"),
                           str(tmp_path / "s"), str(tmp_path / "q"))
    with pytest.raises(SourceHeaderError):
        SparkReviewCleaner(spark).clean(request)
