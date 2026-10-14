# Phân tích dữ liệu đánh giá trò chơi trên Steam

Bộ khung đồ án môn học **Nhập môn Big Data** dành cho **nhóm 3 sinh viên (TV1, TV2, TV3)**, thực hiện theo kế hoạch 10 tuần.  
Luồng dữ liệu tổng thể: **Kaggle Dataset → Apache NiFi → HDFS → Apache Spark (ETL & MLlib) → Streamlit Dashboard**.

**Trạng thái:** Đã thiết lập cấu trúc mã nguồn theo Clean Architecture, package Python và các tài liệu kế hoạch/phân công. Các thư mục đang giữ bằng `.gitkeep` và sẵn sàng triển khai.

> [!IMPORTANT]
> **Ba yêu cầu cố định của đồ án**
> - **Đề tài:** Phân tích dữ liệu đánh giá trò chơi trên Steam.
> - **Công cụ luồng dữ liệu:** [Apache NiFi](https://nifi.apache.org/index.html) — đường tiếp nhận duy nhất đưa dataset vào HDFS ([thiết kế luồng](Plan.md#34-luồng-apache-nifi-tv1-chủ-trì), [thư mục `nifi/`](nifi/README.md)).
> - **Dataset:** [Steam Reviews Dataset 2021 — najzeko (Kaggle)](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021/data) ([hợp đồng dữ liệu](Plan.md#33-dataset-steam-reviews-2021-và-hợp-đồng-dữ-liệu-v1)).

---

## 1. Căn cứ và Tài liệu làm việc

- [Plan.md](Plan.md): Kế hoạch chi tiết 10 tuần, ma trận rubric 6 tiêu chí (CLO1–CLO5), 2 mốc nộp bài (GĐ1: 30%, GĐ2: 70%) và tiêu chuẩn nghiệm thu.
- [Checklist.md](Checklist.md): Danh mục công việc chi tiết theo từng tuần cho 3 thành viên (TV1, TV2 và TV3).
- [Kiến trúc Clean Architecture](docs/architecture.md): Ranh giới các lớp, chiều phụ thuộc và quy tắc import mã nguồn.
- [Nhật ký đóng góp](docs/contributions.md): Mẫu theo dõi tiến độ hàng ngày, tổng hợp tuần và xác nhận tỷ lệ đóng góp của từng thành viên.

---

## 2. Phân công vai trò (Nhóm 3 sinh viên)

| Thành viên | Vai trò chính | Trách nhiệm & Sản phẩm bàn giao |
|---|---|---|
| **TV1** | **Kỹ sư Hạ tầng dữ liệu & Trực quan hóa** (Data Platform & App Engineer) | • Hạ tầng cụm phân tán (`infra/docker/`, `infra/hadoop/`, `infra/spark/`).<br>• Luồng thu thập & ingestion (`nifi/flows/`, `nifi/parameters/`, WebHDFS).<br>• Xây dựng Dashboard trực quan hóa (`src/steam_reviews/presentation/dashboard/`).<br>• Điều phối chung, hồ sơ báo cáo Word & Slide (`report/`). |
| **TV2** | **Kỹ sư Xử lý dữ liệu lớn & ML** (Big Data Processing & ML Engineer) | • Hợp đồng dữ liệu & quy tắc (`schemas/`, `src/steam_reviews/domain/`).<br>• Xử lý phân tán Spark ETL: Clean, Dedup, Gold (`src/steam_reviews/infrastructure/spark/`).<br>• Xây dựng và đánh giá mô hình phân loại Spark MLlib (`src/steam_reviews/infrastructure/ml/`).<br>• Phân tích lỗi, benchmark, kiểm soát độ đo & chất lượng dữ liệu. |
| **TV3** | **Kỹ sư Chất lượng dữ liệu & Báo cáo** (Data Quality & Documentation Engineer) | • Xây dựng fixture kiểm thử & test đối soát số liệu (`tests/fixtures/`, `tests/`).<br>• Đối soát số liệu Gold Layer và Dashboard (ít nhất 3 tổ hợp filter).<br>• Soạn thảo báo cáo Word: Cơ sở lý thuyết Big Data, Kết luận & Định hướng, Tài liệu tham khảo, Phụ lục. |

---

## 3. Cấu trúc thư mục dự án

```text
Bigdata/
├── src/steam_reviews/
│   ├── domain/
│   │   ├── entities/             # Khái niệm Review, Dataset, Run (thuần Python)
│   │   └── policies/             # Quy tắc nhãn, làm sạch, phân lớp, KPI
│   ├── application/
│   │   ├── ports/                # Hợp đồng giao tiếp (Protocol/ABC)
│   │   ├── dto/                  # Request/Response data transfer objects
│   │   └── use_cases/            # Use cases: Clean, Aggregate, Train, Evaluate, Query
│   ├── infrastructure/
│   │   ├── ingestion/            # Adapter metadata nguồn, checksum, manifest
│   │   ├── storage/              # Adapter lưu trữ HDFS và snapshot cục bộ
│   │   ├── spark/                # Adapter PySpark DataFrame & Spark SQL
│   │   └── ml/                   # Adapter Spark MLlib (TF-IDF + Logistic Regression)
│   ├── presentation/
│   │   ├── cli/                  # CLI entry point kích hoạt batch job
│   │   └── dashboard/            # Streamlit UI (4 trang, 6+ biểu đồ Plotly)
│   │       ├── pages/            # Trang chi tiết: Tổng quan, Trò chơi, Chất lượng, Mô hình
│   │       └── components/       # Bộ lọc, biểu đồ, metrics card
│   └── bootstrap/                # Composition root: Khởi tạo và liên kết các adapter
├── infra/
│   ├── docker/                   # Dockerfile & Docker Compose cho cụm
│   ├── hadoop/                   # Cấu hình HDFS (NameNode, 2 DataNodes)
│   └── spark/                    # Cấu hình Spark (Master, 2 Workers)
├── nifi/
│   ├── flows/                    # Template luồng NiFi JSON
│   └── parameters/               # Tham số cấu hình NiFi
├── schemas/
│   ├── source/                   # Schema dữ liệu gốc từ Kaggle
│   ├── silver/                   # Schema dữ liệu sau chuẩn hóa & dedup
│   └── gold/                     # Schema các bảng tổng hợp và metrics
├── tests/
│   ├── unit/                     # Unit test cho Domain & Use cases (fake ports)
│   ├── integration/              # Integration test cho Spark, HDFS, NiFi adapter
│   ├── e2e/                      # End-to-end pipeline test
│   └── fixtures/                 # Dữ liệu mẫu kiểm thử
├── scripts/                      # Script wrapper vận hành và submit job
├── data/
│   ├── landing/                  # Nơi chứa dataset gốc tải về
│   ├── sample/                   # Mẫu dữ liệu nhỏ phục vụ dev
│   └── cache/                    # Cache cục bộ
├── artifacts/
│   ├── manifests/                # Manifest nguồn, batch, run ID
│   ├── metrics/                  # Độ đo mô hình và hiệu năng
│   ├── figures/                  # Biểu đồ phục vụ báo cáo
│   ├── models/                   # Metadata/model lưu trữ (không commit Git)
│   └── snapshots/                # Snapshot dữ liệu cho dashboard
├── docs/
│   ├── architecture.md           # Thiết kế kiến trúc Clean Architecture
│   ├── contributions.md          # Bảng theo dõi phân công & đóng góp
│   ├── data/                     # Data dictionary và ghi chú lấy mẫu
│   ├── runbooks/                 # Hướng dẫn cài đặt, vận hành, sửa lỗi
│   └── evidence/                 # Bằng chứng kiểm thử và thực nghiệm
├── report/
│   ├── word/                     # File Word báo cáo (đủ 10 mục theo quy định)
│   ├── slides/                   # Slide thuyết trình (Giai đoạn 1 & Cuối kỳ)
│   └── demo/                     # Kịch bản demo và video dự phòng
├── Plan.md                       # Kế hoạch chi tiết 10 tuần
├── Checklist.md                  # Checklist công việc của 3 thành viên
└── README.md
```

---

## 4. Nguyên tắc cốt lõi

1. **Tuân thủ Clean Architecture:** Tầng `domain` và `application` hoàn toàn độc lập với framework/hạ tầng. `infrastructure` triển khai các ports bằng Spark/HDFS/NiFi. `presentation` (CLI, Streamlit) chỉ tương tác qua `use_cases`.
2. **Xử lý phân tán thực sự:** Giữ toàn bộ việc xử lý hàng triệu bản ghi trong Spark; không `collect()` toàn bộ dữ liệu lên driver. Dashboard chỉ đọc các bảng tổng hợp hoặc snapshot nhỏ ở tầng Gold.
3. **Quản lý dữ liệu lớn & phân vùng:** Dữ liệu phân tầng Bronze → Silver → Gold trên HDFS. Có cơ chế idempotent, dedup theo `review_id`, cô lập bản ghi lỗi (quarantine) và lưu trữ dạng Parquet tối ưu.
4. **Đánh giá mô hình chuẩn mực:** Xây dựng mô hình baseline đa số để so sánh với Logistic Regression (TF-IDF). Tách tập train/validation/test không để rò rỉ dữ liệu. Đánh giá đa chiều qua Macro-F1, Precision, Recall, PR-AUC và phân tích lỗi.
5. **Hồ sơ minh bạch:** Mọi kết quả, độ đo và biểu đồ đều từ thực nghiệm thực tế, có thể tái lập; không dùng số liệu giả định.
