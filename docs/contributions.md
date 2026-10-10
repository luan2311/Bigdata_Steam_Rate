# Nhật ký và đóng góp của nhóm (3 sinh viên)

## 1. Thành viên

| Mã | Họ tên | MSSV | Vai trò chính | Người review chéo |
|---|---|---|---|---|
| **TV1** | Chưa điền | Chưa điền | Hạ tầng (Docker, HDFS), Ingestion (NiFi), Dashboard (Streamlit/Plotly), Điều phối & Hồ sơ | TV2, TV3 |
| **TV2** | Chưa điền | Chưa điền | Hợp đồng dữ liệu (Schema), Spark ETL/Processing, Spark MLlib, Metrics & Đánh giá | TV1, TV3 |
| **TV3** | Chưa điền | Chưa điền | Chất lượng dữ liệu (Fixture, Đối soát), Soạn thảo báo cáo (Cơ sở lý thuyết, Kết luận, TLTK, Phụ lục) | TV1, TV2 |

## 2. Nhật ký làm việc hàng ngày

Thêm dòng cho mỗi công việc thực hiện. Sử dụng mã nhiệm vụ trong `Checklist.md`. Đường dẫn bằng chứng là tệp trong repo, commit hoặc log/ảnh thực nghiệm.

| Ngày thực tế | Tuần học phần | Thành viên | Mã nhiệm vụ | Công việc đã làm | Giờ thực tế | Sản phẩm / Bằng chứng | Người review & Kết quả | Vướng mắc / Bước tiếp theo |
|---|---|---|---|---|---|---|---|---|
| 01/10/2026 | Tuần 1 | TV1 | TV1-W01 | Khởi tạo Git repo, khung thư mục Clean Architecture, thiết lập pyproject.toml, README.md, docs/architecture.md, thống nhất phân công 3 thành viên. | 6h | Cấu trúc repo, `pyproject.toml`, `docs/architecture.md`, `Plan.md` | TV2: Đạt chuẩn Clean Architecture | Sẵn sàng khảo sát hạ tầng |
| 05/10/2026 | Tuần 2 | TV1 | TV1-W02 | Khảo sát thông số phần cứng thực tế (Ryzen 7 4800H 8C/16T, 24GB RAM, SSD trống 77.6GB), lập bảng sizing phân bổ tài nguyên cho cụm Docker Compose 7 container (NiFi 2.x, HDFS 1 NameNode + 2 DataNodes, Spark Master + 2 Workers). | 8h | `docs/runbooks/infrastructure-sizing-runbook.md` | TV2: Khả thi, thống nhất cổng không xung đột | Chuẩn bị viết docker-compose.yml ở Tuần 4 |
| 10/10/2026 | Tuần 3 | TV1 | TV1-W03 | Cùng TV2 & TV3 chốt đề tài Phân tích đánh giá Steam, phạm vi dữ liệu (Kaggle ~8.17 GB CSV, 3 tiers Smoke/Core/Full), 5 câu hỏi phân tích và hoàn thiện kế hoạch chi tiết 10 tuần. | 6h | `Plan.md`, `Checklist.md`, `data/landing/steam_reviews.csv` | TV2, TV3: Thống nhất kế hoạch và ma trận bàn giao | Trình giảng viên phê duyệt mốc M1 |
| 03/10/2026 | Tuần 1 | TV2 | TV2-W01 | Khảo sát chi tiết bộ dữ liệu Steam Reviews 2021 (8.17 GB, 23 cột), đo đạc thống kê mẫu 10k bản ghi (The Witcher 3: 97.1% True / 2.9% False, phát hiện Class Imbalance, 41 bản ghi null văn bản), xác định 7 trường dữ liệu trọng tâm. | 6h | `docs/data/dataset_survey_notes.md` | TV1, TV3: Đạt chuẩn khảo sát dữ liệu thực tế | Chuyển sang thiết kế Data Dictionary & Schema |
| 06/10/2026 | Tuần 2 | TV2 | TV2-W02 | Xây dựng Data Dictionary v1 và thiết kế trọn bộ hợp đồng dữ liệu chuẩn JSON Schema cho 3 tầng: Source (CSV thô 23 cột), Silver (Parquet sạch), và 6 bảng Gold (quality, game, monthly, language, playtime, model_metrics). | 8h | `docs/data/data_dictionary.md`, `schemas/source/`, `schemas/silver/`, `schemas/gold/` | TV1, TV3: Thống nhất contract giữa NiFi, Spark và UI | Chuyển sang định hình Domain logic |
| 09/10/2026 | Tuần 3 | TV2 | TV2-W03 | Định hình tầng Domain độc lập 100% với Spark: tạo các Entities (Review, AuthorInfo, GameSummary, RunMetadata) và Policies (xử lý nhãn, an toàn mẫu số 0, làm sạch text, phân nhóm playtime). Viết 19 unit tests đạt 100% PASS. | 8h | `src/steam_reviews/domain/`, `tests/unit/test_domain_policies.py`, `tests/unit/test_domain_entities.py` | TV1, TV3: Đạt chuẩn Clean Architecture | Sẵn sàng cho Giai đoạn Lý thuyết (Tuần 4–5) |
| 10/10/2026 | Tuần 4 | TV1 | TV1-W04 | Soạn thảo cơ sở lý thuyết hạ tầng lưu trữ phân tán Hadoop HDFS (Master/Worker, 128MB Block, Replication, WebHDFS REST) và nền tảng Apache NiFi (FlowFile, Flow-Based Programming, Record-Oriented CSVReader, Back Pressure, Quarantine). | 7h | `report/word/draft_co_so_ly_thuyet_ha_tang.md`, `report/word/TV1-W04_Co_So_Ly_Thuyet_Ha_Tang.docx` | TV2, TV3: Đạt chuẩn học thuật, tích hợp vào Mục 6 | Chuẩn bị triển khai Docker Compose |
| 10/10/2026 | Tuần 4 | TV1 | TV1-W05 | Dựng cụm phân tán qua Docker Compose gồm 7 container (NiFi, HDFS NameNode + 2 DataNodes, Spark Master + 2 Workers). Cấu hình core-site.xml, hdfs-site.xml, scripts khởi động, phân bổ cổng tránh xung đột (:8443 NiFi vs :8080 Spark). | 8h | `infra/docker/docker-compose.yml`, `infra/hadoop/core-site.xml`, `infra/hadoop/hdfs-site.xml`, `docs/runbooks/cluster-deployment-runbook.md` | TV2, TV3: Đạt chuẩn mô phỏng cụm phân tán | Chuyển sang xây dựng luồng Ingestion mẫu |
| 10/10/2026 | Tuần 5 | TV1 | TV1-W06 | Xây dựng luồng tiếp nhận mẫu Apache NiFi (ListFile -> FetchFile -> SplitRecord -> UpdateAttribute -> InvokeHTTP WebHDFS -> Quarantine). Trích xuất an toàn 10.000 logical records mẫu (19.799 dòng text, bảo toàn multiline và UTF-8) và viết script tự động hoá nạp WebHDFS. | 8h | `data/sample/steam_reviews_sample_10k.csv`, `nifi/flows/steam_reviews_ingestion_sample_flow.json`, `nifi/parameters/ingestion_params.json`, `scripts/ingest_sample_to_hdfs.py` | TV2, TV3: Đạt chuẩn Ingestion bảo toàn multiline | Sẵn sàng cho Giai đoạn 1 (Tuần 6–7) |

## 3. Tổng hợp tiến độ theo tuần (Khung 10 tuần)

| Giai đoạn | Tuần | TV1 (Hạ tầng, NiFi, Dashboard) | TV2 (Spark ETL, MLlib, Phân tích) | TV3 (Chất lượng, Kiểm thử, Báo cáo) | Mốc nghiệm thu | Điều chỉnh (nếu có) |
|---|---|---|---|---|---|---|
| **Giai đoạn chuẩn bị** | Tuần 1–3 | Phân công, lập kế hoạch chi tiết, chuẩn bị hạ tầng container | Chọn bài toán, khảo sát dataset Steam Reviews, phác thảo pipeline | Nghiên cứu quy định, xây dựng fixture kiểm thử, khung báo cáo | Đề tài được duyệt; Kế hoạch chi tiết hoàn chỉnh | — |
| **Lý thuyết & Thiết kế** | Tuần 4–5 | Dựng môi trường cụm (HDFS/NiFi/Spark), xây luồng NiFi mẫu vào WebHDFS | Khảo sát dữ liệu, chốt Schema v1, viết tài liệu thuật toán (TF-IDF + LR) | Soạn lý thuyết Big Data, thiết kế khung báo cáo Word 10 mục | Tài liệu tóm tắt thuật toán & ví dụ; Smoke cluster chạy thông suốt | — |
| **Giai đoạn 1 (30% điểm đồ án)** | Tuần 6–7 | Hoàn thiện luồng NiFi có chia lô/retry/manifest, nạp bronze/silver; demo hạ tầng | Xây dựng baseline model, đánh giá sơ bộ, xác định điểm cần cải thiện | Viết test đối soát ETL, soạn mục Giới thiệu & Cơ sở lý thuyết GĐ1 | **Báo cáo tiến độ GĐ1 nộp Tuần 6-7** (CLO1, CLO2) | — |
| **Hoàn thiện & Giai đoạn 2 (70% điểm đồ án)** | Tuần 8–9 | Hoàn thiện Dashboard 4 trang, kết nối Gold data, viết báo cáo Word & Slide | Tối ưu mô hình MLlib, phân tích lỗi, đối soát số liệu Gold | Đối soát Dashboard vs Gold, soạn Kết luận & TLTK & Phụ lục | **Báo cáo hoàn chỉnh GĐ2 nộp Tuần 9** (Source code, Word, PPT) | — |
| **Báo cáo cuối kỳ** | Tuần 10 | Chuẩn bị kịch bản Demo, diễn tập thuyết trình, kiểm tra môi trường offline | Chuẩn bị trả lời phản biện về dữ liệu, Spark MLlib và thuật toán | Trình bày phần Cơ sở lý thuyết & Kết luận, trả lời phản biện lý thuyết | **Thuyết trình & Demo trước lớp** (CLO3, CLO4, CLO5) | — |

## 4. Bảng phân công và tỷ lệ đóng góp cuối kỳ

| Thành viên | Sản phẩm chính đã nghiệm thu | Giờ thực tế | Tỷ lệ đóng góp thống nhất | Xác nhận của nhóm |
|---|---|---|---|---|
| **TV1** | Hạ tầng cụm, Luồng NiFi, Dashboard Streamlit, Hồ sơ Word & PPT | — | ≈ 33% | [ ] Đồng thuận |
| **TV2** | Schema, Pipeline Spark ETL, Mô hình Spark MLlib, Metrics & Đánh giá | — | ≈ 33% | [ ] Đồng thuận |
| **TV3** | Fixture kiểm thử, Đối soát số liệu, Báo cáo (Cơ sở lý thuyết, Kết luận, TLTK, Phụ lục) | — | ≈ 34% | [ ] Đồng thuận |

*Ghi chú: Tỷ lệ đóng góp đánh giá dựa trên toàn bộ quá trình (kỹ thuật, tài liệu, review, thuyết trình), tổng ba thành viên phải đạt 100%.*
