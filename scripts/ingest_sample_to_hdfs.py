"""
Script thực thi và kiểm thử Ingestion dữ liệu mẫu vào HDFS qua WebHDFS REST API.
Mô phỏng chính xác cơ chế hoạt động của Apache NiFi InvokeHTTP Processor:
1. Đọc tệp CSV mẫu (~10.000 bản ghi) giữ toàn vẹn multiline và Unicode UTF-8.
2. Chia lô (batching) theo cấu hình của NiFi SplitRecord (~5.000 bản ghi/lô).
3. Gửi yêu cầu PUT tới WebHDFS NameNode (http://localhost:9870/webhdfs/v1/steam/bronze/sample/batch_X.csv?op=CREATE).
4. Nhận phản hồi HTTP 307 Redirect kèm vị trí DataNode đích.
5. Gửi stream nội dung sang DataNode đích và nhận mã HTTP 201 Created.
6. Đọc lại từ WebHDFS (OPEN) và xác minh tính toàn vẹn của 10.000 bản ghi.
"""

import csv
import io
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests

WEBHDFS_BASE = os.getenv("WEBHDFS_URL", "http://localhost:9870/webhdfs/v1")
SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "steam_reviews_sample_10k.csv")
BATCH_SIZE = 5000

def split_csv_into_batches(csv_path: str, batch_size: int = 5000):
    batches = []
    current_batch = []
    header = None
    
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            current_batch.append(row)
            if len(current_batch) >= batch_size:
                batches.append((header, current_batch))
                current_batch = []
        if current_batch:
            batches.append((header, current_batch))
            
    return batches

def batch_to_csv_bytes(header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")

def _resolve_docker_redirect_url(url: str) -> str:
    """
    Khi gọi WebHDFS từ máy host bên ngoài Docker, NameNode chuyển hướng sang hostname container:
    - hdfs-datanode-1:9864 -> localhost:9864
    - hdfs-datanode-2:9864 -> localhost:9865 (host port mapping)
    """
    import re
    if "hdfs-datanode-2" in url:
        return re.sub(r"hdfs-datanode-2(:\d+)?", "localhost:9865", url)
    elif "hdfs-datanode-1" in url:
        return re.sub(r"hdfs-datanode-1(:\d+)?", "localhost:9864", url)
    return url


def upload_to_webhdfs(hdfs_path: str, data_bytes: bytes, base_url: str = WEBHDFS_BASE):
    """
    Quy trình WebHDFS CREATE 2 bước chuẩn:
    Bước 1: PUT tới NameNode để nhận 307 Redirect URL
    Bước 2: PUT tới DataNode đích
    """
    create_url = f"{base_url}{hdfs_path}?op=CREATE&overwrite=true&permission=755"
    print(f"[*] Bước 1: Gửi yêu cầu khởi tạo tới NameNode: {create_url}")
    
    res1 = requests.put(create_url, allow_redirects=False, timeout=30)
    if res1.status_code == 307:
        raw_location = res1.headers["Location"]
        redirect_url = _resolve_docker_redirect_url(raw_location)
        print(f"[*] Bước 2: Nhận redirect tới DataNode ({raw_location}) -> Resolved: {redirect_url}")
        
        res2 = requests.put(redirect_url, data=data_bytes, headers={"Content-Type": "application/octet-stream"}, timeout=60)
        if res2.status_code in [200, 201]:
            print(f"[+] Nạp thành công vào HDFS: {hdfs_path}")
            return True
        else:
            print(f"[-] Lỗi bước 2 tại DataNode: HTTP {res2.status_code} - {res2.text}")
            return False
    elif res1.status_code in [200, 201]:
        print(f"[+] Nạp thành công vào HDFS: {hdfs_path}")
        return True
    else:
        print(f"[-] Lỗi bước 1 tại NameNode: HTTP {res1.status_code} - {res1.text}")
        return False

def verify_hdfs_content(hdfs_path: str, base_url: str = WEBHDFS_BASE):
    """Đọc lại dữ liệu từ WebHDFS và đếm số lượng logical records"""
    open_url = f"{base_url}{hdfs_path}?op=OPEN"
    print(f"[*] Đọc kiểm chứng từ HDFS: {open_url}")
    res = requests.get(open_url, allow_redirects=False, timeout=30)
    if res.status_code == 307:
        redirect_url = _resolve_docker_redirect_url(res.headers["Location"])
        res = requests.get(redirect_url, timeout=30)
    if res.status_code == 200:
        content = res.content.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        count = sum(1 for _ in reader)
        print(f"[+] Đọc thành công {count:,} records từ {hdfs_path}")
        return count
    else:
        print(f"[-] Không thể đọc tệp từ HDFS: HTTP {res.status_code}")
        return -1

def main():
    if not os.path.exists(SAMPLE_CSV_PATH):
        print(f"[-] Tệp mẫu không tồn tại: {SAMPLE_CSV_PATH}")
        sys.exit(1)
        
    print(f"[*] Đang đọc và chia lô tệp mẫu: {SAMPLE_CSV_PATH}")
    batches = split_csv_into_batches(SAMPLE_CSV_PATH, BATCH_SIZE)
    print(f"[*] Đã chia thành {len(batches)} lô (mỗi lô tối đa {BATCH_SIZE} records)")
    
    total_uploaded = 0
    uploaded_paths = []
    for idx, (header, rows) in enumerate(batches, start=1):
        hdfs_target = f"/steam/bronze/sample/batch_{idx:02d}.csv"
        csv_bytes = batch_to_csv_bytes(header, rows)
        print(f"\n--- Tiến hành nạp Lô {idx}/{len(batches)} ({len(rows):,} records, {len(csv_bytes):,} bytes) ---")
        try:
            ok = upload_to_webhdfs(hdfs_target, csv_bytes)
            if ok:
                total_uploaded += len(rows)
                uploaded_paths.append(hdfs_target)
        except Exception as e:
            print(f"[-] Ngoại lệ kết nối tới WebHDFS: {e}")
            print("[!] Lưu ý: Cụm HDFS cần đang ở trạng thái chạy để thực hiện nạp.")
            
    print(f"\n[*] Tổng số records đã nạp: {total_uploaded:,} records.")

    print("\n--- Kiểm chứng ngược lại qua WebHDFS (OPEN) ---")
    total_verified = 0
    for path in uploaded_paths:
        count = verify_hdfs_content(path)
        if count >= 0:
            total_verified += count
            
    if total_verified == total_uploaded and total_uploaded > 0:
        print(f"[+] Kiểm chứng khớp: {total_verified:,} logical records trong HDFS")
    else:
        print(f"[-] Kiểm chứng không khớp: {total_verified:,} != {total_uploaded:,}")

if __name__ == "__main__":
    main()
