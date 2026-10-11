# Báo cáo tiến độ TV2: Dữ liệu, Spark và ML

**Ngày cập nhật:** 11/10/2026
**Nhánh:** `phungtuanhuy` (chưa commit)
**Trạng thái:** 9/15 việc của TV2 đã có sản phẩm chạy được và đang **chờ review**. 6 việc còn lại cần TV1 hoặc TV3.

> Theo quy định của nhóm, các ô trong `Checklist.md` chỉ được đánh `[x]` sau khi người review xác nhận. Danh sách bên dưới là đề nghị review, chưa phải nghiệm thu.

---

## 1. Tóm tắt nhanh

- Đã tải và kiểm kê **toàn bộ dataset**: 1 tệp `steam_reviews.csv`, 8,17 GB, **21.747.371 review**, 315 game, 28 ngôn ngữ, thời gian 2010-11 → 2021-01.
- Pipeline **CSV → silver → gold → ML** chạy được bằng Spark `local[*]` trên mẫu **Core 1.044.450 dòng**. Lưu ý: chưa chạy trên cụm.
- Gold được kiểm tra lại bằng một cách tính độc lập: **lệch 0 dòng**.
- Mô hình TF-IDF + Logistic Regression đạt **macro-F1 0,786 trên test**, baseline đa số đạt 0,473, mức tăng vượt mục tiêu +0,10 trong Plan.
- 50 test tự động (unit và integration) đều pass.

---

## 2. Chín việc đã làm (chờ review)

| Mã | Việc | Sản phẩm / bằng chứng | Người review đề xuất |
|---|---|---|---|
| **TV2-D01** | Chốt bài toán, 5 câu hỏi phân tích, phạm vi EDA/ML, phân biệt nhãn khuyến nghị với cảm xúc | [docs/data/01_bai_toan_du_lieu.md](docs/data/01_bai_toan_du_lieu.md) | TV3 |
| **TV2-D02** | Tải dataset, đo SHA-256, kiểm kê toàn tệp, tạo mẫu smoke/core tái lập, data dictionary, schema source/silver/gold | [02_kiem_ke_du_lieu.md](docs/data/02_kiem_ke_du_lieu.md), [03_data_dictionary.md](docs/data/03_data_dictionary.md), [schemas/](schemas/), [source_manifest.json](artifacts/manifests/source_manifest.json), [profile_report.json](artifacts/manifests/profile_report.json) | **TV1 + TV3** (bắt buộc) |
| **TV2-D03** | ETL đúng Clean Architecture: domain → application → adapter Spark → CLI | `src/steam_reviews/`, [tests/unit/test_architecture.py](tests/unit/test_architecture.py) | TV1 |
| **TV2-D04** | Làm sạch, quarantine có mã lý do, dedup theo `review_id`, ghi silver Parquet | [cleaning.py](src/steam_reviews/infrastructure/spark/cleaning.py), fixture [reviews_edge_cases.csv](tests/fixtures/reviews_edge_cases.csv) | TV1 |
| **TV2-D05** | Gold v1 gồm 5 bảng, đối soát độc lập bằng pandas | [analytics.py](src/steam_reviews/infrastructure/spark/analytics.py), [scripts/verify_gold.py](scripts/verify_gold.py), `artifacts/metrics/core-20261011-v1/verify_gold.json` | TV3 |
| **TV2-D06** | Chia train/val/test theo hash văn bản, baseline đa số, TF-IDF + LR đầu tiên | [trainer.py](src/steam_reviews/infrastructure/ml/trainer.py), `split_manifest.json` | TV1 |
| **TV2-D07** | Kiểm tra rò rỉ: số ID và text hash nằm ở nhiều tập đều bằng 0; số liệu sơ bộ cho slide | [04_ket_qua_core.md](docs/data/04_ket_qua_core.md) mục 2–3 | TV3 |
| **TV2-D08** | Thử 4 cấu hình (regParam 0,01/0,1, có/không trọng số lớp), chọn theo macro-F1 validation | `model_selection.json`, `validation_*.json` | TV3 |
| **TV2-D09** | Chấm test một lần sau khi chốt mô hình; precision/recall/F1 từng lớp, PR-AUC, confusion matrix; phân tích 30 lỗi | `test_metrics.json`, `test_error_examples.json`, [04_ket_qua_core.md](docs/data/04_ket_qua_core.md) mục 5–6 | TV3 |

Metrics nằm trong `artifacts/metrics/core-20261011-v1/`. Hướng dẫn chạy lại: [docs/runbooks/tv2_local_pipeline.md](docs/runbooks/tv2_local_pipeline.md).

---

## 3. Số liệu chính

### Dữ liệu (toàn bộ 21,7 triệu dòng, số thô)

| Chỉ số | Giá trị |
|---|---:|
| Tổng review | 21.747.371 |
| `review_id` trùng | 134.927 |
| Nhãn khuyến nghị (`True`) | 87,47% |
| Review tiếng Anh | 9.635.437 (44,3%) |
| Text rỗng | 39.963 |
| Thiếu `playtime_at_review` | 25.682 |

### Pipeline mức Core (mẫu 4,8%)

| Bước | Số dòng |
|---|---:|
| Đọc vào | 1.044.450 |
| Quarantine | 0 |
| Trùng bị loại | 6.379 |
| Silver | 1.038.071 |
| Tập ML (tiếng Anh, giới hạn 200.000) | train 138.661 / val 29.202 / test 32.137 |

### Mô hình (trên test, 32.137 dòng)

| Mô hình | Macro-F1 | Accuracy | Recall lớp "không khuyến nghị" |
|---|---:|---:|---:|
| Baseline đa số | 0,473 | 0,897 | 0,000 |
| **LR (regParam 0,1, có trọng số lớp)** | **0,786** | **0,916** | **0,658** |

---

## 4. Phát hiện quan trọng cần cả nhóm biết

1. **Dataset có dữ liệu lặp:** 134.927 review Hollow Knight bị lặp nguyên khối, mọi cột đều giống hệt nhau. Nếu không dedup, Hollow Knight bị đếm gấp đôi. Pipeline đã xử lý; **TV1 không cần dedup trong NiFi**.
2. **Dataset không chỉ gồm review năm 2021:** dữ liệu trải từ 11/2010 đến 23/01/2021, và tháng 01/2021 chưa đủ tháng. TV3 cần ghi chú điều này trên biểu đồ theo tháng.
3. **`timestamp_updated` có giá trị lỗi**, lớn nhất tới năm 2042. Chỉ dùng cột này để chọn bản mới khi dedup, không vẽ biểu đồ theo nó.
4. **Nhãn mất cân bằng (87,5% khuyến nghị).** Không dùng accuracy làm thước đo chính, vì luôn đoán "khuyến nghị" cũng đạt khoảng 90%.
5. **`author.steamid` là định danh cá nhân** nên đã bị bỏ khỏi silver. Dashboard không được hiển thị cột này.
6. Một số review gắn `language = english` nhưng thực tế là ngôn ngữ khác, và một số chứa ký tự lỗi mã hóa `�` ngay từ nguồn.

---

## 5. Bàn giao ngay cho thành viên khác

### Gửi TV1

| Bàn giao | File | TV1 dùng để |
|---|---|---|
| Schema nguồn và gợi ý cấu hình NiFi | [schemas/source/steam_reviews_v1.md](schemas/source/steam_reviews_v1.md) | Cấu hình CSVReader: quote/escape `"`, header 23 cột, **không cắt theo dòng** |
| Fixture CSV lỗi | [tests/fixtures/reviews_edge_cases.csv](tests/fixtures/reviews_edge_cases.csv) | Thử luồng NiFi (review nhiều dòng, dấu nháy, Unicode, nhãn sai, ID trùng) |
| Dataset đã tải và mẫu | `data/landing/...`, `data/sample/smoke.csv`, `core.csv` (không có trên Git, lấy trực tiếp từ máy TV2 hoặc tải lại bằng script) | Smoke test NiFi → HDFS |
| Đề xuất phiên bản runtime | Spark **3.5.x**, Java **17**, Python **3.11** | Khóa phiên bản cho cụm, khớp với code của TV2 |
| Biến môi trường để chạy trên cụm | `STEAM_LAKE_ROOT`, `SPARK_MASTER`, `SPARK_DRIVER_MEMORY` (xem runbook mục 5) | Chạy code TV2 trên cụm mà không phải sửa code |

### Gửi TV3

| Bàn giao | File | TV3 dùng để |
|---|---|---|
| Schema gold v1 (**cần TV3 duyệt**) | [schemas/gold/gold_v1.md](schemas/gold/gold_v1.md) | Thiết kế bộ lọc và biểu đồ; xác nhận grain có đủ chiều cần lọc chưa |
| Gold thật (Core) | `data/lake/gold/core-20261011-v1/` (Parquet, lấy trực tiếp từ máy TV2) | Thay fixture bằng dữ liệu thật |
| 5 nhận xét có số liệu và kết quả ML | [docs/data/04_ket_qua_core.md](docs/data/04_ket_qua_core.md) mục 2, 4, 5, 6 | Slide tiến độ D7 và trang Mô hình của dashboard. **Bắt buộc ghi "mẫu Core 4,8%"** |
| Metrics dạng JSON | `artifacts/metrics/core-20261011-v1/` | Dữ liệu cho trang Mô hình (confusion matrix, F1 từng lớp) |

---

## 6. Sáu việc còn lại: cần thành viên nào

| Mã | Việc | **Cần ai** | Cần cụ thể gì | TV2 đã chuẩn bị |
|---|---|---|---|---|
| **TV2-D10** | Chạy Core/Full trên cụm, tối ưu partition và kích thước tệp | **TV1** | Cụm HDFS + Spark 2 worker chạy được; bronze do NiFi ghi vào HDFS; manifest lô có checksum | Code chạy được trên cụm chỉ bằng biến môi trường. Cần sửa thêm phần đọc checksum từ manifest NiFi (làm cùng TV1) |
| **TV2-D11** | Đối soát gold độc lập, kiểm tra model nạp lại, so ít nhất 3 tổ hợp filter | **TV3** (một phần TV1) | Dashboard có bộ lọc để so số liệu; gold chạy trên cụm | `verify_gold.py` đã khớp 0 lệch. Test nạp lại model TV2 tự làm được |
| **TV2-D12** | Viết phần thực nghiệm vào Word (lý thuyết, làm sạch, mô hình, metrics, hạn chế) | **TV3** (một phần TV1) | Khung Word đúng Rule; số liệu cuối từ run trên cụm | Khoảng 70% nội dung có sẵn trong `docs/data/`. Phần lý thuyết TV2 viết được ngay |
| **TV2-D13** | Review chéo: chia tập, schema, số liệu Word/PPT/dashboard, quy tắc kiến trúc | **TV3** | Bản Word, PPT và dashboard hoàn chỉnh | Có test tự động kiểm tra quy tắc import giữa các lớp |
| **TV2-D14** | Diễn tập phần xử lý/ML và câu hỏi phản biện | **TV1 + TV3** (cả nhóm) | Buổi diễn tập chung | TV2 tự soạn được bộ câu hỏi và câu trả lời |
| **TV2-D15** | Xác nhận artifact: metrics, model, checksum, phiên bản, hướng dẫn tái lập | **TV1 + TV3** (cả nhóm) | Mọi thành phần đã chốt; TV1 sao lưu artifact | Manifest, SHA-256 và `run_id` đã được ghi tự động |

### TV2 đang cần gì từ từng người

**Từ TV1:**
1. Xác nhận phiên bản Spark 3.5.x / Java 17 / Python 3.11 cho cụm.
2. Review schema nguồn ([schemas/source/](schemas/source/)) để cấu hình NiFi.
3. Cho biết khi nào HDFS và Spark 2 worker chạy được, kèm đường dẫn bronze và định dạng manifest lô (cần cho D10).

**Từ TV3:**
1. Duyệt schema gold v1 ([schemas/gold/gold_v1.md](schemas/gold/gold_v1.md)): grain và các chiều lọc đã đủ cho 4 trang dashboard chưa.
2. Gửi khung Word để TV2 viết phần thực nghiệm (D12).
3. Chọn thời điểm cùng đối soát 3 tổ hợp filter (D11).

---

## 7. Giới hạn hiện tại

- **Chưa chạy trên cụm phân tán.** Mọi kết quả là Spark `local[*]` trên một máy (11,7 GB RAM) với mẫu Core. Không được trình bày là kết quả Full.
- Lệnh `etl` đang tính checksum trên file local; khi đọc từ HDFS phải đổi sang lấy checksum từ manifest NiFi.
- Mô hình chỉ học nhãn khuyến nghị từ review tiếng Anh. Đây không phải phân tích cảm xúc và không áp dụng cho ngôn ngữ khác.
- Nhận xét từ gold chỉ mô tả dữ liệu quan sát, không suy ra nhân quả hay cho toàn bộ người chơi Steam.

---

## 8. Cách chạy lại (cho thành viên khác)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
# Windows: đặt HADOOP_HOME có bin\winutils.exe + bin\hadoop.dll (xem runbook)

.venv\Scripts\python.exe scripts\download_dataset.py
.venv\Scripts\python.exe scripts\profile_dataset.py
.\scripts\run_tv2.ps1 etl --source data\sample\smoke.csv --level smoke
.\scripts\run_tv2.ps1 ml-prepare  --run-id <run_id>
.\scripts\run_tv2.ps1 ml-train    --run-id <run_id>
.\scripts\run_tv2.ps1 ml-evaluate --run-id <run_id>
.venv\Scripts\python.exe -m pytest
```

Chi tiết đầu vào, đầu ra và exit code: [docs/runbooks/tv2_local_pipeline.md](docs/runbooks/tv2_local_pipeline.md).
