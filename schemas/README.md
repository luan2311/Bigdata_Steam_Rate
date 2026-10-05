# Hợp đồng dữ liệu — TV2, TV1 và TV3 cùng review

- `source/`: schema và ánh xạ từ header thực của dataset Kaggle, chốt D2.
- `silver/`: schema sau chuẩn hóa/dedup, kiểu và nullable rõ ràng.
- `gold/`: schema quality/game/monthly/language/playtime summaries và model metrics; giữ đủ chiều cần cho bộ lọc.

Mỗi hợp đồng ghi version, khóa, đơn vị, grain (mỗi dòng đại diện cho gì), null, run_id và ví dụ nhỏ. TV1 dùng để cấu hình NiFi, TV2 dùng cho Spark, TV3 dùng cho dashboard. Thay đổi phải báo cả nhóm trước khi cập nhật adapter.

Chưa tạo schema giả từ tên cột dự kiến; đối chiếu dữ liệu thực trước khi viết schema chạy được. Data dictionary và quyết định lấy mẫu lưu tại `docs/data/`.
