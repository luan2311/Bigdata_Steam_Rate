"""TV2-D05: đối soát gold bằng một cách tính độc lập (pandas, không dùng code Spark).

Chạy:  .venv\\Scripts\\python.exe scripts\\verify_gold.py --source data\\sample\\core.csv --run-id <run>

Đọc lại CSV nguồn, tự áp quy tắc (nhãn True/False, dedup theo review_id giữ updated
mới nhất, tháng UTC, nhóm giờ chơi), rồi so từng dòng với gold Parquet của run.
Ghi kết quả vào artifacts/metrics/<run>/verify_gold.json. Exit 1 nếu có chênh lệch.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LAKE = ROOT / "data" / "lake"
BINS = [0, 2, 10, 50, 100, np.inf]
LABELS = ["[0,2)", "[2,10)", "[10,50)", "[50,100)", "[100,inf)"]
USECOLS = ["review_id", "app_id", "language", "recommended", "timestamp_created",
           "timestamp_updated", "author.playtime_at_review"]


def load_expected(source: Path) -> pd.DataFrame:
    df = pd.read_csv(source, dtype=str, keep_default_na=False, na_values=[""], usecols=USECOLS)
    df = df[df["recommended"].str.lower().isin(["true", "false"])
            & df["review_id"].str.fullmatch(r"\d+", na=False)
            & df["app_id"].str.fullmatch(r"\d+", na=False)].copy()
    df["recommended"] = df["recommended"].str.lower().eq("true")
    df["updated"] = pd.to_numeric(df["timestamp_updated"], errors="coerce")
    df = df.sort_values("updated", ascending=False, na_position="last").drop_duplicates("review_id")
    created = pd.to_numeric(df["timestamp_created"], errors="coerce")
    df["created_month"] = pd.to_datetime(created.where(created > 0), unit="s", utc=True).dt.strftime("%Y-%m")
    df["language"] = df["language"].fillna("unknown").str.strip().str.lower()
    minutes = pd.to_numeric(df["author.playtime_at_review"], errors="coerce")
    bucket = pd.cut(minutes / 60, BINS, right=False, labels=LABELS).astype(object)
    bucket[minutes.isna()] = "missing"
    bucket[minutes < 0] = "negative"
    df["playtime_bucket"] = bucket
    return df


def summarize(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    out = df.groupby(keys, dropna=False).agg(review_count=("recommended", "size"),
                                             recommended_count=("recommended", "sum"))
    return out.astype("int64").sort_index()


def compare(name: str, expected: pd.DataFrame, gold_dir: Path, keys: list[str]) -> dict:
    gold = pd.read_parquet(gold_dir / name)
    actual = gold.set_index(keys)[["review_count", "recommended_count"]].astype("int64").sort_index()
    joined = expected.join(actual, how="outer", lsuffix="_expected", rsuffix="_gold").fillna(-1)
    diff = joined[(joined["review_count_expected"] != joined["review_count_gold"])
                  | (joined["recommended_count_expected"] != joined["recommended_count_gold"])]
    rate_gold = gold["recommended_rate"].to_numpy()
    rate_calc = (gold["recommended_count"] / gold["review_count"]).to_numpy()
    return {"table": name, "rows_expected": len(expected), "rows_gold": len(actual),
            "mismatched_rows": len(diff), "rate_formula_ok": bool(np.allclose(rate_gold, rate_calc)),
            "examples": diff.head(5).reset_index().astype(str).to_dict("records")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    gold_dir = LAKE / "gold" / args.run_id
    df = load_expected(Path(args.source))
    checks = [
        compare("game_summary", summarize(df, ["app_id"]), gold_dir, ["app_id"]),
        compare("language_summary", summarize(df, ["language"]), gold_dir, ["language"]),
        compare("monthly_summary", summarize(df.dropna(subset=["created_month"]),
                                             ["app_id", "created_month", "language"]),
                gold_dir, ["app_id", "created_month", "language"]),
        compare("playtime_summary", summarize(df, ["app_id", "language", "playtime_bucket"]),
                gold_dir, ["app_id", "language", "playtime_bucket"]),
    ]
    report = {"run_id": args.run_id, "source": args.source, "silver_rows_expected": len(df),
              "method": "pandas recomputation from CSV, independent of Spark code", "checks": checks}
    out = ROOT / "artifacts" / "metrics" / args.run_id / "verify_gold.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in checks:
        status = "OK" if c["mismatched_rows"] == 0 and c["rate_formula_ok"] else "MISMATCH"
        print(f"{status:8s} {c['table']:18s} expected {c['rows_expected']:>7} gold {c['rows_gold']:>7} "
              f"mismatched {c['mismatched_rows']}")
    ok = all(c["mismatched_rows"] == 0 and c["rate_formula_ok"] for c in checks)
    print(f"silver rows (pandas): {len(df):,}; report: {out.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
