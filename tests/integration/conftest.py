from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture(scope="session")
def spark():
    from steam_reviews.infrastructure.spark.session import SparkSettings, create_spark

    session = create_spark(SparkSettings(master="local[2]", app_name="tests", driver_memory="1g",
                                         shuffle_partitions=2))
    yield session
    session.stop()


@pytest.fixture
def edge_cases_csv() -> str:
    return str(FIXTURES / "reviews_edge_cases.csv")
