# Dữ liệu cục bộ

- `landing/`: nguồn đã tải, checksum và phiên bản được ghi trong manifest.
- `sample/`: mẫu phát triển lấy theo quy tắc có thể tái lập.
- `cache/`: dữ liệu tạm có thể tạo lại.

Các tệp dữ liệu ở đây được `.gitignore` loại khỏi Git; `.gitkeep` giữ cấu trúc thư mục. Fixture nhỏ dùng kiểm thử đặt trong `tests/fixtures/`. Không thay fixture bằng bản sao dataset lớn.

Dữ liệu bronze/silver/gold của pipeline nằm trên HDFS theo Plan.md. Thư mục này chưa có dataset; hướng dẫn tải và phạm vi mẫu sẽ được bổ sung ở D2.
