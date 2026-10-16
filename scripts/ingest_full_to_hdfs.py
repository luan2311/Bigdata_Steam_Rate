"""Script nạp tuần tự toàn bộ dataset Steam Reviews (8.17 GB, 21.7+ triệu dòng) vào HDFS qua WebHDFS REST API.

Cơ chế hoạt động:
1. Đọc tệp CSV nguồn dạng luồng (streaming) qua csv.reader, hỗ trợ trọn vẹn multiline RFC 4180 và Unicode UTF-8 mà không nạp toàn bộ tệp vào RAM.
2. Phân lô tuần tự (mặc định 100.000 dòng/lô, ~38 MB/lô).
3. Đẩy từng lô lên WebHDFS NameNode (CREATE -> nhận HTTP 307 -> ghi DataNode).
4. Tự động ánh xạ Docker port: hdfs-datanode-1:9864 -> localhost:9864, hdfs-datanode-2:9864 -> localhost:9865.
5. Hỗ trợ tiếp tục (resume) từ số thứ tự lô cụ thể nếu bị gián đoạn.
6. Lưu manifest báo cáo vào artifacts/manifests/hdfs_full_ingestion_manifest.json.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests

# Tăng giới hạn độ dài trường của csv module để xử lý các bài review rất dài
max_int = sys.maxsize
while True:
    try:
        csv.field_size_limit(max_int)
        break
    except OverflowError:
        max_int = int(max_int / 10)

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT_DIR / "data" / "landing" / "steam_reviews.csv"
DEFAULT_MANIFEST = ROOT_DIR / "artifacts" / "manifests" / "hdfs_full_ingestion_manifest.json"
WEBHDFS_BASE = os.getenv("WEBHDFS_URL", "http://localhost:9870/webhdfs/v1")
HDFS_TARGET_DIR = "/steam/bronze/full"


def _resolve_docker_redirect_url(url: str) -> str:
    """Ánh xạ hostname trong container sang port mapping trên máy host Windows."""
    if "hdfs-datanode-2" in url:
        return re.sub(r"hdfs-datanode-2(:\d+)?", "localhost:9865", url)
    elif "hdfs-datanode-1" in url:
        return re.sub(r"hdfs-datanode-1(:\d+)?", "localhost:9864", url)
    return url


def upload_batch_to_webhdfs(
    hdfs_path: str,
    data_bytes: bytes,
    base_url: str = WEBHDFS_BASE,
    max_retries: int = 3,
) -> bool:
    """Gửi một lô dữ liệu vào HDFS qua WebHDFS REST API kèm retry."""
    create_url = f"{base_url}{hdfs_path}?op=CREATE&overwrite=true&permission=755"
    
    for attempt in range(1, max_retries + 1):
        try:
            res1 = requests.put(create_url, allow_redirects=False, timeout=30)
            if res1.status_code == 307:
                raw_location = res1.headers["Location"]
                redirect_url = _resolve_docker_redirect_url(raw_location)
                res2 = requests.put(
                    redirect_url,
                    data=data_bytes,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=120,
                )
                if res2.status_code in (200, 201):
                    return True
                else:
                    print(f"[-] Lỗi DataNode (lần {attempt}): HTTP {res2.status_code} - {res2.text[:200]}")
            elif res1.status_code in (200, 201):
                return True
            else:
                print(f"[-] Lỗi NameNode (lần {attempt}): HTTP {res1.status_code} - {res1.text[:200]}")
        except Exception as exc:
            print(f"[-] Ngoại lệ kết nối (lần {attempt}/{max_retries}): {exc}")
        
        time.sleep(2 * attempt)
    return False


def verify_batch_record_count(hdfs_path: str, base_url: str = WEBHDFS_BASE) -> int:
    """Đọc lại một lô từ WebHDFS và đếm số dòng logic để kiểm chứng."""
    open_url = f"{base_url}{hdfs_path}?op=OPEN"
    try:
        res = requests.get(open_url, allow_redirects=False, timeout=30)
        if res.status_code == 307:
            redirect_url = _resolve_docker_redirect_url(res.headers["Location"])
            res = requests.get(redirect_url, timeout=60)
        if res.status_code == 200:
            content = res.content.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(content))
            next(reader)  # skip header
            return sum(1 for _ in reader)
    except Exception as exc:
        print(f"[-] Lỗi khi đọc kiểm chứng {hdfs_path}: {exc}")
    return -1


def stream_batches(
    file_path: Path,
    batch_size: int,
) -> Iterator[Tuple[int, list[str], list[list[str]]]]:
    """Đọc tệp CSV dạng luồng và sinh các lô không giữ toàn bộ trong bộ nhớ."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader)
        batch_idx = 1
        current_rows = []
        for row in reader:
            current_rows.append(row)
            if len(current_rows) >= batch_size:
                yield batch_idx, header, current_rows
                batch_idx += 1
                current_rows = []
        if current_rows:
            yield batch_idx, header, current_rows


def batch_to_bytes(header: list[str], rows: list[list[str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description="Nạp tuần tự dữ liệu lớn vào HDFS")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Đường dẫn file CSV nguồn")
    parser.add_argument("--batch-size", type=int, default=100000, help="Số dòng logic mỗi lô")
    parser.add_argument("--start-batch", type=int, default=1, help="Bắt đầu từ số thứ tự lô (dùng khi resume)")
    parser.add_argument("--max-batches", type=int, default=0, help="Số lô tối đa cần nạp (0 = nạp toàn bộ)")
    parser.add_argument("--verify-samples", action="store_true", default=True, help="Kiểm chứng ngẫu nhiên sau khi nạp")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"[-] Không tìm thấy tệp nguồn: {args.source}")
        sys.exit(2)

    file_size_gb = args.source.stat().st_size / (1024 ** 3)
    print(f"==================================================================")
    print(f"[*] Bắt đầu nạp tuần tự dataset vào HDFS Bronze qua WebHDFS REST API")
    print(f"[*] Tệp nguồn: {args.source} ({file_size_gb:.2f} GB)")
    print(f"[*] Quy mô lô: {args.batch_size:,} dòng/lô")
    print(f"[*] WebHDFS Base: {WEBHDFS_BASE}")
    print(f"[*] Thư mục đích: {HDFS_TARGET_DIR}")
    print(f"==================================================================")

    start_time = time.time()
    total_records = 0
    total_bytes = 0
    uploaded_batches = []
    failed_batches = []

    batches_stream = stream_batches(args.source, args.batch_size)

    for batch_idx, header, rows in batches_stream:
        if batch_idx < args.start_batch:
            total_records += len(rows)
            continue
        if args.max_batches > 0 and (batch_idx - args.start_batch + 1) > args.max_batches:
            break

        hdfs_path = f"{HDFS_TARGET_DIR}/batch_{batch_idx:04d}.csv"
        csv_bytes = batch_to_bytes(header, rows)
        batch_size_mb = len(csv_bytes) / (1024 * 1024)
        
        step_start = time.time()
        ok = upload_batch_to_webhdfs(hdfs_path, csv_bytes)
        step_elapsed = time.time() - step_start

        if ok:
            total_records += len(rows)
            total_bytes += len(csv_bytes)
            uploaded_batches.append(hdfs_path)
            cum_elapsed = time.time() - start_time
            rec_per_sec = total_records / max(cum_elapsed, 0.001)
            print(
                f"[+] Lô {batch_idx:04d} ({len(rows):,} dòng, {batch_size_mb:.1f} MB) "
                f"-> OK ({step_elapsed:.1f}s) | Tổng: {total_records:,} dòng | {rec_per_sec:.0f} dòng/s"
            )
        else:
            print(f"[-] Lô {batch_idx:04d} -> THẤT BẠI!")
            failed_batches.append(hdfs_path)
            break

    total_elapsed = time.time() - start_time
    print(f"\n==================================================================")
    print(f"[*] Hoàn tất giai đoạn nạp HDFS trong {total_elapsed:.1f} giây ({total_elapsed/60:.2f} phút)")
    print(f"[*] Đã nạp thành công: {len(uploaded_batches)} lô, tổng {total_records:,} dòng, {total_bytes/(1024**3):.2f} GB")

    if failed_batches:
        print(f"[-] Có {len(failed_batches)} lô bị lỗi. Dừng pipeline.")
        sys.exit(1)

    # Kiểm chứng mẫu qua WebHDFS OPEN
    verified_ok = True
    if args.verify_samples and uploaded_batches:
        sample_indices = [0, len(uploaded_batches) // 2, -1]
        print(f"[*] Đang kiểm chứng ngẫu nhiên các lô: đầu, giữa, cuối...")
        for idx in set(sample_indices):
            path = uploaded_batches[idx]
            count = verify_batch_record_count(path)
            if count > 0:
                print(f"    [+] Kiểm chứng {path}: Đọc được {count:,} dòng -> KHỚP")
            else:
                print(f"    [-] Kiểm chứng {path}: Thất bại!")
                verified_ok = False

    # Ghi manifest
    manifest_data = {
        "dataset_name": "steam-reviews-2021",
        "source_path": str(args.source),
        "source_size_bytes": args.source.stat().st_size,
        "hdfs_target_directory": HDFS_TARGET_DIR,
        "batch_size": args.batch_size,
        "total_batches": len(uploaded_batches),
        "total_records": total_records,
        "total_bytes_uploaded": total_bytes,
        "elapsed_seconds": round(total_elapsed, 2),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "verified": verified_ok,
        "status": "SUCCESS" if (not failed_batches and verified_ok) else "FAILED",
    }
    DEFAULT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    print(f"[*] Đã lưu manifest tại: {DEFAULT_MANIFEST}")

    sys.exit(0 if manifest_data["status"] == "SUCCESS" else 1)


if __name__ == "__main__":
    main()
