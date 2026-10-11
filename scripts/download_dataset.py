"""TV2-D02: tải dataset Kaggle vào data/landing và ghi manifest nguồn.

Chạy:  .venv\\Scripts\\python.exe scripts\\download_dataset.py [--force]

Đầu ra:
- data/landing/steam-reviews-2021/v1/steam_reviews.csv
- artifacts/manifests/source_manifest.json (kích thước, SHA-256, phiên bản, giấy phép)

Tệp chỉ được đưa vào thư mục đích sau khi tải xong (tải vào thư mục tạm rồi đổi tên),
để NiFi/Spark không đọc phải tệp đang tải dở.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import kagglehub

HANDLE = "najzeko/steam-reviews-2021"
DATASET_VERSION = "v1"
FILE_NAME = "steam_reviews.csv"
EXPECTED_BYTES = 8_171_787_229  # Kaggle API datasets/list, kiểm tra 11/10/2026
LICENSE = "GPL 2"

ROOT = Path(__file__).resolve().parents[1]
LANDING_DIR = ROOT / "data" / "landing" / "steam-reviews-2021" / DATASET_VERSION
TEMP_DIR = ROOT / "data" / "landing" / "steam-reviews-2021" / f"_downloading_{DATASET_VERSION}"
MANIFEST_PATH = ROOT / "artifacts" / "manifests" / "source_manifest.json"


def sha256_of(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def download(force: bool) -> Path:
    target = LANDING_DIR / FILE_NAME
    if target.exists() and target.stat().st_size == EXPECTED_BYTES and not force:
        print(f"Đã có tệp hoàn chỉnh: {target}")
        return target

    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True)

    print(f"Đang tải {HANDLE} -> {TEMP_DIR} (khoảng 3,2 GB nén, 8,2 GB giải nén)...")
    kagglehub.dataset_download(HANDLE, output_dir=str(TEMP_DIR), force_download=True)

    downloaded = TEMP_DIR / FILE_NAME
    if not downloaded.exists():
        found = [p.name for p in TEMP_DIR.rglob("*") if p.is_file()]
        sys.exit(f"Không thấy {FILE_NAME} sau khi tải; các tệp nhận được: {found}")

    size = downloaded.stat().st_size
    if size != EXPECTED_BYTES:
        print(f"CẢNH BÁO: kích thước {size:,} khác metadata {EXPECTED_BYTES:,} byte.")

    LANDING_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    downloaded.replace(target)
    shutil.rmtree(TEMP_DIR)
    return target


def write_manifest(target: Path) -> dict:
    print("Đang tính SHA-256 (vài phút với tệp 8 GB)...")
    manifest = {
        "source": f"https://www.kaggle.com/datasets/{HANDLE}",
        "kaggle_handle": HANDLE,
        "dataset_version": DATASET_VERSION,
        "license": LICENSE,
        "file_name": target.name,
        "local_path": target.relative_to(ROOT).as_posix(),
        "size_bytes": target.stat().st_size,
        "expected_size_bytes": EXPECTED_BYTES,
        "sha256": sha256_of(target),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": f"kagglehub {kagglehub.__version__}",
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="tải lại dù đã có tệp")
    args = parser.parse_args()

    target = download(args.force)
    manifest = write_manifest(target)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
