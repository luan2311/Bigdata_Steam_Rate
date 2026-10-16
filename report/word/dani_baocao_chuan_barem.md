# DÀN Ý CHI TIẾT BÁO CÁO ĐỒ ÁN MÔN HỌC: DỮ LIỆU LỚN (BIG DATA)
*(Khớp 100% theo chuẩn Barem: Lời nói đầu, Chương 1, Chương 2, Chương 3, Kết luận, Tài liệu tham khảo)*

---

## PHẦN ĐẦU
1. **Trang bìa chính:** Tên Trường, Khoa, Môn học, Tên đề tài, Giảng viên hướng dẫn, Thông tin 3 sinh viên, Năm học.
2. **Nhận xét của Giảng viên hướng dẫn.**
3. **Mục lục tự động:** Mục lục nội dung, Danh mục Bảng biểu, Danh mục Hình vẽ, Danh mục Từ viết tắt.
4. **Lịch làm việc và Bảng phân công đóng góp của nhóm:**
   * Bảng nhật ký công việc thực tế (D1 – D15 / Tuần 1 – 10).
   * Bảng tỷ lệ phần trăm đóng góp thống nhất giữa 3 thành viên (Tổng: 100%).

---

## LỜI NÓI ĐẦU *(TV3 chủ trì)*
* Lý do thực hiện đồ án môn học Dữ liệu lớn.
* Tổng quan về phạm vi nghiên cứu: Xử lý dữ liệu đánh giá Steam bằng cụm phân tán (NiFi, HDFS, Spark) và xây dựng ứng dụng trực quan hóa Dashboard.
* Lời cảm ơn gửi đến Giảng viên hướng dẫn và Bộ môn.

---

## CHƯƠNG 1: GIỚI THIỆU VÀ BÀI TOÁN *(TV3 chủ trì)*

### 1.1. Bối cảnh và Tính cấp thiết của đề tài
* Sự phát triển của thị trường phát hành game trực tuyến (Steam) và vai trò của phản hồi người dùng (User Reviews).
* Thách thức Big Data trong bài toán phân tích đánh giá: Dung lượng lớn, tốc độ tăng trưởng nhanh, nhiều đánh giá trùng lặp và tính phi cấu trúc của văn bản tự do.

### 1.2. Mục tiêu nghiên cứu của đề tài
* Xây dựng pipeline dữ liệu tự động, khép kín và có khả năng chạy lại (Reproducible): Thu thập $\rightarrow$ Lưu trữ $\rightarrow$ Tiền xử lý $\rightarrow$ Phân tích thống kê & Học máy $\rightarrow$ Trực quan hóa.
* Phát triển ứng dụng Dashboard đa chiều, hỗ trợ nhà phát hành và người chơi theo dõi chất lượng game.

### 1.3. 5 Câu hỏi phân tích cốt lõi (Core Research Questions)
* **Câu hỏi 1:** Trò chơi nào sở hữu lượng đánh giá cao và tỷ lệ khuyến nghị tích cực/tiêu cực nhất?
* **Câu hỏi 2:** Số lượng đánh giá và mức độ hài lòng của cộng đồng biến động như thế nào theo các mốc thời gian (tháng UTC)?
* **Câu hỏi 3:** Sự phân bố của các cộng đồng ngôn ngữ và sự khác biệt về tỷ lệ khuyến nghị giữa các nhóm là gì?
* **Câu hỏi 4:** Thời gian chơi tại thời điểm đánh giá (`playtime`) liên hệ như thế nào với quyết định khuyến nghị game?
* **Câu hỏi 5:** Mô hình học máy dựa trên nội dung bài viết tiếng Anh có khả năng dự đoán nhãn khuyến nghị tốt hơn Baseline đa số ở mức nào?

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ÁP DỤNG *(TV3 & TV2 chủ trì)*

### 2.1. Tổng quan về Tập dữ liệu (Dataset Overview)
* Nguồn dữ liệu: *Steam Reviews Dataset 2021* (từ Kaggle / Steam API), giấy phép mã nguồn mở GPL 2.
* Từ điển dữ liệu (Data Dictionary): Mô tả chi tiết kiểu dữ liệu và ý nghĩa của các trường: `review_id`, `app_id`, `app_name`, `review_text`, `recommended`, `language`, `timestamp_created`, `playtime_forever`...
* Chiến lược quy mô thử nghiệm (3 mức dữ liệu):
  * *Mức Smoke (10.000 dòng):* Kiểm thử thông luồng và bắt lỗi định dạng (Unicode, CSV xuống dòng).
  * *Mức Core (1.000.000 dòng):* Bộ dữ liệu chuẩn dùng để huấn luyện mô hình và đo đạc phân tích.
  * *Mức Full (~21.000.000 dòng):* Thử nghiệm xử lý toàn bộ và đo benchmark phân tán.

### 2.2. Cơ sở lý thuyết về Dữ liệu lớn (Big Data)
* Khái niệm Big Data và đặc trưng 4V trong bài toán Steam: Volume (Quy mô hàng chục triệu review), Velocity (Tốc độ sinh dữ liệu liên tục), Variety (Dữ liệu bảng kết hợp văn bản tự do), Veracity (Độ tin cậy, dữ liệu rác, đánh giá mỉa mai/ảo).
* Nguyên lý tính toán và lưu trữ phân tán.

### 2.3. Hệ thống lưu trữ phân tán Hadoop HDFS
* Kiến trúc Master/Worker: NameNode và DataNode.
* Cơ chế chia khối (Block Size 128MB) và nhân bản dữ liệu (Replication Factor = 2).

### 2.4. Nền tảng điều phối luồng dữ liệu Apache NiFi
* Khái niệm Lập trình hướng luồng (Flow-based Programming): FlowFile, Processor, Connection.
* Tính năng theo dõi phả hệ dữ liệu (Data Provenance) và cơ chế kiểm soát áp lực ngược (Back Pressure).

### 2.5. Khung tính toán phân tán Apache Spark & Spark MLlib
* Mô hình thực thi Driver và Worker, Spark Session, DataFrame và tối ưu hóa truy vấn Catalyst Optimizer.
* Thư viện học máy phân tán Spark MLlib: Pipeline, Transformer, Estimator.

### 2.6. Thư viện Trực quan hóa Streamlit & Plotly
* Kiến trúc ứng dụng Web tương tác hướng dữ liệu bằng Python.
* Khả năng kết xuất biểu đồ động đa chiều (Plotly).

### 2.7. Kiến trúc phần mềm Clean Architecture
* Nguyên lý phụ thuộc một chiều (Dependency Rule) và cấu trúc 4 tầng: Domain $\rightarrow$ Application $\rightarrow$ Infrastructure $\rightarrow$ Presentation.

---

## CHƯƠNG 3: THIẾT KẾ VÀ XÂY DỰNG HỆ THỐNG *(Trọng tâm đồ án)*

### 3.1. Thiết kế Kiến trúc Tổng thể Hệ thống *(TV1 chủ trì)*
* **3.1.1. Sơ đồ kiến trúc luồng dữ liệu (Data Pipeline Architecture):**
  * Luồng luân chuyển liên tục: `Landing CSV -> Apache NiFi -> HDFS Bronze -> Apache Spark -> HDFS Silver (Parquet) -> HDFS Gold -> Streamlit Dashboard`.
* **3.1.2. Ảo hóa cụm phân tán bằng Docker Compose:**
  * Cấu hình dịch vụ: 1 NiFi, 1 NameNode + 2 DataNode (HDFS), 1 Spark Master + 2 Spark Worker, 1 Streamlit App.
  * Bằng chứng vận hành cụm phân tán (`hdfs dfsadmin -report`, Spark Web UI).
* **3.1.3. Thiết kế luồng Ingestion bằng Apache NiFi:**
  * Chuỗi Processor: `ListFile` $\rightarrow$ `FetchFile` $\rightarrow$ `SplitRecord` (với `CSVReader` xử lý nhiều dòng, escape ký tự) $\rightarrow$ `InvokeHTTP` ghi WebHDFS.
  * Quản lý phân lô (`batch_id`), tạo `manifest` kiểm tra toàn vẹn và cơ chế cách ly lỗi (`Quarantine Queue`).

### 3.2. Tiền xử lý và Làm sạch Dữ liệu Phân tán (Spark ETL) *(TV2 chủ trì)*
* **3.2.1. Chuẩn hóa tầng Silver:**
  * Ép kiểu dữ liệu, chuẩn hóa thời gian UTC (`timestamp_created`), xử lý giá trị khuyết thiếu (Null/NaN).
* **3.2.2. Khử trùng lặp đa phiên bản (Deduplication):**
  * Thuật toán khử trùng dựa trên `review_id`, ưu tiên giữ bản ghi có thời điểm cập nhật mới nhất (`updated_at`).
* **3.2.3. Báo cáo đối soát chất lượng dữ liệu (`quality_summary`):**
  * Bảng phễu lọc: Số bản ghi thô $\rightarrow$ Hợp lệ $\rightarrow$ Trùng lặp $\rightarrow$ Cách ly theo từng nguyên nhân.
* **3.2.4. Lưu trữ tối ưu định dạng Parquet:**
  * Phân vùng dữ liệu (Partitioning) theo Năm/Tháng để tăng tốc độ truy vấn.

### 3.3. Phân tích Thống kê và Xây dựng Bảng Gold *(TV2 chủ trì, TV3 đối soát)*
* **3.3.1. Xây dựng 5 bảng tổng hợp Gold Layer:**
  * Bảng `game_summary`, `monthly_summary`, `language_summary`, `playtime_summary`.
* **3.3.2. Quy tắc nghiệp vụ và công thức tính toán:**
  * Công thức tính tỷ lệ khuyến nghị: $\text{Rate} = \frac{\text{Recommended Count}}{\text{Total Valid Reviews}}$.
  * Thiết lập ngưỡng mẫu số tối thiểu tin cậy: Mặc định $\ge 100$ lượt đánh giá mới đưa vào xếp hạng.

### 3.4. Xây dựng Mô hình Học máy Dự đoán Đánh giá (Spark MLlib) *(TV2 chủ trì)*
* **3.4.1. Định nghĩa bài toán & Phân chia tập dữ liệu chống rò rỉ:**
  * Bài toán phân loại nhị phân nhãn `recommended` (1/0) dựa trên văn bản tiếng Anh.
  * Hash-based Split theo tỷ lệ 70% Train / 15% Validation / 15% Test với seed cố định.
* **3.4.2. Xây dựng Pipeline NLP phân tán:**
  * `RegexTokenizer` $\rightarrow$ `StopWordsRemover` (giữ lại từ phủ định *not, no, never*) $\rightarrow$ `HashingTF` $\rightarrow$ `IDF` $\rightarrow$ `LogisticRegression`.
* **3.4.3. Đánh giá Mô hình trên Tập Test Độc lập:**
  * So sánh chi tiết Baseline (Majority Class) vs Logistic Regression: Accuracy, Precision, Recall, Macro-F1, PR-AUC.
  * Ma trận nhầm lẫn (Confusion Matrix).
* **3.4.4. Phân tích lỗi mô hình (Error Analysis):**
  * Trích xuất và phân tích định tính 30 trường hợp dự đoán sai (do ngôn ngữ mỉa mai, từ ngữ ngắn cụt lủn, đánh giá khen nhưng vote không khuyên).

### 3.5. Xây dựng Ứng dụng Trực quan hóa Dashboard *(TV3 chủ trì)*
* **3.5.1. Thiết kế Giao diện theo Clean Architecture:**
  * Tách biệt tầng Presentation qua DTO và Use Case; không import trực tiếp Spark Session hay HDFS client vào giao diện web.
* **3.5.2. Chi tiết 4 Màn hình Phân tích & Hệ thống Biểu đồ Plotly:**
  * *Trang 1: Tổng quan Thị trường:* KPI tổng thể, biểu đồ thanh Top 10 game, phân bố ngôn ngữ.
  * *Trang 2: Khám phá Trò chơi:* Bộ lọc tương tác (Slider ngưỡng $\ge 100$), bảng xếp hạng và biểu đồ đường xu hướng thời gian UTC.
  * *Trang 3: Thời gian chơi & Chất lượng dữ liệu:* Biểu đồ phễu làm sạch dữ liệu và biểu đồ nhóm giờ chơi $[0, 2h), [2h, 10h), \dots$
  * *Trang 4: Hiệu năng Mô hình ML:* Bảng metrics so sánh, Heatmap Confusion Matrix và bảng mẫu phân tích lỗi.
* **3.5.3. 5 Nhận xét Đột phá rút ra từ Dữ liệu thực tế:**
  * [TV3 trình bày 5 nhận xét có số liệu chứng minh cụ thể từ hệ thống biểu đồ].

### 3.6. Đối soát Số liệu, Đo lường Hiệu năng & Thử nghiệm Tái lập *(Cả 3 thành viên)*
* **3.6.1. Kiểm thử đối soát số liệu độc lập (TV3 & TV2):**
  * Bảng kiểm tra đối chiếu `Expected` (Spark SQL) vs `Actual` (Dashboard) trên ít nhất 3 tổ hợp bộ lọc.
* **3.6.2. Đo lường hiệu năng và Benchmark cụm (TV1 & TV2):**
  * So sánh tốc độ đọc ghi I/O của NiFi và thời gian chạy Spark Job giữa cấu hình 1 Worker và 2 Worker.
* **3.6.3. Thử nghiệm tái lập trên môi trường sạch (TV3 thực hiện theo README):**
  * Đánh giá khả năng dựng và chạy lại hệ thống từ đầu theo tài liệu hướng dẫn.

---

## KẾT LUẬN *(TV3 chủ trì)*
1. **Tổng kết kết quả đạt được:**
   * Hoàn thành 100% pipeline dữ liệu lớn phân tán khép kín từ NiFi $\rightarrow$ HDFS $\rightarrow$ Spark $\rightarrow$ Streamlit.
   * Giải quyết trọn vẹn 5 câu hỏi nghiên cứu ban đầu.
2. **Hạn chế của đề tài:**
   * Giới hạn tài nguyên phần cứng máy đơn nút (mô phỏng cụm container).
   * Mô hình Bag-of-Words (TF-IDF) chưa nắm bắt trọn vẹn ngữ cảnh ngữ nghĩa phức tạp như các mô hình Transformer hiện đại.
3. **Định hướng phát triển trong tương lai:**
   * Mở rộng luồng Ingestion Streaming thời gian thực với Apache Kafka.
   * Tích hợp các mô hình ngôn ngữ lớn (LLM / BERT) để phân tích cảm xúc và sắc thái đánh giá chuyên sâu.

---

## TÀI LIỆU THAM KHẢO *(TV3 chủ trì)*
* Tài liệu chính thức: Apache NiFi Documentation, Apache Hadoop HDFS Architecture Guide, Apache Spark Programming Guide.
* Nguồn dữ liệu: Kaggle Steam Reviews Dataset 2021.
* Các bài báo khoa học và tài liệu kỹ thuật liên quan (Định dạng chuẩn IEEE / APA).

---

## PHỤ LỤC *(TV3 chủ trì)*
* **Phụ lục A:** Hướng dẫn cài đặt và khởi chạy hệ thống từng bước từ môi trường sạch.
* **Phụ lục B:** File cấu hình Docker Compose mẫu cho cụm phân tán.
* **Phụ lục C:** Schema hợp đồng dữ liệu Gold Layer JSON v1.
