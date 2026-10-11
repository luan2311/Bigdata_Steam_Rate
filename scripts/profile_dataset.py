"""TV2-D02: kiểm kê dataset nguồn và tạo mẫu tái lập.

Chạy:  .venv\\Scripts\\python.exe scripts\\profile_dataset.py [--chunksize 500000]

Đọc CSV theo khối (không nạp toàn bộ 8 GB vào RAM), giữ mọi cột ở dạng chuỗi để thấy
giá trị thô. Đầu ra:
- artifacts/manifests/profile_report.json: header, số dòng, null, nhãn, ngôn ngữ, game,
  khoảng thời gian, trùng review_id, độ dài văn bản, thời gian chơi.
- data/sample/smoke.csv và data/sample/core.csv: mẫu theo hash của review_id.

Quy tắc lấy mẫu: bucket = hash_pandas_object(review_id, hash_key cố định) % 100000.
smoke giữ bucket < 48 (~0,048%, ~10 nghìn dòng), core giữ bucket < 4800 (~4,8%, ~1 triệu dòng).
Hai mẫu lồng nhau (smoke ⊂ core) và không phụ thuộc thứ tự dòng trong tệp.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "landing" / "steam-reviews-2021" / "v1" / "steam_reviews.csv"
REPORT_PATH = ROOT / "artifacts" / "manifests" / "profile_report.json"
SAMPLE_DIR = ROOT / "data" / "sample"

HASH_KEY = "steam2021tv2seed"  # đúng 16 ký tự, yêu cầu của pandas
BUCKETS = 100_000
SAMPLES = {"smoke": 48, "core": 4_800}

# Nhóm giờ chơi theo Plan.md §5.1, đơn vị giờ.
PLAYTIME_EDGES = [0, 2, 10, 50, 100, np.inf]
PLAYTIME_LABELS = ["[0,2)", "[2,10)", "[10,50)", "[50,100)", "[100,inf)"]
LENGTH_EDGES = [0, 1, 20, 100, 500, 2000, np.inf]
LENGTH_LABELS = ["0", "[1,20)", "[20,100)", "[100,500)", "[500,2000)", "[2000,inf)"]


def sample_buckets(review_ids: pd.Series) -> np.ndarray:
    hashed = pd.util.hash_pandas_object(review_ids.fillna(""), index=False, hash_key=HASH_KEY)
    return (hashed.to_numpy() % BUCKETS).astype(np.int64)


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


class Profile:
    def __init__(self) -> None:
        self.columns: list[str] = []
        self.rows = 0
        self.nulls: Counter = Counter()
        self.recommended_raw: Counter = Counter()
        self.language: Counter = Counter()
        self.language_recommended: Counter = Counter()
        self.app_reviews: Counter = Counter()
        self.app_recommended: Counter = Counter()
        self.app_names: dict[str, set] = {}
        self.month_created: Counter = Counter()
        self.ts_invalid: Counter = Counter()
        self.ts_min: dict[str, float] = {}
        self.ts_max: dict[str, float] = {}
        self.updated_before_created = 0
        self.review_length: Counter = Counter()
        self.review_blank = 0
        self.playtime_bucket: dict[str, Counter] = {}
        self.playtime_negative: Counter = Counter()
        self.playtime_invalid: Counter = Counter()
        self.playtime_max: dict[str, float] = {}
        self.ids: list[np.ndarray] = []
        self.non_numeric_ids = 0
        self.sample_rows: Counter = Counter()

    def update(self, chunk: pd.DataFrame) -> None:
        if not self.columns:
            self.columns = list(chunk.columns)
        self.rows += len(chunk)
        self.nulls.update(chunk.isna().sum().to_dict())

        rec = chunk["recommended"].fillna("<null>")
        self.recommended_raw.update(rec.value_counts().to_dict())
        is_rec = rec.str.lower().eq("true")

        lang = chunk["language"].fillna("<null>")
        self.language.update(lang.value_counts().to_dict())
        self.language_recommended.update(lang[is_rec].value_counts().to_dict())

        app = chunk["app_id"].fillna("<null>")
        self.app_reviews.update(app.value_counts().to_dict())
        self.app_recommended.update(app[is_rec].value_counts().to_dict())
        for app_id, names in chunk.groupby(app, sort=False)["app_name"].unique().items():
            self.app_names.setdefault(app_id, set()).update(str(n) for n in names)

        timestamps = {}
        for col in ("timestamp_created", "timestamp_updated"):
            values = to_number(chunk[col])
            timestamps[col] = values
            self.ts_invalid[col] += int((values.isna() & chunk[col].notna()).sum())
            if values.notna().any():
                self.ts_min[col] = min(self.ts_min.get(col, np.inf), float(values.min()))
                self.ts_max[col] = max(self.ts_max.get(col, -np.inf), float(values.max()))
        created = pd.to_datetime(timestamps["timestamp_created"], unit="s", utc=True, errors="coerce")
        self.month_created.update(created.dt.strftime("%Y-%m").dropna().value_counts().to_dict())
        self.updated_before_created += int(
            (timestamps["timestamp_updated"] < timestamps["timestamp_created"]).sum()
        )

        text = chunk["review"]
        length = text.fillna("").str.strip().str.len()
        self.review_blank += int(length.eq(0).sum())
        bucket = pd.cut(length, LENGTH_EDGES, right=False, labels=LENGTH_LABELS)
        self.review_length.update(bucket.value_counts().to_dict())

        for col in ("author.playtime_at_review", "author.playtime_forever"):
            if col not in chunk.columns:
                continue
            minutes = to_number(chunk[col])
            self.playtime_invalid[col] += int((minutes.isna() & chunk[col].notna()).sum())
            self.playtime_negative[col] += int((minutes < 0).sum())
            if minutes.notna().any():
                self.playtime_max[col] = max(self.playtime_max.get(col, 0.0), float(minutes.max()))
            hours = minutes[minutes >= 0] / 60
            counts = pd.cut(hours, PLAYTIME_EDGES, right=False, labels=PLAYTIME_LABELS).value_counts()
            self.playtime_bucket.setdefault(col, Counter()).update(counts.to_dict())

        ids = to_number(chunk["review_id"])
        self.non_numeric_ids += int((ids.isna() & chunk["review_id"].notna()).sum())
        self.ids.append(ids.dropna().astype(np.int64).to_numpy())

    def duplicate_stats(self) -> dict:
        all_ids = np.concatenate(self.ids) if self.ids else np.array([], dtype=np.int64)
        unique, counts = np.unique(all_ids, return_counts=True)
        return {
            "numeric_ids": int(all_ids.size),
            "unique_ids": int(unique.size),
            "ids_with_duplicates": int((counts > 1).sum()),
            "duplicate_rows_to_remove": int(all_ids.size - unique.size),
            "max_copies_of_one_id": int(counts.max()) if counts.size else 0,
            "non_numeric_ids": self.non_numeric_ids,
        }

    def report(self, bad_lines: list[str], seconds: float) -> dict:
        def ts(col: str) -> dict:
            lo, hi = self.ts_min.get(col), self.ts_max.get(col)
            fmt = lambda v: datetime.fromtimestamp(v, timezone.utc).isoformat() if v is not None else None
            return {"min_raw": lo, "max_raw": hi, "min_utc": fmt(lo), "max_utc": fmt(hi),
                    "non_numeric": self.ts_invalid[col]}

        apps = []
        for app_id, total in self.app_reviews.most_common():
            rec = self.app_recommended[app_id]
            apps.append({"app_id": app_id, "names": sorted(self.app_names.get(app_id, [])),
                         "reviews": total, "recommended": rec,
                         "recommended_rate_raw": round(rec / total, 4) if total else None})
        languages = [{"language": k, "reviews": v, "recommended": self.language_recommended[k],
                      "recommended_rate_raw": round(self.language_recommended[k] / v, 4)}
                     for k, v in self.language.most_common()]
        return {
            "source_file": SOURCE.relative_to(ROOT).as_posix(),
            "profiled_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "elapsed_seconds": round(seconds, 1),
            "note": "Số liệu thô trước làm sạch/dedup; tỷ lệ tính trên dòng có nhãn 'True'.",
            "columns": self.columns,
            "rows_parsed": self.rows,
            "bad_lines_skipped": len(bad_lines),
            "bad_line_examples": bad_lines[:20],
            "null_counts": {c: int(self.nulls[c]) for c in self.columns},
            "recommended_raw_values": dict(self.recommended_raw.most_common()),
            "review_id": self.duplicate_stats(),
            "review_text": {"blank_or_null": self.review_blank,
                            "length_chars_buckets": {k: int(self.review_length[k]) for k in LENGTH_LABELS}},
            "timestamps": {c: ts(c) for c in ("timestamp_created", "timestamp_updated")},
            "updated_before_created": self.updated_before_created,
            "reviews_by_created_month_utc": dict(sorted(self.month_created.items())),
            "playtime_minutes": {
                col: {"max": self.playtime_max.get(col), "negative": self.playtime_negative[col],
                      "non_numeric": self.playtime_invalid[col],
                      "hour_buckets": {k: int(self.playtime_bucket[col][k]) for k in PLAYTIME_LABELS}}
                for col in self.playtime_bucket
            },
            "languages": languages,
            "apps": apps,
            "app_count": len(self.app_reviews),
            "samples": {
                "method": f"hash_pandas_object(review_id, hash_key='{HASH_KEY}') % {BUCKETS}",
                "thresholds": SAMPLES,
                "rows": dict(self.sample_rows),
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--chunksize", type=int, default=500_000)
    parser.add_argument("--limit-chunks", type=int, default=0, help="chỉ đọc N khối đầu để thử")
    args = parser.parse_args()

    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    sample_paths = {name: SAMPLE_DIR / f"{name}.csv" for name in SAMPLES}
    for path in sample_paths.values():
        path.unlink(missing_ok=True)

    profile = Profile()
    bad_lines: list[str] = []
    started = time.perf_counter()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", pd.errors.ParserWarning)
        reader = pd.read_csv(
            SOURCE, dtype=str, keep_default_na=False, na_values=[""], encoding="utf-8",
            chunksize=args.chunksize, on_bad_lines="warn", index_col=0,
        )
        for i, chunk in enumerate(reader, start=1):
            profile.update(chunk)
            buckets = sample_buckets(chunk["review_id"])
            for name, threshold in SAMPLES.items():
                part = chunk[buckets < threshold]
                profile.sample_rows[name] += len(part)
                # Keep the unnamed source-row column so samples have the exact source header.
                part.to_csv(sample_paths[name], mode="a", header=not sample_paths[name].exists(),
                            index=True, index_label="", lineterminator="\n")
            print(f"khối {i}: {profile.rows:,} dòng, {time.perf_counter() - started:,.0f}s", flush=True)
            if args.limit_chunks and i >= args.limit_chunks:
                break
        for w in caught:
            if issubclass(w.category, pd.errors.ParserWarning):
                bad_lines.extend(str(w.message).strip().splitlines())

    report = profile.report(bad_lines, time.perf_counter() - started)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi {REPORT_PATH.relative_to(ROOT)}; mẫu: {dict(profile.sample_rows)}")


if __name__ == "__main__":
    main()
