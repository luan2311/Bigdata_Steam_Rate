# Kế hoạch nạp tuần tự toàn bộ dataset Steam Reviews và vận hành toàn diện dự án

## Goal
Nạp tuần tự toàn bộ 21,7+ triệu bản ghi (8,17 GB) từ `data/landing/steam_reviews.csv` vào HDFS Bronze qua WebHDFS REST API theo cơ chế phân lô (batching) không tràn bộ nhớ, sau đó thực thi trọn vẹn luồng Spark ETL, MLlib Pipeline, trích xuất Snapshot và kiểm chứng Dashboard.

## Tasks
- [x] Task 1: Kiểm tra sức khỏe cụm phân tán Docker và kiểm định mã nguồn → Verify: `docker compose -f infra/docker/docker-compose.yml ps` (7 container running) và `py -3.13 -m pytest tests/unit` (58 passed).
- [x] Task 2: Xây dựng script nạp tuần tự streaming (`scripts/ingest_full_to_hdfs.py`) chia lô 100.000 dòng/lô, tự động xử lý WebHDFS redirect 307 và ghi manifest → Verify: `py -3.13 scripts/ingest_full_to_hdfs.py --help` chạy thành công không lỗi syntax.
- [x] Task 3: Thực thi nạp tuần tự toàn bộ 8,17 GB dữ liệu vào cụm HDFS `/steam/bronze/full/` → Verify: `docker exec hdfs-namenode hdfs dfs -ls /steam/bronze/full` hiển thị đủ ~218 file lô `batch_*.csv`.
- [x] Task 4: Kiểm chứng tính toàn vẹn dữ liệu HDFS và đối soát checksum → Verify: `artifacts/manifests/hdfs_full_ingestion_manifest.json` ghi nhận đúng 21.747.371 bản ghi logic và mã trạng thái SUCCESS.
- [x] Task 5: Thực thi Spark ETL tầng Medallion mức Full (Bronze → Silver → Gold) → Verify: `py -3.13 -m steam_reviews.presentation.cli.main etl --source data/landing/steam_reviews.csv --level full --run-id full-cluster-01 --sha256 0e6f8e9c791337cc19265deec0d6437f6ab84a840953d47f220acd8e0e882759` tạo đủ Parquet Silver/Gold và 0 lỗi reconciliation.
- [x] Task 6: Thực thi quy trình Machine Learning (Prepare Splits, Model Selection, Test Evaluation) → Verify: `ml-prepare`, `ml-train`, `ml-evaluate` hoàn tất, sinh ra `artifacts/metrics/full-cluster-01/test_metrics.json` với Macro-F1 >= 0.75.
- [x] Task 7: Kết xuất dữ liệu sang Dashboard Snapshot theo chuẩn schema v1 → Verify: `py -3.13 scripts/export_dashboard_snapshot.py --run-id full-cluster-01` tạo ra `artifacts/snapshots/dashboard_snapshot_full-cluster-01.json`.
- [x] Task 8: Kiểm định hiển thị và đối soát dữ liệu trên Streamlit Dashboard → Verify: Khởi chạy Streamlit với biến môi trường snapshot full, kiểm tra tự động 4 tab Overview, Data Quality, Deep Dive (EDA) và Model Ops không có lỗi runtime.

## Done When
- [x] Toàn bộ 21.747.371 bản ghi từ tệp 8,17 GB được phân lô và nạp nguyên vẹn vào cụm HDFS Bronze.
- [x] Tầng Silver Parquet khử trùng lặp thành công (134.927 bản ghi trùng của Hollow Knight được xử lý đúng theo F1).
- [x] 5 bảng Gold Parquet tổng hợp đầy đủ theo Game, Tháng, Ngôn ngữ, Giờ chơi và Chất lượng.
- [x] Mô hình Logistic Regression huấn luyện xong, chọn ra cấu hình tối ưu và đánh giá 30 mẫu lỗi.
- [x] Tệp `dashboard_snapshot_full-cluster-01.json` hợp lệ và Dashboard Streamlit sẵn sàng phục vụ trình diễn.

## Notes
- Dung lượng đĩa trống trên ổ C: ~48 GB, đủ cho HDFS replication 2 (~16.3 GB) và Silver Parquet (~2.5 GB).
- Xử lý WebHDFS từ Windows Host sang Docker bridge yêu cầu phân giải port mapping: `hdfs-datanode-1:9864 -> localhost:9864`, `hdfs-datanode-2:9864 -> localhost:9865`.
- Tập dữ liệu có chứa các đánh giá xuống dòng trong nháy kép (multiline RFC 4180), script phân lô phải dùng bộ phân tích cú pháp streaming an toàn.
