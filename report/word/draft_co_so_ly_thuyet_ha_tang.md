# BẢN THẢO BÁO CÁO: CƠ SỞ LÝ THUYẾT HẠ TẦNG DỮ LIỆU LỚN & LUỒNG TIẾP NHẬN
## MỤC 6.2: HỆ THỐNG LƯU TRỮ PHÂN TÁN HADOOP HDFS VÀ NỀN TẢNG TIẾP NHẬN DỮ LIỆU APACHE NIFI

> **Mã nhiệm vụ:** `TV1-W04`  
> **Người thực hiện:** TV1 — Kỹ sư Hạ tầng dữ liệu & Trực quan hóa  
> **Người review chéo:** TV2, TV3  
> **Đề tài:** Phân tích dữ liệu đánh giá trò chơi trên Steam (Steam Reviews Analytics)  
> **Mục tiêu áp dụng:** Trực tiếp đưa vào Mục 6 (Cơ sở lý thuyết) của Báo cáo đồ án môn học Nhập môn Big Data.

---

### 1. Tổng quan về Hạ tầng lưu trữ và tiếp nhận trong hệ sinh thái Big Data

Trong kiến trúc xử lý dữ liệu lớn hiện đại theo mô hình Medallion (Bronze – Silver – Gold) và Clean Architecture, tầng hạ tầng đóng vai trò nền móng quyết định khả năng mở rộng, tính sẵn sàng cao và tính toàn vẹn của dữ liệu:
- **Tầng lưu trữ phân tán (Storage Layer):** Yêu cầu một hệ thống có khả năng lưu trữ các tập tin dung lượng lớn (hàng Gigabyte đến hàng Terabyte), phân tán trên nhiều nút phần cứng thương mại (commodity hardware), hỗ trợ cơ chế nhân bản (replication) để chống chịu lỗi phần cứng mà không làm gián đoạn hệ thống. Nhóm lựa chọn **Hadoop Distributed File System (HDFS)**.
- **Tầng tiếp nhận dữ liệu (Ingestion Layer):** Không nạp dữ liệu thủ công hay dùng script gián đoạn, mà sử dụng hệ thống luồng dữ liệu tự động, kiểm soát áp lực ngược (back pressure), ghi vết dòng đời dữ liệu (data provenance), và cách ly các bản ghi lỗi cấu trúc (quarantine). Nhóm lựa chọn **Apache NiFi**.

---

### 2. Hệ thống tệp phân tán Hadoop HDFS (Hadoop Distributed File System)

#### 2.1. Kiến trúc tổng thể Master/Worker
HDFS được xây dựng theo kiến trúc Master/Worker phân cấp rõ ràng:

1. **NameNode (Master Node):**
   - Đóng vai trò là "bộ não" của cụm HDFS, quản lý toàn bộ không gian tên hệ thống tệp (file system namespace), cây thư mục và thông tin định vị khối dữ liệu (metadata mapping: tệp nào bao gồm những block nào và các block đó đang nằm trên DataNode nào).
   - NameNode lưu trữ toàn bộ metadata trong bộ nhớ RAM để đảm bảo thời gian phản hồi mili-giây cho các truy vấn mở/đóng/đổi tên tệp.
   - Để đảm bảo tính bền vững (durability), NameNode duy trì hai cấu trúc trên đĩa:
     + `fsimage`: Snapshot toàn bộ trạng thái namespace tại một thời điểm nhất định.
     + `edits` (EditLog): Nhật ký ghi lại mọi thay đổi (tạo mới, xóa, đổi quyền) phát sinh sau snapshot `fsimage`.
   - **Secondary NameNode / Checkpoint Node:** Thực hiện định kỳ kéo `fsimage` và `edits` từ NameNode, hợp nhất (checkpointing) thành một `fsimage` mới và gửi ngược lại NameNode, giúp ngăn chặn kích thước `edits` phình to làm chậm quá trình khởi động lại của NameNode.

2. **DataNodes (Worker Nodes):**
   - Các nút công nhân trực tiếp lưu trữ các khối dữ liệu (Data Blocks) vật lý dưới dạng các tệp nhị phân trên hệ điều hành cục bộ (ext4, XFS).
   - Chịu trách nhiệm thực hiện các yêu cầu đọc/ghi trực tiếp từ phía client sau khi client đã hỏi vị trí khối từ NameNode.
   - Định kỳ gửi các tín hiệu nhịp tim (**Heartbeats**) và báo cáo khối (**Block Reports**) về cho NameNode để báo cáo tình trạng sống còn và danh mục các khối dữ liệu mà nút đang lưu giữ.

```
+-------------------------------------------------------------------------+
|                           HDFS Master / Worker                          |
|                                                                         |
|                          +-------------------+                          |
|                          |     NameNode      |                          |
|                          | (Metadata in RAM) |                          |
|                          +-------------------+                          |
|                            /       |       \                            |
|             Heartbeat &   /        |        \   Heartbeat &             |
|             Block Report /         |         \  Block Report            |
|                         v          |          v                         |
|                 +-----------+      |      +-----------+                 |
|                 | DataNode 1|      |      | DataNode 2|                 |
|                 | (Block 1) | <----+----> | (Block 1) |                 |
|                 | (Block 2) | Pipeline Ghi| (Block 3) |                 |
|                 +-----------+             +-----------+                 |
+-------------------------------------------------------------------------+
```

#### 2.2. Khái niệm Khối dữ liệu (Data Block) & Kích thước khối 128 MB
- Khác với hệ thống tệp truyền thống (OS file system có kích thước block thường là 4 KB), HDFS chia nhỏ các tệp lớn thành các khối độc lập có kích thước mặc định là **128 MB** (hoặc 256 MB trong các hệ thống quy mô lớn).
- **Lý do HDFS sử dụng kích thước block lớn:**
  1. *Giảm thiểu chi phí tìm kiếm đĩa (Disk Seek Time):* Chi phí định vị đầu đọc đĩa cơ/bộ điều khiển được khấu hao trên một khối truyền tải liên tục lớn, giúp tốc độ truyền tải đạt mức tối đa của băng thông I/O.
  2. *Tiết kiệm bộ nhớ cho NameNode:* Mỗi tệp, thư mục và khối dữ liệu chỉ tiêu tốn khoảng 150 byte metadata trong RAM của NameNode. Nếu chia thành các khối 4 KB, một tệp 10 GB sẽ sinh ra 2.5 triệu khối, gây tràn bộ nhớ NameNode. Với khối 128 MB, 10 GB chỉ tạo ra khoảng 80 khối dữ liệu.

#### 2.3. Cơ chế Nhân bản khối (Block Replication) và Khả năng chịu lỗi (Fault-Tolerance)
- Để bảo vệ dữ liệu trước nguy cơ hỏng hóc phần cứng, mỗi block trong HDFS được nhân bản thành $N$ bản sao (mặc định trong sản xuất là `dfs.replication = 3`, trong mô phỏng cụm đồ án là `dfs.replication = 2`).
- **Chính sách phân bổ bản sao (Rack Awareness):**
  + Bản sao 1: Đặt trên một DataNode trong cùng rack với client thực hiện ghi.
  + Bản sao 2: Đặt trên một DataNode ở một rack khác (để phòng ngừa rủi ro mất toàn bộ nguồn điện hoặc hỏng switch mạng của một rack).
  + Bản sao 3: Đặt trên một DataNode khác cùng rack với bản sao 2.
- **Tự phục hồi (Self-Healing):** Khi một DataNode không gửi Heartbeat quá thời gian cấu hình (mặc định 10 phút), NameNode đánh dấu nút đó đã chết (Dead Node), kiểm tra danh sách các block bị thiếu bản sao (Under-replicated Blocks), và tự động chỉ đạo các DataNode còn lại nhân bản bổ sung các block đó sang các DataNode còn sống để đưa replication factor về đúng giá trị quy định.

#### 2.4. Quy trình Đọc và Ghi dữ liệu trong HDFS

1. **Quy trình Ghi dữ liệu (Write Pipeline):**
   - **Bước 1:** Client gửi yêu cầu tạo tệp tới NameNode (`CREATE`).
   - **Bước 2:** NameNode kiểm tra quyền, xác nhận tệp chưa tồn tại và cấp phát một danh sách các DataNode sẽ lưu trữ khối dữ liệu đầu tiên.
   - **Bước 3:** Client mở luồng ghi tới DataNode thứ nhất ($DN_1$). $DN_1$ nhận từng gói dữ liệu (packet 64 KB), ghi vào bộ đệm và lập tức chuyển tiếp (stream) sang DataNode thứ hai ($DN_2$), hình thành một đường ống truyền tải (**Pipeline Stream**).
   - **Bước 4:** Sau khi các DataNode trong pipeline đều xác nhận nhận đủ gói tin qua chuỗi ACK, khối dữ liệu được hoàn tất và client chuyển sang khối tiếp theo.

2. **Quy trình Đọc dữ liệu (Read Pipeline):**
   - **Bước 1:** Client gửi yêu cầu đọc tệp tới NameNode (`OPEN`).
   - **Bước 2:** NameNode trả về vị trí các DataNode chứa từng block của tệp, sắp xếp theo thứ tự khoảng cách mạng gần nhất với client.
   - **Bước 3:** Client kết nối trực tiếp tới DataNode gần nhất để đọc dữ liệu mà không đi qua NameNode, tránh tình trạng NameNode trở thành nút thắt cổ chai về băng thông dữ liệu.

#### 2.5. Giao thức WebHDFS REST API
- WebHDFS cung cấp một giao thức RESTful hoàn chỉnh tuân thủ chuẩn POSIX để tương tác với HDFS qua giao thức HTTP/HTTPS.
- **Quy trình tạo tệp hai bước (Two-step Creation Process):**
  + **Bước 1:** Client gửi `PUT http://<namenode>:9870/webhdfs/v1/<path>?op=CREATE`. NameNode xử lý và trả về phản hồi mã HTTP `307 Temporary Redirect`, trong Header `Location` chứa địa chỉ trực tiếp của DataNode được chỉ định (`http://<datanode>:9864/webhdfs/v1/<path>?op=CREATE...`).
  + **Bước 2:** Client gửi tiếp yêu cầu HTTP `PUT` kèm theo luồng dữ liệu (payload) trực tiếp tới DataNode tại URL nhận được ở bước 1. Sau khi ghi thành công, DataNode trả về HTTP `201 Created`.
- Đây là cơ chế nền tảng giúp Apache NiFi có thể nạp dữ liệu phân tán vào HDFS qua processor `InvokeHTTP` một cách an toàn và chuẩn mực.

---

### 3. Nền tảng điều phối luồng dữ liệu Apache NiFi

#### 3.1. Kiến trúc Flow-Based Programming (FBP)
Apache NiFi là một hệ sinh thái mã nguồn mở mạnh mẽ được thiết kế dựa trên triết lý lập trình hướng luồng (Flow-Based Programming):
- Dữ liệu được xem như những "gói thông tin" (FlowFile) chảy liên tục qua các "nút xử lý" (Processors) thông qua các "hàng đợi kết nối" (Queues/Connections).
- Người phát triển có thể cấu hình, giám sát, dừng/bật các luồng dữ liệu theo thời gian thực mà không cần khởi động lại toàn bộ hệ thống.

```
+--------------------------------------------------------------------------+
|                       Apache NiFi Core Architecture                      |
|                                                                          |
|       +---------------------------------------------------------+        |
|       |                     FlowFile                            |        |
|       |  [Attributes: metadata, filename, batch_id, mime_type]  |        |
|       |  [Content: con trỏ trỏ tới dữ liệu vật lý]              |        |
|       +---------------------------------------------------------+        |
|                                    |                                     |
|    +----------------------+        |          +----------------------+   |
|    | FlowFile Repository  | <------+--------> |  Content Repository  |   |
|    | (Lưu metadata trong  |                   | (Lưu nội dung nhị    |   |
|    |  WAL đĩa/bộ nhớ)     |                   |  phân trên đĩa)      |   |
|    +----------------------+                   +----------------------+   |
|                                    |                                     |
|                                    v                                     |
|                       +--------------------------+                       |
|                       |  Provenance Repository   |                       |
|                       | (Lịch sử biến đổi dòng)  |                       |
|                       +--------------------------+                       |
+--------------------------------------------------------------------------+
```

#### 3.2. Cấu trúc cốt lõi của FlowFile
Một FlowFile trong NiFi cấu thành từ hai phần tách biệt:
1. **Attributes (Thuộc tính):** Là tập hợp các cặp `Key-Value` lưu giữ metadata của dữ liệu (ví dụ: `filename`, `fileSize`, `uuid`, `batch_id`, `record.count`). Attributes được lưu trữ trong **FlowFile Repository** bằng nhật ký ghi trước (Write-Ahead Log), cho phép tìm kiếm và định tuyến luồng với độ trễ cực thấp.
2. **Content (Nội dung dữ liệu):** Là bản thân tệp dữ liệu thực tế (dữ liệu CSV thô, JSON, nhị phân). Nội dung này được lưu trữ bất biến (immutable) trong **Content Repository**. Khi một Processor thay đổi nội dung, NiFi ghi nội dung mới sang một block mới và cập nhật con trỏ thay vì ghi đè, bảo vệ dữ liệu khỏi tình trạng hỏng hóc giữa chừng.

#### 3.3. Các kho lưu trữ nội bộ (NiFi Repositories)
- **FlowFile Repository:** Giữ vết trạng thái và thuộc tính hiện tại của từng FlowFile đang di chuyển trong hệ thống.
- **Content Repository:** Lưu trữ dữ liệu thực tế. Nhờ cơ chế copy-on-write, NiFi có thể hỗ trợ nhiều luồng xử lý cùng trỏ tới một vùng nội dung mà không gây lãng phí bộ nhớ.
- **Provenance Repository:** Lưu giữ toàn bộ lịch sử biến đổi (Data Lineage) của mọi FlowFile từ khi sinh ra (CREATE), bị phân tách (FORK), biến đổi (MODIFY) cho đến khi nạp thành công vào hệ thống đích (SEND). Cho phép tua lại (replay) bất kỳ FlowFile nào tại bất kỳ thời điểm nào trong quá khứ.

#### 3.4. Xử lý dữ liệu định hướng bản ghi (Record-Oriented Data Processing)
Trong các kiến trúc cũ, NiFi xử lý dữ liệu theo từng tệp (File-oriented), khiến việc tiếp nhận một tập dữ liệu lớn hàng chục triệu bản ghi trở nên nặng nề và dễ gây tràn bộ nhớ heap.
Ở phiên bản hiện đại (NiFi 2.x), NiFi chuyển dịch hoàn toàn sang kiến trúc **Record-Oriented**:
- **Controller Services tách biệt:**
  + `CSVReader`: Phân tích cú pháp dữ liệu CSV dựa trên schema được định nghĩa trước hoặc suy luận từ header. Đặc biệt, `CSVReader` sử dụng thư viện Apache Commons CSV, có khả năng xử lý hoàn hảo các trường dữ liệu đa dòng (multiline review), các ký tự escape và dấu nháy kép phức tạp (`"` bên trong `"..."`).
  + `CSVRecordSetWriter`: Ghi lại dữ liệu theo định dạng chuẩn hóa, đảm bảo mã hóa ký tự UTF-8 thống nhất.
- **SplitRecord Processor:** Thay vì dùng `SplitText` (vốn cắt thô bạo theo ký tự xuống dòng `\n` và sẽ làm gãy nát các bài đánh giá game có nhiều đoạn văn bản), `SplitRecord` phân tích đúng cấu trúc từng bản ghi logic và chia nhỏ tập tin 8.17 GB thành các lô nhỏ đồng đều (~50.000 records/lô) mà không làm biến dạng dữ liệu.

#### 3.5. Kiểm soát áp lực ngược (Back Pressure) & Hàng đợi cách ly (Quarantine)
- **Back Pressure:** Khi một processor downstream (ví dụ: bộ đẩy dữ liệu WebHDFS) xử lý chậm hơn processor upstream (bộ đọc đĩa), hàng đợi giữa chúng sẽ đầy dần. NiFi cho phép đặt ngưỡng Back Pressure (ví dụ: tối đa 10.000 đối tượng hoặc 1 GB). Khi chạm ngưỡng, upstream processor sẽ tự động bị ngắt kích hoạt cho tới khi hàng đợi giải phóng, ngăn chặn hiện tượng tràn bộ nhớ (Out-Of-Memory).
- **Quarantine Queue (Hàng đợi cách ly):** Các bản ghi bị lỗi cú pháp, thiếu các trường khóa bắt buộc (`review_id`, `app_id`), hoặc có cấu trúc hỏng sẽ không bị vứt bỏ âm thầm mà được định tuyến tự động vào nhánh Quarantine. Nhánh này ghi nhận mã lỗi và chuyển vào vùng lưu trữ cách ly để kỹ sư dữ liệu đối soát.

---

### 4. So sánh: NiFi Ingestion vs. Nạp dữ liệu thủ công qua `hdfs dfs -put`

| Tiêu chí so sánh | Nạp thủ công bằng lệnh `hdfs dfs -put` | Tiếp nhận tự động qua Apache NiFi (Dự án lựa chọn) |
|---|---|---|
| **Mức độ tự động hóa** | Hoàn toàn thủ công, phụ thuộc vào thao tác gõ lệnh của con người. | Hoàn toàn tự động, vận hành liên tục theo cơ chế hướng sự kiện hoặc lập lịch. |
| **Xử lý bản ghi đa dòng & lỗi** | Không kiểm tra nội dung; nếu CSV chứa dữ liệu lỗi cấu trúc, toàn bộ tệp vẫn bị nạp nguyên xi vào HDFS. | Sử dụng `CSVReader` và `SplitRecord`, kiểm soát chặt chẽ bản ghi lỗi, tự động định tuyến vào Quarantine queue. |
| **Kiểm soát áp lực & Chạy lại** | Nếu lệnh ngắt giữa chừng, không có cơ chế resume mà phải xóa đi nạp lại từ đầu. | Tích hợp sẵn cơ chế Retry có giới hạn, Back Pressure chống nghẽn, và sinh `batch_id` kèm manifest kiểm soát. |
| **Khả năng quan sát (Observability)**| Không có giao diện; chỉ biết thành công hoặc thất bại qua mã thoát dòng lệnh. | Giao diện đồ họa trực quan theo thời gian thực; giám sát throughput (records/s), dung lượng hàng đợi và biểu đồ luồng. |
| **Truy vết dòng dữ liệu (Lineage)** | Không có lịch sử biến đổi của từng bản ghi dữ liệu. | Tính năng Data Provenance theo dõi chi tiết từng thao tác sinh ra, phân tách và nạp vào HDFS. |

**Kết luận:** Việc sử dụng Apache NiFi làm cổng tiếp nhận dữ liệu duy nhất là quyết định kiến trúc đúng đắn, đáp ứng triệt để các tiêu chuẩn của một hệ thống Big Data chuyên nghiệp theo đúng yêu cầu đề tài môn học.
