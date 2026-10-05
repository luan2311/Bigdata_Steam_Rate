# Luồng Apache NiFi — TV1

Đồ án bắt buộc dùng [Apache NiFi](https://nifi.apache.org/index.html) (dòng 2.x) để đưa [Steam Reviews Dataset 2021](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021/data) từ landing vào HDFS. Dữ liệu chính thức trên HDFS bronze phải đi qua NiFi, không nạp tay.

- `flows/`: flow JSON export đã kiểm tra import lại.
- `parameters/`: mẫu tham số không chứa bí mật (đường dẫn landing, WebHDFS host/port, kích thước lô).

Luồng cần triển khai: landing → `ListFile`/`FetchFile` → `CSVReader`/`SplitRecord` → kiểm tra → `InvokeHTTP` (WebHDFS CREATE 2 bước) → commit manifest. Có nhánh lỗi/quarantine, retry giới hạn 3 lần, back pressure và provenance. Thiết kế chi tiết: [Plan.md mục 3.4](../Plan.md#34-luồng-apache-nifi-tv1-chủ-trì).

`batch_id` phải tái lập; Spark chỉ đọc đợt có dấu hoàn tất. Bằng chứng replay/gián đoạn và đối soát đặt trong `docs/evidence/`; hướng dẫn import/vận hành đặt trong `docs/runbooks/`.

**Hiện chưa có flow thực thi.** Không đánh dấu công việc NiFi hoàn thành chỉ vì đã có thư mục.
