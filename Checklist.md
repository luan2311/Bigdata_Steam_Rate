# CHECKLIST CÔNG VIỆC — NHÓM 2 SINH VIÊN / 10 TUẦN
## ĐỀ TÀI: PHÂN TÍCH DỮ LIỆU ĐÁNH GIÁ TRÒ CHƠI TRÊN STEAM

- **Căn cứ kế hoạch:** [Plan.md](Plan.md), quy định học phần Nhập môn Big Data, [kiến trúc mã nguồn](docs/architecture.md).
- **Yêu cầu cố định:** luồng tiếp nhận dùng [Apache NiFi](https://nifi.apache.org/index.html); dữ liệu duy nhất là [Steam Reviews Dataset 2021 — najzeko (Kaggle)](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021/data).
- **Phân công nhóm 2 người:**
  - **TV1:** Kỹ sư Hạ tầng dữ liệu, NiFi Ingestion, HDFS Storage, Streamlit Dashboard UI và Điều phối hồ sơ.
  - **TV2:** Kỹ sư Hợp đồng dữ liệu, Spark Processing (Clean & Gold ETL), Spark MLlib (Baseline & Logistic Regression), Đánh giá & Đối soát.
- **Quy tắc nghiệm thu:** Chỉ chuyển `[ ]` thành `[x]` khi đã có sản phẩm thực tế, có người review chéo xác nhận và được lưu vết trong `docs/contributions.md`.

---

## 1. TV1 — Hạ tầng phân tán, Thu thập dữ liệu (NiFi), Dashboard & Điều phối

**Khu vực phụ trách chính:** `infra/`, `nifi/`, `src/steam_reviews/infrastructure/ingestion/`, `src/steam_reviews/infrastructure/storage/`, `src/steam_reviews/presentation/dashboard/`, `src/steam_reviews/bootstrap/`, `report/slides/`, `report/demo/`.  
**Người review chéo:** TV2.

### Giai đoạn chuẩn bị (Tuần 1–3)
- [ ] **TV1-W01 — Thiết lập dự án & Quy ước nhóm:** Khởi tạo Git repo, cấu trúc thư mục Clean Architecture, thiết lập tài liệu làm việc, thống nhất phân công 2 thành viên. **Đạt khi:** Repo có đầy đủ khung thư mục, file cấu hình và tài liệu khởi tạo.
- [ ] **TV1-W02 — Nghiên cứu công nghệ hạ tầng:** Khảo sát cài đặt Docker Compose cho cụm Big Data (Hadoop HDFS, Spark, NiFi), đánh giá dung lượng RAM/disk máy thực thi. **Đầu ra:** Ghi nhận cấu hình tài nguyên khả thi trong `docs/runbooks/`.
- [ ] **TV1-W03 — Hoàn thiện kế hoạch chi tiết:** Cùng TV2 chốt đề tài, phạm vi dữ liệu, 5 câu hỏi phân tích và kế hoạch 10 tuần. **Đạt khi:** Bản kế hoạch được giáo viên chấp thuận.

### Giai đoạn Lý thuyết & Thiết kế giải pháp (Tuần 4–5)
- [ ] **TV1-W04 — Soạn thảo cơ sở lý thuyết hạ tầng:** Viết phần lý thuyết về hệ thống tệp phân tán Hadoop HDFS (NameNode, DataNode, Block, Replication) và cơ chế Ingestion của Apache NiFi vào báo cáo Word. **Đầu ra:** Bản thảo mục Cơ sở lý thuyết hạ tầng trong báo cáo Word.
- [ ] **TV1-W05 — Dựng cụm phân tán bằng Docker Compose:** Tạo file cấu hình `infra/docker/docker-compose.yml` gồm: 1 NiFi, 1 HDFS NameNode + 2 DataNodes, 1 Spark Master + 2 Workers. **Đạt khi:** Khởi động thành công toàn bộ container, truy cập được Web UI của HDFS (:9870), Spark (:8080), NiFi (HTTPS :8443; không dùng :8080 vì trùng Spark).
- [ ] **TV1-W06 — Xây dựng luồng NiFi Ingestion mẫu:** Thiết lập luồng tiếp nhận `ListFile → FetchFile → SplitRecord → InvokeHTTP (WebHDFS)`. **Đạt khi:** Đẩy thành công ~10.000 bản ghi mẫu vào HDFS `/steam/bronze/` mà không làm vỡ các dòng CSV có chứa ký tự xuống dòng hoặc Unicode; export template JSON vào `nifi/flows/`.

### Giai đoạn 1: Baseline & Báo cáo tiến độ (Tuần 6–7) — Chiếm 30% điểm đồ án
- [ ] **TV1-W07 — Hoàn thiện luồng Ingestion đáng tin cậy:** Bổ sung cơ chế chia lô (batching ~50.000 record/lô), xử lý lỗi cấu trúc qua Quarantine queue, giới hạn retry (tối đa 3 lần), chống nghẽn (back pressure) và tạo manifest kiểm soát lô. **Đạt khi:** Luồng chạy ổn định, có log chứng minh xử lý lỗi và provenance; export flow hoàn chỉnh.
- [ ] **TV1-W08 — Nạp Core Tier vào HDFS:** Nạp tập dữ liệu Core (~1.000.000 bản ghi) vào HDFS Bronze, lưu trữ bằng chứng phân tán (báo cáo block replication, dung lượng DataNode qua `hdfs dfsadmin -report`). **Đầu ra:** Bằng chứng log/ảnh lưu tại `docs/evidence/`.
- [ ] **TV1-W09 — Thiết kế khung giao diện Dashboard:** Dựng khung ứng dụng Streamlit trong `src/steam_reviews/presentation/dashboard/` với 4 trang điều hướng, cấu hình theme và components hiển thị thử nghiệm với fixture nhỏ. **Đạt khi:** Dashboard chạy mượt mà, độc lập, không import trực tiếp Spark driver.
- [ ] **TV1-W10 — Hoàn thiện hồ sơ Báo cáo tiến độ GĐ1:** Viết phần Hạ tầng, NiFi, HDFS trong báo cáo Word; tổng hợp slide thuyết trình tiến độ Giai đoạn 1. **Đạt khi:** Hồ sơ báo cáo tiến độ Giai đoạn 1 hoàn thành đúng hạn quy định (Tuần 6–7).

### Giai đoạn 2: Hoàn thiện ứng dụng, Đánh giá & Báo cáo hoàn chỉnh (Tuần 8–9) — Chiếm 70% điểm đồ án
- [ ] **TV1-W11 — Kết nối Dashboard với dữ liệu Gold thực tế:** Triển khai nạp dữ liệu từ snapshot Gold/Parquet thông qua các DTO và use cases. Đảm bảo Dashboard hiển thị đầy đủ thông tin: nguồn dữ liệu, quy mô mẫu, `run_id`. **Đạt khi:** Không còn sử dụng dữ liệu giả (fixture), mọi chỉ số hiển thị khớp với số liệu của TV2.
- [ ] **TV1-W12 — Hoàn thiện 4 trang Dashboard chi tiết:**
  - *Trang 1: Tổng quan:* Số lượng review, số game, khoảng thời gian, biểu đồ phân bố game và ngôn ngữ.
  - *Trang 2: Khám phá trò chơi:* Bảng xếp hạng game theo tỷ lệ khuyến nghị có bộ lọc ngưỡng số đánh giá, biểu đồ xu hướng theo tháng.
  - *Trang 3: Thời lượng chơi & Chất lượng:* Biểu đồ tỷ lệ khuyến nghị theo các khoảng thời lượng chơi, biểu đồ thống kê chất lượng dữ liệu (thiếu/trùng/lỗi).
  - *Trang 4: Hiệu năng mô hình:* Trực quan hóa ma trận nhầm lẫn (Confusion Matrix), so sánh Baseline vs Logistic Regression, ví dụ dự đoán đã tính sẵn từ test set (nhập văn bản dự đoán trực tiếp chỉ là phần mở rộng, không khởi chạy Spark trong dashboard).  
  **Đạt khi:** Đạt tối thiểu 6 biểu đồ Plotly tương tác, có xử lý trạng thái rỗng (empty state) khi lọc dữ liệu.
- [ ] **TV1-W13 — Đo đạc hiệu năng & Benchmark hạ tầng:** Đo thời gian xử lý Ingestion, throughput (bản ghi/giây), tiêu thụ RAM/CPU; benchmark so sánh hiệu năng chạy Spark với 1 worker vs 2 workers trên cùng cấu hình dữ liệu. **Đầu ra:** Bảng số liệu benchmark lưu tại `artifacts/metrics/`.
- [ ] **TV1-W14 — Đóng gói hồ sơ & Nộp bài Giai đoạn 2:** Soạn thảo hướng dẫn cài đặt/vận hành chi tiết trong `README.md` và `docs/runbooks/`; hoàn thiện toàn bộ slide thuyết trình cuối kỳ (.pptx); rà soát kỹ thuật cùng TV2 và nộp đầy đủ trên Classroom trước hạn chót Tuần 9. **Đạt khi:** Nộp đủ Source Code, File Word, File PPT và lưu minh chứng nộp bài.

### Tuần 10: Thuyết trình & Demo sản phẩm
- [ ] **TV1-W15 — Diễn tập thuyết trình & Kịch bản Demo:** Chuẩn bị kịch bản demo (8–10 phút); thiết lập môi trường demo offline (snapshot dữ liệu dự phòng, video demo chất lượng cao phòng sự cố). **Đạt khi:** Trình bày tự tin phần hạ tầng, luồng thu thập và demo dashboard trực quan trước lớp.

---

## 2. TV2 — Hợp đồng dữ liệu, Spark Processing, Mô hình MLlib & Đánh giá

**Khu vực phụ trách chính:** `schemas/`, `src/steam_reviews/domain/`, `src/steam_reviews/application/`, `src/steam_reviews/infrastructure/spark/`, `src/steam_reviews/infrastructure/ml/`, `src/steam_reviews/presentation/cli/`, `artifacts/metrics/`, `artifacts/models/`.  
**Người review chéo:** TV1.

### Giai đoạn chuẩn bị (Tuần 1–3)
- [ ] **TV2-W01 — Khảo sát Dataset Steam Reviews:** Tải mẫu dữ liệu từ Kaggle, kiểm tra danh sách cột thực tế, xác định các trường dữ liệu quan trọng (`review_id`, `app_id`, `review`, `recommended`, `language`, `timestamp_created`, `author.playtime_at_review`). **Đầu ra:** Ghi chú khảo sát dữ liệu trong `docs/data/`.
- [ ] **TV2-W02 — Xây dựng Data Dictionary & Hợp đồng dữ liệu v1:** Thiết lập từ điển dữ liệu, định nghĩa schema cho 3 tầng: `schemas/source/`, `schemas/silver/`, `schemas/gold/`. **Đạt khi:** Quy định rõ kiểu dữ liệu, ràng buộc nullable, đơn vị tính và logic từng bảng.
- [ ] **TV2-W03 — Định hình bài toán & Nghiệp vụ Domain:** Viết các entities và policies thuần Python trong `src/steam_reviews/domain/` (chính sách phân loại nhãn, tiêu chuẩn làm sạch, cách tính tỷ lệ khuyến nghị an toàn mẫu số 0). **Đạt khi:** Tầng domain hoàn toàn độc lập với Spark và các framework ngoài.

### Giai đoạn Lý thuyết & Thiết kế giải pháp (Tuần 4–5)
- [ ] **TV2-W04 — Soạn thảo cơ sở lý thuyết Xử lý & Học máy:** Viết phần lý thuyết về kiến trúc xử lý phân tán Apache Spark (Driver, Executor, Catalyst Optimizer), xử lý văn bản (TF-IDF), phân loại Logistic Regression và các độ đo đánh giá (Macro-F1, Precision, Recall, PR-AUC). **Đầu ra:** Bản thảo mục Cơ sở lý thuyết xử lý dữ liệu và thuật toán trong báo cáo Word.
- [ ] **TV2-W05 — Thiết kế tầng Application & Use Cases:** Khai báo các Protocol/Ports (`ReviewBatchProcessor`, `ModelTrainer`, `AnalyticsReader`), DTOs và Use cases (`CleanReviews`, `BuildAnalytics`, `TrainRecommendationModel`). **Đạt khi:** Không import PySpark hay thư viện hạ tầng vào tầng Application.
- [ ] **TV2-W06 — Xây dựng Spark ETL Smoke Job:** Viết adapter PySpark đọc dữ liệu Bronze từ HDFS, thực hiện ép kiểu an toàn, xử lý chuỗi thời gian UTC, ghi nhận bản ghi lỗi. **Đạt khi:** Chạy thông suốt với dữ liệu mẫu smoke test qua CLI.

### Giai đoạn 1: Baseline & Báo cáo tiến độ (Tuần 6–7) — Chiếm 30% điểm đồ án
- [ ] **TV2-W07 — Xây dựng quy trình làm sạch & Dedup phân tán:** Xây dựng Spark job lọc các bản ghi vi phạm cấu trúc, deduplication toàn diện theo `review_id` (giữ bản ghi có `updated_at` mới nhất), ghi dữ liệu sạch sang HDFS Silver (`/steam/silver/`) dưới định dạng Parquet. **Đạt khi:** Có bảng thống kê đối soát số lượng trước và sau làm sạch/dedup.
- [ ] **TV2-W08 — Xây dựng mô hình Baseline:** Lấy tập đánh giá tiếng Anh hợp lệ từ Silver; phân chia Train / Validation / Test (70/15/15) bằng hàm hash của nội dung văn bản (ngăn chặn rò rỉ dữ liệu). Xây dựng mô hình Baseline luôn dự đoán lớp đa số trên tập train. **Đầu ra:** Split manifest và kết quả độ đo baseline trên validation set.
- [ ] **TV2-W09 — Đánh giá sơ bộ & Xác định hướng cải thiện:** Đánh giá điểm mạnh/yếu của baseline, phân tích hiện tượng mất cân bằng nhãn (imbalance) của dữ liệu đánh giá; vạch ra phương án xử lý trọng số lớp và trích xuất đặc trưng văn bản. **Đầu ra:** Báo cáo đánh giá sơ bộ đưa vào hồ sơ tiến độ.
- [ ] **TV2-W10 — Soạn thảo nội dung Báo cáo tiến độ GĐ1:** Viết các mục Giới thiệu đề tài, Khảo sát dữ liệu, Quy trình tiền xử lý Spark và Kết quả baseline trong báo cáo Word. **Đạt khi:** Cùng TV1 hoàn thiện và nộp hồ sơ Giai đoạn 1 đúng hạn (Tuần 6–7).

### Giai đoạn 2: Hoàn thiện ứng dụng, Đánh giá & Báo cáo hoàn chỉnh (Tuần 8–9) — Chiếm 70% điểm đồ án
- [ ] **TV2-W11 — Hoàn thiện Pipeline Spark MLlib:** Xây dựng quy trình máy học phân tán: `RegexTokenizer → StopWordsRemover (giữ từ phủ định) → HashingTF → IDF → LogisticRegression`. Fit IDF và mô hình chỉ trên tập Train. Thử nghiệm có và không có trọng số lớp (`classWeightCol`). **Đạt khi:** Lưu model và pipeline hoàn chỉnh vào `artifacts/models/`.
- [ ] **TV2-W12 — Tinh chỉnh tham số & Đánh giá khách quan:** Tinh chỉnh tham số (regParam, maxIter) trên validation set để chọn mô hình tốt nhất theo Macro-F1. Sau khi chốt mô hình, đánh giá lần duy nhất trên Test set; tính toán Precision, Recall, Macro-F1, PR-AUC và Confusion Matrix. **Đạt khi:** Bảng kết quả đối sánh chi tiết Baseline vs Logistic Regression được lưu trong `artifacts/metrics/`.
- [ ] **TV2-W13 — Phân tích lỗi (Error Analysis) & Hạn chế:** Trích xuất và phân tích định tính ~30 trường hợp mô hình dự đoán sai (do ngôn ngữ mỉa mai, từ ngữ ngắn cụt ngủn, đánh giá tích cực nhưng nhãn không khuyến nghị hoặc ngược lại). Chỉ ra các hạn chế kỹ thuật của phương pháp Bag-of-Words. **Đầu ra:** Bản phân tích lỗi chi tiết đưa vào báo cáo Word.
- [ ] **TV2-W14 — Tính toán các bảng tổng hợp Gold Layer:** Sử dụng Spark SQL tính toán 5 bảng tổng hợp (`quality_summary`, `game_summary`, `monthly_summary`, `language_summary`, `playtime_summary`), lưu dưới dạng Parquet trên HDFS Gold và xuất snapshot nhỏ cho Dashboard của TV1. **Đạt khi:** Số liệu đối soát chính xác 100% với các truy vấn độc lập.
- [ ] **TV2-W15 — Rà soát báo cáo & Nộp bài Giai đoạn 2:** Soạn thảo mục Kết quả thực nghiệm, Đánh giá mô hình, Phân tích lỗi và Kết luận/Định hướng phát triển trong báo cáo Word; rà soát đảm bảo đủ 10 mục theo quy định; cùng TV1 nộp bài trên Classroom đúng hạn Tuần 9. **Đạt khi:** Hoàn thành toàn diện báo cáo Word và kiểm tra chéo toàn bộ kết quả.

### Tuần 10: Thuyết trình & Demo sản phẩm
- [ ] **TV2-W16 — Báo cáo kỹ thuật & Trả lời phản biện:** Trình bày phần xử lý dữ liệu Spark, thuật toán MLlib, kết quả đánh giá mô hình và phân tích lỗi trước lớp; chuẩn bị trả lời sâu các câu hỏi phản biện của giảng viên về mặt kỹ thuật, thuật toán và độ đo. **Đạt khi:** Buổi báo cáo thành công, phản biện xuất sắc.

---

## 3. Ma trận bàn giao công việc giữa 2 thành viên

| Mốc thời gian | Người giao → Người nhận | Sản phẩm bàn giao cụ thể | Điều kiện bắt đầu của người nhận |
|---|---|---|---|
| **Cuối Tuần 3** | TV2 → TV1 | Danh sách trường dữ liệu, Schema v1, Data Dictionary | TV1 có căn cứ cấu hình `CSVReader` và định dạng lô trong NiFi. |
| **Cuối Tuần 5** | TV1 → TV2 | Cụm container hoạt động, dữ liệu mẫu đã vào HDFS Bronze | TV2 có dữ liệu trên HDFS để viết và chạy thử Spark ETL. |
| **Cuối Tuần 6** | TV2 → TV1 | Bảng dữ liệu Silver và kết quả mô hình Baseline sơ bộ | TV1 có số liệu và wireframe để hoàn thiện slide tiến độ GĐ1. |
| **Cuối Tuần 7** | Cả hai | **NỘP BÁO CÁO TIẾN ĐỘ GIAI ĐOẠN 1 (30% điểm đồ án)** | Nộp đúng hạn quy định trên Classroom. |
| **Cuối Tuần 8** | TV2 → TV1 | Các bảng Gold summary và Metrics mô hình MLlib hoàn chỉnh | TV1 có số liệu thực tế để gắn vào các trang Dashboard Streamlit. |
| **Giữa Tuần 9** | TV1 → TV2 | Ứng dụng Dashboard hoàn chỉnh, số liệu đo hiệu năng cụm | TV2 kiểm tra đối soát chéo số liệu hiển thị với kết quả Spark SQL. |
| **Cuối Tuần 9** | Cả hai | **NỘP BÁO CÁO HOÀN CHỈNH GIAI ĐOẠN 2 (70% điểm đồ án)** | Nộp đủ Source Code, File Word, File PPT trên Classroom. |
| **Tuần 10** | Cả hai | **THUYẾT TRÌNH & DEMO SẢN PHẨM TRƯỚC LỚP** | Demo mượt mà, slide rõ ràng, phản biện tốt. |

---

## 4. Danh mục nghiệm thu các mốc lớn (Milestones)

- [ ] **M1 (Tuần 3):** Hoàn thành kế hoạch chi tiết, đề tài được phê duyệt, thiết lập repo chuẩn Clean Architecture.
- [ ] **M2 (Tuần 5):** Khởi chạy thành công cụm Docker (HDFS + Spark + NiFi), kiểm thử luồng Ingestion mẫu thông suốt.
- [ ] **M3 (Tuần 7):** Hoàn thành Baseline model, nạp dữ liệu Silver, **nộp thành công Báo cáo tiến độ Giai đoạn 1**.
- [ ] **M4 (Tuần 8):** Huấn luyện xong mô hình Spark MLlib, hoàn thành Error Analysis, tính toán toàn bộ bảng Gold.
- [ ] **M5 (Tuần 9):** Hoàn thành Dashboard Streamlit 4 trang, đối soát khớp 100% số liệu, hoàn thiện file Word 10 mục và Slide PPT, **nộp thành công Báo cáo hoàn chỉnh Giai đoạn 2**.
- [ ] **M6 (Tuần 10):** Hoàn thành buổi thuyết trình và demo trước lớp, nghiệm thu toàn bộ đồ án.
