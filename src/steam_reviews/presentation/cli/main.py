"""Batch entry point.

    python -m steam_reviews.presentation.cli.main etl --source data/sample/smoke.csv --level smoke
    python -m steam_reviews.presentation.cli.main ml-prepare --run-id <run>
    python -m steam_reviews.presentation.cli.main ml-train --run-id <run>
    python -m steam_reviews.presentation.cli.main ml-evaluate --run-id <run>

Exit codes: 0 ok, 1 failed check (reconciliation/leakage), 2 bad arguments or missing input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from steam_reviews.application.dto.modeling import ModelConfig, SplitRequest, TrainRequest
from steam_reviews.application.dto.pipeline import AnalyticsRequest, CleanRequest
from steam_reviews.application.use_cases.modeling import LeakageError
from steam_reviews.application.use_cases.pipeline import ReconciliationError
from steam_reviews.application.use_cases.run_state import (
    quality_counts_from,
    split_summary_from,
    to_payload,
    train_result_from,
)
from steam_reviews.bootstrap.config import AppConfig
from steam_reviews.bootstrap.container import Container
from steam_reviews.domain.entities.dataset import DatasetLevel, DatasetReference, RunId
from steam_reviews.domain.policies.split import ML_MAX_ROWS_CORE, SplitPolicy

# Plan.md 5.2: regParam 0.01 / 0.1, with and without class weights; at most four runs.
DEFAULT_CONFIGS = (
    ModelConfig("lr_reg001", reg_param=0.01),
    ModelConfig("lr_reg01", reg_param=0.1),
    ModelConfig("lr_reg001_weighted", reg_param=0.01, class_weighting=True),
    ModelConfig("lr_reg01_weighted", reg_param=0.1, class_weighting=True),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _print(title: str, payload) -> None:
    print(f"== {title}")
    print(json.dumps(to_payload(payload), ensure_ascii=False, indent=2, default=str))


def cmd_etl(c: Container, args) -> None:
    level = DatasetLevel(args.level)
    run_id = RunId(args.run_id) if args.run_id else RunId.new(level)
    source_uri = str(args.source)
    if source_uri.startswith("hdfs://") or source_uri.startswith("webhdfs://") or source_uri.startswith("http://"):
        sha = getattr(args, "sha256", None) or "remote_hdfs_source"
        source = DatasetReference(source_uri, args.dataset_version, level, sha)
    else:
        local = Path(source_uri)
        if not local.exists():
            raise FileNotFoundError(args.source)
        sha = getattr(args, "sha256", None) or _sha256(local)
        source = DatasetReference(local.resolve().as_posix(), args.dataset_version, level, sha)
    cleaned = c.clean_reviews().execute(CleanRequest(
        source, run_id, c.config.lake("silver", run_id), c.config.lake("quarantine", run_id)))
    _print("clean", cleaned.counts)
    gold = c.build_analytics().execute(AnalyticsRequest(
        run_id, cleaned.silver_uri, c.config.lake("gold", run_id), cleaned.counts))
    _print("gold", gold)
    print(f"run_id={run_id}")


def cmd_ml_prepare(c: Container, args) -> None:
    run_id = RunId(args.run_id)
    quality_counts_from(c.recorder.load(run_id, "quality_counts")["result"]["counts"])  # silver exists
    summary = c.prepare_model_data().execute(SplitRequest(
        run_id, c.config.lake("silver", run_id), c.config.lake("ml_splits", run_id),
        SplitPolicy(), args.max_rows or None))
    _print("splits", summary)


def cmd_ml_train(c: Container, args) -> None:
    run_id = RunId(args.run_id)
    splits = split_summary_from(c.recorder.load(run_id, "split_manifest")["summary"])
    configs = tuple(cfg for cfg in DEFAULT_CONFIGS if not args.only or cfg.name in args.only)
    result = c.train_model().execute(TrainRequest(run_id, splits, c.config.models_uri(run_id), configs))
    print(f"baseline validation macro-F1: {result.baseline_validation.macro_f1:.4f}")
    for name, m in result.validation.items():
        print(f"{name:22s} validation macro-F1: {m.macro_f1:.4f}")
    print(f"selected: {result.selected.config.name} -> {result.selected.model_uri}")


def cmd_ml_evaluate(c: Container, args) -> None:
    run_id = RunId(args.run_id)
    splits = split_summary_from(c.recorder.load(run_id, "split_manifest")["summary"])
    trained = train_result_from(c.recorder.load(run_id, "model_selection"))
    result = c.evaluate_model().execute(splits, trained, args.errors)
    for m in (result.baseline_test, result.model_test):
        print(f"{m.model:22s} test macro-F1 {m.macro_f1:.4f}  acc {m.accuracy:.4f}  "
              f"recall(0) {m.recall[0]:.4f}  recall(1) {m.recall[1]:.4f}  confusion {m.confusion}")
    print(f"error examples: {result.error_examples_uri}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="steam-reviews")
    sub = parser.add_subparsers(dest="command", required=True)

    etl = sub.add_parser("etl", help="bronze CSV -> silver -> gold")
    etl.add_argument("--source", required=True)
    etl.add_argument("--level", choices=[lv.value for lv in DatasetLevel], required=True)
    etl.add_argument("--dataset-version", default="v1")
    etl.add_argument("--run-id")
    etl.add_argument("--sha256", help="Checksum SHA-256 (tùy chọn khi đọc từ HDFS hoặc đã có manifest)")
    etl.set_defaults(handler=cmd_etl)

    prep = sub.add_parser("ml-prepare", help="english scope + hash split + leakage check")
    prep.add_argument("--run-id", required=True)
    prep.add_argument("--max-rows", type=int, default=ML_MAX_ROWS_CORE, help="0 = no cap")
    prep.set_defaults(handler=cmd_ml_prepare)

    train = sub.add_parser("ml-train", help="baseline + up to 4 LR configs, select on validation")
    train.add_argument("--run-id", required=True)
    train.add_argument("--only", nargs="*", help="subset of config names")
    train.set_defaults(handler=cmd_ml_train)

    evaluate = sub.add_parser("ml-evaluate", help="score selected model and baseline on test")
    evaluate.add_argument("--run-id", required=True)
    evaluate.add_argument("--errors", type=int, default=30)
    evaluate.set_defaults(handler=cmd_ml_evaluate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    container = Container(AppConfig.from_env())
    try:
        args.handler(container, args)
    except (ReconciliationError, LeakageError) as exc:
        print(f"CHECK FAILED: {exc}", file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        container.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
