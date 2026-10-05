# Dữ liệu cục bộ

Nguồn duy nhất: [Steam Reviews Dataset 2021 — najzeko (Kaggle)](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021/data), giấy phép ghi trên Kaggle là `GPL 2`. Hợp đồng cột và quy tắc xử lý: [Plan.md mục 3.3](../Plan.md#33-dataset-steam-reviews-2021-và-hợp-đồng-dữ-liệu-v1).

- `landing/`: tệp đã tải hoàn tất (NiFi đọc từ đây); checksum SHA-256 và phiên bản ghi trong manifest.
- `sample/`: mẫu phát triển lấy theo hash `review_id`, có thể tái lập.
- `cache/`: dữ liệu tạm có thể tạo lại.

Các tệp dữ liệu ở đây được `.gitignore` loại khỏi Git; `.gitkeep` giữ cấu trúc thư mục. Fixture nhỏ dùng kiểm thử đặt trong `tests/fixtures/`. Không thay fixture bằng bản sao dataset lớn.

Dữ liệu bronze/silver/gold của pipeline nằm trên HDFS theo bố cục ở [Plan.md mục 3.5](../Plan.md#35-môi-trường-cụm-và-bố-cục-hdfs). Thư mục này chưa có dataset; hướng dẫn tải sẽ bổ sung vào `docs/runbooks/` trong Tuần 1–3.
