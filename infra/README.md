# Cấu hình triển khai — TV1

- `docker/`: Dockerfile, Compose và cấu hình volume/network khi triển khai ở Tuần 4–5 (NiFi 2.x, HDFS, Spark — xem [Plan.md mục 3.5](../Plan.md#35-môi-trường-cụm-và-bố-cục-hdfs)).
- `hadoop/`: cấu hình NameNode/DataNode và HDFS.
- `spark/`: cấu hình master/worker, submit và event log.

Chốt phiên bản/image digest và tài nguyên theo Plan.md; lưu hướng dẫn dựng cụm trong `docs/runbooks/`. NiFi, Spark và Hadoop có thể cần runtime Java riêng.

**Hiện chưa có cấu hình cụm chạy được.** Không lưu mật khẩu, token hoặc dữ liệu volume vào Git. Mẫu biến môi trường bổ sung sau phải dùng giá trị minh họa và ghi rõ trường cần điền.
