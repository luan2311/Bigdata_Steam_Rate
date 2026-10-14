# RUNBOOK: KHẢO SÁT HẠ TẦNG & TÀI NGUYÊN CỤM BIG DATA (TV1-W02)
## Đề tài: Phân tích dữ liệu đánh giá trò chơi trên Steam (Steam Reviews Analytics)

> **Mã nhiệm vụ:** `TV1-W02`  
> **Người thực hiện:** TV1 (Kỹ sư Hạ tầng dữ liệu & Trực quan hóa)  
> **Người review chéo:** TV2 (Kỹ sư Xử lý dữ liệu lớn & ML)  
> **Căn cứ kế hoạch:** [Plan.md](../../Plan.md) (Mục 3.4, 3.5), [Checklist.md](../../Checklist.md) (Mục 1, TV1-W02)

---

## 1. Khảo sát cấu hình phần cứng máy thực thi thực tế

Dựa trên kết quả đo đạc trực tiếp trên máy chủ phát triển cục bộ:

| Thành phần phần cứng | Thông số ghi nhận thực tế | Đánh giá khả năng đáp ứng cụm phân tán |
|---|---|---|
| **CPU** | AMD Ryzen 7 4800H with Radeon Graphics (8 Cores, 16 Logical Processors) | **Rất tốt.** Dư dả CPU cores để phân bổ cho 7 container (NiFi, HDFS, Spark Master + 2 Workers). |
| **RAM vật lý (Host)** | **24 GB** (24,558,704 KB ~ 23.42 GiB) | **Đạt yêu cầu khuyến nghị.** Đủ tài nguyên để cấp phát 14–16 GB cho Docker Desktop/WSL2, giữ 8 GB cho Windows Host + Browser/IDE. |
| **RAM khả dụng hiện tại** | ~4.6 GB (trước khi tối ưu hóa nền tảng) | Cần cấu hình giới hạn RAM qua `.wslconfig` để Docker không chiếm dụng tràn sang Host OS. |
| **Ổ cứng trống (C:)** | **77.6 GB SSD NVMe** | **Đạt yêu cầu.** Đủ cho landing dataset (~8.2 GB), Bronze HDFS (replication 2: ~16 GB hoặc Core Tier ~1.5 GB), Silver/Gold Parquet (~3 GB), và Docker image cache (~10 GB). |
| **Ổ cứng trống (D:)** | **52.6 GB SSD/HDD** | Sẵn sàng làm phân vùng sao lưu hoặc chứa artifact xuất khẩu dự phòng. |
| **Môi trường ảo hóa** | Docker version 29.7.2, Docker Compose v5.5.1 trên nền Windows Subsystem for Linux (WSL2) | Hỗ trợ đầy đủ cgroups v2, mạng cầu nối Docker bridge và kiểm soát giới hạn tài nguyên container. |

---

## 2. Khảo sát các thành phần công nghệ cụm phân tán

Cụm được triển khai qua Docker Compose gồm 7 dịch vụ chính:

```
+-----------------------------------------------------------------------------------+
|                            DOCKER VIRTUAL NETWORK (bridge)                        |
|                                                                                   |
|  +--------------------+         WebHDFS REST          +-----------------------+   |
|  |    Apache NiFi     | ----------------------------> |  Hadoop HDFS NameNode |   |
|  |  (HTTPS :8443)     |                               |      (Web :9870)      |   |
|  +--------------------+                               +-----------------------+   |
|            |                                             /                 \      |
|     Tải lô từ Landing                       +--------------------+  +--------------------+
|                                             |  HDFS DataNode 1   |  |  HDFS DataNode 2   |
|                                             |    (Web :9864)     |  |    (Web :9865)     |
|                                             +--------------------+  +--------------------+
|                                                          ^                     ^          
|                                                          |   Đọc/Ghi Parquet   |          
|  +--------------------+                     +--------------------+  +--------------------+
|  |  Spark Master      | <================== |   Spark Worker 1   |  |   Spark Worker 2   |
|  |   (Web :8080)      |     Phân phối task  |    (Web :8081)     |  |    (Web :8082)     |
|  +--------------------+                     +--------------------+  +--------------------+
+-----------------------------------------------------------------------------------+
                                            |
                             +-------------------------------+
                             | Streamlit Dashboard UI (:8501)|
                             +-------------------------------+
```

### 2.1. Apache NiFi 2.x
- **Vai trò:** Tiếp nhận duy nhất (Ingestion Gateway), phân tích CSV đa dòng, chia lô (batching ~50.000 dòng/lô), xử lý hàng đợi cách ly (Quarantine), đẩy dữ liệu vào HDFS qua WebHDFS REST API.
- **Yêu cầu hệ điều hành/Runtime:** NiFi 2.x yêu cầu tối thiểu Java 21 LTS.
- **Tài nguyên cần thiết:** JVM Heap `-Xms1g -Xmx2g`. Giới hạn container: 3.5 GB RAM, 2 CPU Cores.

### 2.2. Hadoop HDFS 3.3.x (Cluster mô phỏng phân tán)
- **1 NameNode:** Quản lý metadata khối, kiểm soát namespace. Heap: `-Xms512m -Xmx1g`. Giới hạn container: 1.5 GB RAM, 1 CPU Core.
- **2 DataNodes:** Lưu trữ phân tán khối dữ liệu thực tế với `dfs.replication = 2`. Mỗi DataNode: Heap `-Xms512m -Xmx1g`, giới hạn container: 1.5 GB RAM, 1 CPU Core.
- **Ưu điểm của mô hình 2 DataNodes:** Đảm bảo chứng minh được cơ chế chịu lỗi và phân tán khối (Block Replication) theo chuẩn đề cương môn học mà không vượt ngưỡng RAM 24 GB.

### 2.3. Apache Spark 3.5.x (Cluster Standalone)
- **1 Spark Master:** Điều phối tài nguyên và phân bổ application. Giới hạn container: 1.5 GB RAM, 1 CPU Core.
- **2 Spark Workers:**
  - Mỗi Worker được cấp phát 2 Cores và 2 GB RAM cho Executor (`SPARK_WORKER_MEMORY=2G`, `SPARK_WORKER_CORES=2`).
  - Giới hạn container: 2.5 GB RAM mỗi Worker.
  - Cho phép benchmark đối sánh thực tế: Chạy ETL/ML với 1 Worker so với 2 Workers để chứng minh tính mở rộng ngang.

### 2.4. Streamlit Dashboard
- **Vai trò:** Ứng dụng giao diện người dùng 4 trang, hiển thị biểu đồ Plotly tương tác, đọc dữ liệu Gold/Snapshot.
- **Tài nguyên:** Giới hạn container 1.0 GB RAM, 1 CPU Core (hoặc chạy trực tiếp trên môi trường ảo Python của Host).

---

## 3. Bảng phân bổ tài nguyên chi tiết (Resource Allocation Matrix)

### 3.1. Phân bổ RAM & CPU cho từng container

| Dịch vụ Container | Image dự kiến | CPU Limit | RAM Heap (JVM) | RAM Limit (Docker) | Cổng Host (Mapped Port) | Mục đích sử dụng |
|---|---|---|---|---|---|---|
| `nifi` | `apache/nifi:2.x` | 2.0 Cores | 2.0 GB | 3.5 GB | `8443:8443` | NiFi Web UI (HTTPS), REST Ingestion |
| `hdfs-namenode` | `apache/hadoop:3.3.6` | 1.0 Core | 1.0 GB | 1.5 GB | `9870:9870`, `9000:9000` | NameNode Web UI & RPC, WebHDFS |
| `hdfs-datanode-1` | `apache/hadoop:3.3.6` | 1.0 Core | 1.0 GB | 1.5 GB | `9864:9864`, `9866:9866` | DataNode 1 Web UI & Data Transfer |
| `hdfs-datanode-2` | `apache/hadoop:3.3.6` | 1.0 Core | 1.0 GB | 1.5 GB | `9865:9864`, `9867:9866` | DataNode 2 Web UI & Data Transfer |
| `spark-master` | `bitnami/spark:3.5.0` | 1.0 Core | 1.0 GB | 1.5 GB | `8080:8080`, `7077:7077` | Spark Master Web UI & Cluster RPC |
| `spark-worker-1` | `bitnami/spark:3.5.0` | 2.0 Cores | 2.0 GB | 2.5 GB | `8081:8081` | Spark Worker 1 Web UI & Executor |
| `spark-worker-2` | `bitnami/spark:3.5.0` | 2.0 Cores | 2.0 GB | 2.5 GB | `8082:8081` | Spark Worker 2 Web UI & Executor |
| **Tổng cộng cụm** | — | **10.0 Cores** | — | **14.0 GB RAM** | — | **Hoàn toàn khả thi trên máy 8C/16T - 24GB RAM** |

> **Cân đối tài nguyên:**
> - Cụm Docker tiêu thụ tối đa: **14.0 GB RAM** và **10 Cores (Logical)**.
> - Máy Host còn lại: **~9.4 GB RAM** và **6 Cores (Logical)** dành riêng cho Windows 11, VS Code/IDE, Trình duyệt Web và Terminal. Không gây hiện tượng nghẽn swap disk hoặc treo máy.

---

## 4. Dự trù và phân bổ dung lượng lưu trữ đĩa (Disk Storage Sizing)

Tập dữ liệu gốc đã được tải về tại `data/landing/steam_reviews.csv` có dung lượng chính xác là:  
**8,171,787,229 bytes (~8.17 GiB)**, chứa khoảng 21,6 triệu bản ghi đánh giá.

Dự trù lưu trữ cho 3 kịch bản vận hành:

| Tầng lưu trữ | Mức Smoke Tier (~10k dòng) | Mức Core Tier (~1M dòng - Mục tiêu chính) | Mức Full Tier (~21.6M dòng) |
|---|---|---|---|
| **Landing Zone** (CSV thô cục bộ) | ~5 MB | ~380 MB | ~8.17 GB |
| **HDFS Bronze** (Lô nạp qua NiFi, replication=2) | ~10 MB | ~760 MB | ~16.34 GB |
| **HDFS Silver** (Parquet snappy, làm sạch + dedup) | ~2 MB | ~150 MB | ~2.50 GB |
| **HDFS Gold** (Bảng tổng hợp KPI + Summary) | < 1 MB | ~20 MB | ~100 MB |
| **NiFi State & FlowFile/Content Repos** | ~200 MB | ~2 GB | ~8 GB |
| **Spark Temp & Shuffle Scratch** | ~100 MB | ~1 GB | ~6 GB |
| **Tổng dung lượng đĩa cần thiết** | **< 1 GB** | **~4.3 GB** | **~41.1 GB** |
| **Tỷ lệ chiếm dụng trên SSD C: (77.6 GB trống)** | **< 1%** | **~5.5%** | **~53.0%** |

**Kết luận:** Dung lượng SSD hiện tại của máy (77.6 GB trống) hoàn toàn dư dả cho quy mô **Core Tier (1 triệu dòng - mục tiêu đồ án)** và đủ khả năng chạy thử nghiệm **Full Tier** khi có kịch bản dọn dẹp các tệp tạm thích hợp.

---

## 5. Ma trận cổng mạng (Port Mapping Matrix) tránh xung đột

Để tránh xung đột giữa các dịch vụ trong cùng máy host:

| Dịch vụ | Cổng mặc định bên trong container | Cổng ánh xạ ra Host (Host Port) | Giao thức | Ghi chú quan trọng |
|---|---|---|---|---|
| **NiFi Web UI** | `8443` | `8443` | HTTPS | Không dùng cổng 8080 để tránh đụng Spark Master! |
| **Spark Master UI** | `8080` | `8080` | HTTP | Giao diện quản lý Spark Master |
| **Spark Master RPC**| `7077` | `7077` | TCP | Cổng giao tiếp nội bộ cho Spark Worker & Driver |
| **Spark Worker 1 UI**| `8081` | `8081` | HTTP | Giao diện Worker 1 |
| **Spark Worker 2 UI**| `8081` | `8082` | HTTP | Ánh xạ sang 8082 trên Host |
| **HDFS NameNode UI**| `9870` | `9870` | HTTP | Giao diện NameNode & WebHDFS endpoint |
| **HDFS NameNode RPC**| `9000` | `9000` | TCP | Cổng RPC client kết nối NameNode |
| **HDFS DataNode 1 UI**| `9864` | `9864` | HTTP | Giao diện DataNode 1 |
| **HDFS DataNode 1 Data**| `9866` | `9866` | TCP | Cổng truyền tải khối dữ liệu |
| **HDFS DataNode 2 UI**| `9864` | `9865` | HTTP | Ánh xạ sang 9865 trên Host |
| **HDFS DataNode 2 Data**| `9866` | `9867` | TCP | Ánh xạ sang 9867 trên Host |
| **Streamlit Dashboard**| `8501` | `8501` | HTTP | Giao diện báo cáo và trực quan hóa dữ liệu |

---

## 6. Chiến lược vận hành linh hoạt (Dual Operational Modes)

Để đảm bảo hệ thống luôn vận hành mượt mà, TV1 thiết kế hai chế độ vận hành:

### Chế độ 1: Cụm đầy đủ đồng thời (Concurrent Full-Cluster Mode)
- **Áp dụng khi:** Máy đang có nhiều RAM trống, chạy quy mô Smoke Tier hoặc Core Tier.
- **Quy trình:** Khởi động đồng thời cả NiFi, HDFS, Spark và Dashboard.
- **Tiêu thụ RAM:** ~14.0 GB.

### Chế độ 2: Vận hành phân kỳ theo giai đoạn (Staged Execution Mode - Khuyến nghị cho kiểm thử tải lớn)
- **Áp dụng khi:** Chạy thử nghiệm Full Tier hoặc khi máy Host cần mở nhiều ứng dụng đồ họa nặng.
- **Giai đoạn Ingestion:**
  1. Chỉ bật `hdfs-namenode`, `hdfs-datanode-1`, `hdfs-datanode-2` và `nifi`. (Tiêu thụ ~8.0 GB RAM).
  2. NiFi chạy hoàn tất việc đẩy dữ liệu vào `/steam/bronze/` và sinh manifest.
  3. Dừng container `nifi` (`docker compose stop nifi`) để giải phóng 3.5 GB RAM.
- **Giai đoạn Processing & ML:**
  4. Khởi động `spark-master`, `spark-worker-1`, `spark-worker-2`. (Tiêu thụ ~9.5 GB RAM gồm cả HDFS).
  5. Thực thi Spark ETL (Bronze -> Silver -> Gold) và huấn luyện mô hình MLlib.
  6. Xuất Gold summary Parquet và Dashboard snapshot vào `artifacts/snapshots/`.
- **Giai đoạn Trực quan hóa:**
  7. Dừng các worker Spark (`docker compose stop spark-worker-1 spark-worker-2`).
  8. Khởi chạy Dashboard Streamlit đọc snapshot Gold siêu nhẹ (chỉ ~150 MB RAM).

---

## 7. Hướng dẫn thiết lập tệp cấu hình WSL2 (`.wslconfig`)

Nhằm tối ưu hóa tài nguyên phần cứng của máy (24 GB RAM, 8 Cores), người vận hành nên tạo hoặc cập nhật tệp `C:\Users\<USER>\.wslconfig` với nội dung sau:

```ini
[wsl2]
# Giới hạn bộ nhớ tối đa cho máy ảo WSL2 (khoảng 65% tổng RAM 24 GB)
memory=16GB

# Phân bổ số luồng CPU cho WSL2
processors=10

# Bật bộ nhớ ảo swap phòng trường hợp đột biến bộ nhớ
swap=8GB
swapFile=C:\\temp\\wsl-swap.vhdx

# Thu hồi bộ nhớ RAM không sử dụng về cho Windows
pageReporting=true
```

Sau khi chỉnh sửa, thực hiện lệnh trong PowerShell để khởi động lại WSL2:
```powershell
wsl --shutdown
```

---

## 8. Kết luận và Kế hoạch tiếp theo (TV1-W02 -> TV1-W05)

1. **Kết luận khảo sát:** Cấu hình phần cứng của máy chủ phát triển (AMD Ryzen 7 4800H 8C/16T, 24 GB RAM, SSD 77.6 GB free) **hoàn toàn đáp ứng xuất sắc** việc triển khai cụm phân tán Big Data theo đúng mục tiêu của đồ án (Core Tier 1.000.000 bản ghi trên cụm Docker Compose 7 container).
2. **Kế hoạch tiếp theo:**
   - Bước sang Tuần 4–5 (nhiệm vụ `TV1-W05`), TV1 sẽ dựa trên bảng phân bổ tài nguyên này để tạo tệp `infra/docker/docker-compose.yml` chính thức và các tệp cấu hình `hdfs-site.xml`, `core-site.xml`, `spark-env.sh`.
