# Runbook TV2: chạy pipeline dữ liệu và ML ở local mode

Áp dụng cho Windows, Spark `local[*]`, chưa cần cụm của TV1. Khi cụm sẵn sàng, chỉ cần đặt biến môi trường (mục 5), không phải sửa code.

## 1. Cài đặt một lần

| Bước | Lệnh / thao tác |
|---|---|
| Python 3.11 | Cài từ python.org (không thêm vào PATH) |
| Java 17 | Temurin 17 (đã có) |
| venv | `py -3.11 -m venv .venv` rồi `.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| winutils | Đặt `winutils.exe` và `hadoop.dll` (Hadoop 3.3.x) vào `<HADOOP_HOME>\bin`, rồi đặt biến user `HADOOP_HOME`. Máy TV2 dùng `D:\HocKi1Nam4\Big_Data\tools\hadoop-3.3.5` (bản build cộng đồng `cdarlint/winutils`) |
| Cache Kaggle | Biến user `KAGGLEHUB_CACHE` trỏ sang ổ D: để không làm đầy ổ C: |

## 2. Lấy dữ liệu và kiểm kê (D02)

```powershell
.venv\Scripts\python.exe scripts\download_dataset.py     # khoảng 3 phút tải + 2 phút giải nén + SHA-256
.venv\Scripts\python.exe scripts\profile_dataset.py      # khoảng 8-10 phút
```

| Đầu ra | Nội dung |
|---|---|
| `data/landing/steam-reviews-2021/v1/steam_reviews.csv` | Tệp nguồn 8,17 GB (không commit) |
| `artifacts/manifests/source_manifest.json` | Kích thước, SHA-256, giấy phép |
| `artifacts/manifests/profile_report.json` | Header, null, nhãn, ngôn ngữ, game, thời gian, trùng |
| `data/sample/smoke.csv`, `data/sample/core.csv` | Mẫu theo hash `review_id`; smoke ⊂ core |

## 3. ETL và ML

```powershell
.\scripts\run_tv2.ps1 etl --source data\sample\smoke.csv --level smoke     # in ra run_id
.\scripts\run_tv2.ps1 ml-prepare  --run-id <run_id> --max-rows 200000
.\scripts\run_tv2.ps1 ml-train    --run-id <run_id>
.\scripts\run_tv2.ps1 ml-evaluate --run-id <run_id>                         # chỉ chạy SAU KHI đã chốt mô hình
```

| Bước | Đọc | Ghi |
|---|---|---|
| `etl` | CSV nguồn/mẫu | `data/lake/silver/<run>`, `quarantine/<run>`, `gold/<run>/<bảng>`; `artifacts/metrics/<run>/quality_counts.json`, `gold_summary.json` |
| `ml-prepare` | silver | `data/lake/ml_splits/<run>`; `split_manifest.json` |
| `ml-train` | splits | `artifacts/models/<run>/<config>`; `validation_<config>.json`, `model_selection.json` |
| `ml-evaluate` | splits, model đã chọn | `test_metrics.json`, `test_error_examples.json` |

**Exit code:**
- `0`: thành công.
- `1`: một phép kiểm tra thất bại (đối soát V4, gold không cộng về silver, rò rỉ split). Kết quả lỗi vẫn được ghi JSON để xem.
- `2`: tham số sai hoặc thiếu đầu vào (ví dụ chạy `ml-train` trước `ml-prepare`).

## 4. Kiểm thử

```powershell
.venv\Scripts\python.exe -m pytest tests\unit                 # không cần Spark, chạy dưới 1 giây
.venv\Scripts\python.exe -m pytest tests\integration          # cần Java + HADOOP_HOME, khoảng 3 phút
```

## 5. Chuyển sang cụm của TV1

| Biến | Local (mặc định) | Cụm |
|---|---|---|
| `STEAM_LAKE_ROOT` | `<repo>/data/lake` | `hdfs://namenode:8020/steam` |
| `SPARK_MASTER` | `local[*]` | `spark://spark-master:7077` |
| `SPARK_DRIVER_MEMORY` | `4g` | Theo cấu hình cụm |

Khi chạy trên cụm, `--source` trỏ tới bronze trên HDFS mà NiFi đã ghi. Lệnh `etl` hiện tính SHA-256 trên file local, nên cần đổi sang đọc checksum từ manifest NiFi; việc này làm cùng TV1 ở D08.
