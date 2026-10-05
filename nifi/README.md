# Luồng NiFi — TV1

- `flows/`: lưu flow JSON export đã kiểm tra import lại.
- `parameters/`: lưu mẫu tham số không chứa bí mật.

Luồng cần triển khai: landing → ListFile/FetchFile → CSVReader/SplitRecord → kiểm tra → WebHDFS → commit manifest. Có nhánh lỗi, retry giới hạn, back pressure và provenance theo Plan.md.

Tên lô phải tái lập; Spark chỉ đọc đợt hoàn tất. Bằng chứng replay/gián đoạn và đối soát đặt trong `docs/evidence/`; hướng dẫn import/vận hành đặt trong `docs/runbooks/`.

**Hiện chưa có flow thực thi.** Không đánh dấu công việc NiFi hoàn thành chỉ vì đã có thư mục.
