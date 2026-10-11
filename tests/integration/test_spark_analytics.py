import pytest

from steam_reviews.application.dto.pipeline import AnalyticsRequest, CleanRequest
from steam_reviews.domain.entities.dataset import DatasetLevel, DatasetReference, RunId
from steam_reviews.infrastructure.spark.analytics import SparkAnalyticsBuilder
from steam_reviews.infrastructure.spark.cleaning import SparkReviewCleaner

pytestmark = pytest.mark.spark


@pytest.fixture
def gold(spark, edge_cases_csv, tmp_path):
    run = RunId("test-run")
    cleaned = SparkReviewCleaner(spark, 1).clean(CleanRequest(
        DatasetReference(edge_cases_csv, "v1", DatasetLevel.SMOKE), run,
        str(tmp_path / "silver"), str(tmp_path / "quarantine")))
    result = SparkAnalyticsBuilder(spark).build(
        AnalyticsRequest(run, cleaned.silver_uri, str(tmp_path / "gold"), cleaned.counts))
    tables = {name: spark.read.parquet(f"{result.gold_uri}/{name}") for name in result.table_rows}
    return result, tables


def test_gold_reconciles_with_silver(gold):
    result, _ = gold
    assert result.check_errors == []
    assert set(result.table_rows) == {"game_summary", "monthly_summary", "language_summary",
                                      "playtime_summary", "quality_summary"}


def test_game_summary_counts_and_rate(gold):
    games = {r["app_id"]: r for r in gold[1]["game_summary"].collect()}
    # Game 10 silver rows: 1001 T, 1002 F, 1003 F, 1008 T, 1009 T, 1010 T, 1011 T, 1012 F
    assert games["10"]["review_count"] == 8
    assert games["10"]["recommended_count"] == 5
    assert games["10"]["recommended_rate"] == pytest.approx(5 / 8)
    assert games["20"]["review_count"] == 1
    assert games["10"]["run_id"] == "test-run"


def test_monthly_excludes_missing_dates_only(gold):
    monthly = gold[1]["monthly_summary"]
    assert monthly.groupBy().sum("review_count").first()[0] == 8
    assert monthly.where("created_month IS NULL").count() == 0


def test_playtime_buckets_keep_negative_separate(gold):
    buckets = {r["playtime_bucket"]: r["review_count"]
               for r in gold[1]["playtime_summary"].groupBy("playtime_bucket").sum("review_count")
               .withColumnRenamed("sum(review_count)", "review_count").collect()}
    assert buckets == {"[2,10)": 8, "negative": 1}


def test_language_keeps_unknown(gold):
    languages = {r["language"]: r["review_count"] for r in gold[1]["language_summary"].collect()}
    assert languages == {"english": 7, "vietnamese": 1, "unknown": 1}
