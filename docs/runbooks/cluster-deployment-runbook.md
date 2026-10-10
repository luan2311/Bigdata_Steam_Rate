# RUNBOOK: HƯỚNG DẪN KHỞI CHẠY & KIỂM THỬ CỤM PHÂN TÁN BIG DATA (TV1-W05)
## Đề tài: Phân tích dữ liệu đánh giá trò chơi trên Steam (Steam Reviews Analytics)

> **Mã nhiệm vụ:** `TV1-W05`, `TV1-W06`  
> **Người thực hiện:** TV1 — Kỹ sư Hạ tầng dữ liệu & Trực quan hóa  
> **Môi trường:** Docker Compose trên nền WSL2 / Linux  
> **Tài liệu cấu hình:** `infra/docker/docker-compose.yml`

---

## 1. Cấu trúc Cụm 7 Container Phân tán

| Dịch vụ | Container Name | Hostname | Image | Cổng Web UI | Cổng Dịch vụ | Chức năng |
|---|---|---|---|---|---|---|
| **HDFS NameNode** | `hdfs-namenode` | `hdfs-namenode` | `apache/hadoop:3.3.6` | `http://localhost:9870` | `9000` (RPC) | Quản lý metadata khối HDFS & WebHDFS REST API |
| **HDFS DataNode 1** | `hdfs-datanode-1` | `hdfs-datanode-1` | `apache/hadoop:3.3.6` | `http://localhost:9864` | `9866` (Data) | Nút lưu trữ khối 1 (`dfs.replication=2`) |
| **HDFS DataNode 2** | `hdfs-datanode-2` | `hdfs-datanode-2` | `apache/hadoop:3.3.6` | `http://localhost:9865` | `9867` (Data) | Nút lưu trữ khối 2 (`dfs.replication=2`) |
| **Spark Master** | `spark-master` | `spark-master` | `apache/spark:3.5.0` | `http://localhost:8080` | `7077` (Cluster RPC) | Điều phối tài nguyên tính toán Spark |
| **Spark Worker 1** | `spark-worker-1` | `spark-worker-1` | `apache/spark:3.5.0` | `http://localhost:8081` | — | Nút tính toán Worker 1 (2 Cores, 2 GB RAM) |
| **Spark Worker 2** | `spark-worker-2` | `spark-worker-2` | `apache/spark:3.5.0` | `http://localhost:8082` | — | Nút tính toán Worker 2 (2 Cores, 2 GB RAM) |
| **Apache NiFi** | `nifi` | `nifi` | `apache/nifi:2.0.0` | `https://localhost:8443` | `8443` (HTTPS) | Cổng tiếp nhận dữ liệu (Ingestion Gateway) |

> [!IMPORTANT]
> **Quy tắc cổng:** NiFi sử dụng cổng HTTPS `8443` để **tuyệt đối không xung đột** với cổng HTTP `8080` của Spark Master!

---

## 2. Các lệnh Quản trị Cụm (CLI Operations)

### 2.1. Khởi động Cụm
Từ thư mục gốc dự án:
```powershell
docker compose -f infra/docker/docker-compose.yml up -d
```

### 2.2. Kiểm tra trạng thái các Container
```powershell
docker compose -f infra/docker/docker-compose.yml ps
```

### 2.3. Kiểm tra bằng chứng phân tán HDFS (HDFS Distributed Evidence)
Kiểm tra báo cáo các DataNodes đang hoạt động:
```powershell
docker exec hdfs-namenode hdfs dfsadmin -report
```
*Kỳ vọng:* `Live datanodes (2)` và tổng dung lượng lưu trữ phân tán hiển thị đủ cả 2 nút.

Kiểm tra tính toàn vẹn và mức độ nhân bản khối:
```powershell
docker exec hdfs-namenode hdfs fsck / -files -blocks -locations
```

### 2.4. Kiểm tra tài nguyên Spark Cluster
Truy cập Web UI tại: `http://localhost:8080`
*Kỳ vọng:* Hiển thị `Alive Workers: 2`, `Cores in use: 0 of 4`, `Memory in use: 0 B of 4.0 GiB`.

### 2.5. Đăng nhập Apache NiFi Web UI
1. Truy cập: `https://localhost:8443/nifi` (chấp nhận chứng chỉ SSL tự ký - Self-signed Certificate).
2. Tài khoản quản trị:
   - **Username:** `admin`
   - **Password:** `BigDataSteam2026!`
3. Tải lên và kích hoạt mẫu luồng tại: `nifi/flows/steam_reviews_ingestion_sample_flow.json`.

---

## 3. Quy trình thực hiện Ingestion mẫu (~10.000 bản ghi) qua WebHDFS (TV1-W06)

### 3.1. Dữ liệu mẫu chuẩn hóa
Tệp dữ liệu mẫu đã được trích xuất an toàn tại:
`data/sample/steam_reviews_sample_10k.csv`
- Đảm bảo trích xuất theo bản ghi logic (record), bảo toàn toàn bộ bài đánh giá đa dòng (multiline), dấu ngoặc kép escape và ký tự Unicode đa ngôn ngữ.

### 3.2. Chạy kịch bản nạp tự động qua WebHDFS
Chạy script kiểm thử:
```powershell
python scripts/ingest_sample_to_hdfs.py
```
Quy trình thực thi:
1. Chia tệp mẫu thành 2 lô (mỗi lô 5.000 bản ghi).
2. Gửi yêu cầu PUT tới WebHDFS NameNode (`http://localhost:9870/webhdfs/v1/steam/bronze/sample/batch_01.csv?op=CREATE`).
3. Tự động nhận chuyển hướng HTTP 307 tới DataNode đích và hoàn tất ghi nhận mã HTTP 201 Created.
4. Xác minh tính toàn vẹn dữ liệu trong HDFS.

---

## 4. Dừng và giải phóng tài nguyên
Khi hoàn thành phiên làm việc:
```powershell
docker compose -f infra/docker/docker-compose.yml down
```
Hoặc tạm dừng để bảo lưu dữ liệu:
```powershell
docker compose -f infra/docker/docker-compose.yml stop
```
