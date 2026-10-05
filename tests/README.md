# Kiểm thử sẽ triển khai cùng chức năng

- `unit/`: kiểm tra domain và use case bằng fake port, không cần dịch vụ ngoài.
- `integration/`: kiểm tra adapter Spark/storage/ingestion với dữ liệu nhỏ.
- `e2e/`: kiểm tra toàn luồng và các ca nghiệm thu trong Plan.md.
- `fixtures/`: tệp nhỏ do nhóm tạo, có kết quả mong đợi rõ.

Bộ khung chưa chứa test. Chọn công cụ và bổ sung hướng dẫn chạy khi khóa dependency D2. Ưu tiên kiểm tra lỗi thực tế: CSV nhiều dòng, nhãn null, dedup, mẫu số 0, split rò rỉ, replay và số liệu dashboard.
