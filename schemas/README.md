# Hợp đồng dữ liệu — TV2 chủ trì, TV1 cùng review

- `source/`: schema và ánh xạ từ header thực của dataset Kaggle.
- `silver/`: schema sau chuẩn hóa/dedup, kiểu dữ liệu và thuộc tính nullable rõ ràng.
- `gold/`: schema quality/game/monthly/language/playtime summaries và model metrics; giữ đủ chiều cần cho bộ lọc.

Mỗi hợp đồng ghi version, khóa, đơn vị, grain (mỗi dòng đại diện cho gì), null, run_id và ví dụ nhỏ. TV1 dùng để cấu hình NiFi và hiển thị Dashboard, TV2 dùng cho Spark ETL và ML. Mọi thay đổi phải thống nhất giữa hai thành viên trước khi cập nhật adapter.

Chưa tạo schema giả từ tên cột dự kiến; đối chiếu dữ liệu thực trước khi viết schema chạy được. Data dictionary và quyết định lấy mẫu lưu tại `docs/data/`.
