"""Physical source contract (schemas/source/steam_reviews_v1.md).

The CSV header contains dotted names such as `author.playtime_at_review`.
They are flat columns, not nested structs, so they are mapped by position to
safe names; the header is verified separately before reading.
"""

from __future__ import annotations

from pyspark.sql.types import StringType, StructField, StructType

SCHEMA_VERSION = "source-v1"

# (header in the CSV, safe column name used inside Spark)
SOURCE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("", "source_row"),
    ("app_id", "app_id"),
    ("app_name", "app_name"),
    ("review_id", "review_id"),
    ("language", "language"),
    ("review", "review"),
    ("timestamp_created", "timestamp_created"),
    ("timestamp_updated", "timestamp_updated"),
    ("recommended", "recommended"),
    ("votes_helpful", "votes_helpful"),
    ("votes_funny", "votes_funny"),
    ("weighted_vote_score", "weighted_vote_score"),
    ("comment_count", "comment_count"),
    ("steam_purchase", "steam_purchase"),
    ("received_for_free", "received_for_free"),
    ("written_during_early_access", "written_during_early_access"),
    ("author.steamid", "author_steamid"),
    ("author.num_games_owned", "author_num_games_owned"),
    ("author.num_reviews", "author_num_reviews"),
    ("author.playtime_forever", "author_playtime_forever"),
    ("author.playtime_last_two_weeks", "author_playtime_last_two_weeks"),
    ("author.playtime_at_review", "author_playtime_at_review"),
    ("author.last_played", "author_last_played"),
)

EXPECTED_HEADER = [header for header, _ in SOURCE_COLUMNS]
CORRUPT_COLUMN = "_corrupt_record"

# Every column is read as string so bad values are visible instead of silently null.
RAW_SCHEMA = StructType(
    [StructField(name, StringType(), True) for _, name in SOURCE_COLUMNS]
    + [StructField(CORRUPT_COLUMN, StringType(), True)]
)

CSV_OPTIONS = {
    "header": "true",
    "multiLine": "true",  # reviews contain line breaks inside quotes
    "quote": '"',
    "escape": '"',  # RFC 4180 doubled quotes, as written by pandas
    "encoding": "UTF-8",
    "mode": "PERMISSIVE",
    "columnNameOfCorruptRecord": CORRUPT_COLUMN,
    "enforceSchema": "true",
}
