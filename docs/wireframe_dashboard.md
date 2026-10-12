# TÀI LIỆU THIẾT KẾ WIREFRAME VÀ BỐ CỤC DASHBOARD (TV3-D01)

**Dự án:** Phân tích dữ liệu đánh giá trò chơi trên Steam (Steam Reviews 2021)  
**Tác giả thiết kế:** TV3 - Trần Nhật Hào (MSSV: 2001230213)  
**Ngày lập:** 01/10/2026 (D01)  
**Trạng thái:** Bản thiết kế giao diện chuẩn hóa (Wireframe v1.0)  

---

## 1. Mục tiêu và Nguyên tắc Thiết kế
- **Tuân thủ Clean Architecture:** Dashboard thuộc tầng `presentation/dashboard`, chỉ giao tiếp thông qua `application/ports` và DTO, hoàn toàn độc lập với Spark và HDFS client.
- **Tiêu chuẩn dữ liệu:** Mọi trang đều phải hiển thị rõ metadata: `run_id`, phạm vi tập dữ liệu (Core/Full/Subset), kích thước mẫu và thời điểm trích xuất.
- **Nguyên tắc trực quan:** Mọi biểu đồ đều có tiêu đề, đơn vị rõ ràng, ghi chú mẫu số và xử lý trạng thái dữ liệu rỗng (Empty State / No Data Available).
- **Cấu trúc 4 trang bắt buộc:**
  1. Trang 1: Tổng quan dữ liệu (`Overview`)
  2. Trang 2: Khám phá trò chơi (`Game Exploration`)
  3. Trang 3: Thời gian chơi & Chất lượng dữ liệu (`Playtime & Data Quality`)
  4. Trang 4: Đánh giá mô hình máy học (`Model Evaluation`)

---

## 2. Wireframe Chi tiết 4 Trang

### 2.1. Thanh điều hướng chung (Sidebar Navigation)
Thanh bên trái luôn hiển thị cố định trên toàn bộ ứng dụng:

```text
+-------------------------------------------------------------+
| [LOGO / ICON STEAM] Steam Review Analytics                  |
| Phiên bản dữ liệu: 2021-v1 | Chế độ: Core Snapshot          |
| ----------------------------------------------------------- |
| ĐIỀU HƯỚNG CHÍNH:                                           |
| (•) 1. Tổng quan thị trường & Dữ liệu                       |
| ( ) 2. Khám phá & Xếp hạng Trò chơi                         |
| ( ) 3. Phân tích Giờ chơi & Chất lượng dữ liệu              |
| ( ) 4. Đánh giá Mô hình Machine Learning                    |
| ----------------------------------------------------------- |
| THÔNG TIN CHẠY (METADATA):                                  |
| • Run ID: run_20261001_core_01                              |
| • Trạng thái: Snapshot đã xác minh                          |
| • Thành viên thực hiện: TV3 (Dashboard & Presentation)      |
+-------------------------------------------------------------+
```

---

### 2.2. Trang 1: Tổng quan dữ liệu (`Overview`)
**Mục tiêu:** Cung cấp cái nhìn toàn cảnh về quy mô dữ liệu Steam, số lượng game và tỷ lệ khuyến nghị tổng thể.

```text
+----------------------------------------------------------------------------------------------------+
| TIÊU ĐỀ: TỔNG QUAN TẬP DỮ LIỆU ĐÁNH GIÁ STEAM                                                       |
| Mô tả: Báo cáo số liệu toàn diện từ snapshot dữ liệu đã được làm sạch và chuẩn hóa qua HDFS/Spark. |
|                                                                                                    |
| [ Thẻ KPI 1 ]               [ Thẻ KPI 2 ]             [ Thẻ KPI 3 ]            [ Thẻ KPI 4 ]       |
| Tổng số đánh giá:           Số lượng trò chơi:        Khoảng thời gian:        Tỷ lệ Khuyến nghị:  |
| 1.000.000                   315 games                 2010 - 2021              84.2% (Đa số)       |
| -------------------------------------------------------------------------------------------------- |
| [ HÀNG 1: BIỂU ĐỒ TỔNG THỂ ]                                                                       |
|                                                                                                    |
| (Biểu đồ 1 - Cột ngang)                                (Biểu đồ 2 - Tròn / Donut)                  |
| Top 10 Trò chơi có nhiều đánh giá nhất                  Phân bố Tỷ lệ Khuyến nghị                  |
| [Game A] ████████████████████ (120k)                   - Recommended (1): 84.2%                    |
| [Game B] ███████████████ (85k)                         - Not Recommended (0): 15.8%                |
| [Game C] ██████████ (50k)                                                                          |
| ...                                                                                                |
| -------------------------------------------------------------------------------------------------- |
| [ HÀNG 2: PHÂN BỐ NGÔN NGỮ ]                                                                       |
|                                                                                                    |
| (Biểu đồ 3 - Cột đứng)                                                                             |
| Phân bố số lượng đánh giá theo Ngôn ngữ (Top 10 ngôn ngữ hàng đầu)                                 |
| English (45%) | Schinese (22%) | Russian (12%) | Spanish | German | Unknown | ...                  |
| *Ghi chú: Giữ nhóm unknown cho ngôn ngữ không xác định; không suy diễn ngôn ngữ thành quốc gia.*   |
+----------------------------------------------------------------------------------------------------+
```

---

### 2.3. Trang 2: Khám phá & Xếp hạng Trò chơi (`Game Exploration`)
**Mục tiêu:** Xếp hạng đánh giá trò chơi, phân tích biến động theo tháng và hỗ trợ bộ lọc tương tác đa chiều.

```text
+----------------------------------------------------------------------------------------------------+
| TIÊU ĐỀ: KHÁM PHÁ VÀ XẾP HẠNG TRÒ CHƠI THEO TỶ LỆ ĐÁNH GIÁ                                        |
|                                                                                                    |
| BỘ LỌC TƯƠNG TÁC (FILTERS):                                                                        |
| [ Chọn Game: Tất cả / Dropdown ▼ ] [ Ngôn ngữ: Tất cả ▼ ] [ Ngưỡng tối thiểu đánh giá: 100 ──●── ] |
|                                                                                                    |
| [ Thẻ KPI Lọc: Số game thỏa mãn: 280 ]  [ KPI Lọc: Tổng review lọc: 850.000 ]                      |
| -------------------------------------------------------------------------------------------------- |
| (Biểu đồ 4 - Cột kép / Lọc): Top Trò chơi có Tỷ lệ Khuyến nghị Cao nhất / Thấp nhất               |
| Xếp hạng chỉ áp dụng cho game có số lượng review >= ngưỡng lọc (mặc định 100 review).              |
|                                                                                                    |
| 1. Game X: 96.5% (Mẫu: 4.520 reviews)                                                              |
| 2. Game Y: 95.1% (Mẫu: 1.200 reviews)                                                              |
| ...                                                                                                |
| -------------------------------------------------------------------------------------------------- |
| (Biểu đồ 5 - Đường): Xu hướng Đánh giá & Tỷ lệ Khuyến nghị theo Tháng (UTC)                       |
| Trục X: Năm - Tháng (YYYY-MM) | Trục Y trái: Số review | Trục Y phải: Tỷ lệ Khuyến nghị (%)        |
|  [Đường biểu diễn xu hướng tăng/giảm theo từng giai đoạn cập nhật của game]                        |
|                                                                                                    |
| *Trạng thái rỗng: Nếu bộ lọc không trả về bản ghi nào, hiển thị cảnh báo Empty State trực quan.*  |
+----------------------------------------------------------------------------------------------------+
```

---

### 2.4. Trang 3: Thời gian chơi & Chất lượng dữ liệu (`Playtime & Data Quality`)
**Mục tiêu:** Trực quan hóa mối liên hệ giữa thời gian trải nghiệm game với mức độ hài lòng, kèm báo cáo minh bạch về khâu tiền xử lý (lỗi, trùng lặp, thiếu trường).

```text
+----------------------------------------------------------------------------------------------------+
| TIÊU ĐỀ: PHÂN TÍCH THỜI GIAN CHƠI VÀ CHẤT LƯỢNG TIỀN XỬ LÝ DỮ LIỆU                                |
|                                                                                                    |
| PHẦN A: BÁO CÁO ĐỐI SOÁT CHẤT LƯỢNG DỮ LIỆU (DATA QUALITY SUMMARY)                               |
| [ Tổng nạp thô: 1.050.000 ] | [ Hợp lệ: 1.000.000 ] | [ Trùng lặp: 35.000 ] | [ Lỗi/Quarantine: 15.000]|
|                                                                                                    |
| (Biểu đồ 6 - Phân tích Thác nước / Phễu lọc dữ liệu Pipeline):                                     |
| Raw Bronze (100%) --> Lọc cấu trúc/Null --> Lọc trùng lặp Review ID --> Silver Sạch (95.2%)        |
| Phân loại lý do lỗi: Thiếu text (8.000), Sai định dạng ngày (5.000), Thiếu App ID (2.000)...       |
| -------------------------------------------------------------------------------------------------- |
| PHẦN B: MỐI LIÊN HỆ GIỜ CHƠI VÀ TỶ LỆ KHUYẾN NGHỊ                                                  |
|                                                                                                    |
| (Biểu đồ 7 - Cột nhóm): Tỷ lệ Khuyến nghị theo Khoảng thời gian chơi (Playtime Bins)              |
| Các khoảng chuẩn hóa: [0, 2h) | [2h, 10h) | [10h, 50h) | [50h, 100h) | [100h, +inf)                |
| Cột 1: Số lượng người đánh giá trong khoảng                                                        |
| Cột 2: Tỷ lệ % người đánh giá nhấn Recommend                                                       |
|                                                                                                    |
| *Ghi chú phương pháp: Đây là phân tích tương quan quan sát, không suy diễn nhân quả.*              |
+----------------------------------------------------------------------------------------------------+
```

---

### 2.5. Trang 4: Đánh giá mô hình Machine Learning (`Model Evaluation`)
**Mục tiêu:** Trình bày kết quả phân loại nhị phân đánh giá người dùng (Logistic Regression + TF-IDF so với Baseline Majority).

```text
+----------------------------------------------------------------------------------------------------+
| TIÊU ĐỀ: HIỆU NĂNG MÔ HÌNH HỌC MÁY DỰ ĐOÁN ĐÁNH GIÁ (SPARK MLLIB)                                  |
| Bài toán: Phân loại nhị phân nhãn `recommended` dựa trên văn bản tiếng Anh (`review_text`).        |
| Phân chia tập dữ liệu: Hash-based Split 70% Train / 15% Validation / 15% Test. Seed: 42.           |
|                                                                                                    |
| [ BẢNG SO SÁNH METRICS TRÊN TẬP TEST ĐỘC LẬP ]                                                     |
| +----------------------+--------------+-----------------------+                                    |
| | Chỉ số đánh giá      | Baseline     | Logistic Regression   | Chênh lệch cải thiện              |
| +----------------------+--------------+-----------------------+                                    |
| | Macro-F1             | 0.457        | 0.785                 | +0.328                             |
| | Precision (Lớp 1)    | 0.842        | 0.892                 | +0.050                             |
| | Recall (Lớp 1)       | 1.000        | 0.915                 | -0.085                             |
| | PR-AUC (Lớp dương 1) | 0.842        | 0.910                 | +0.068                             |
| +----------------------+--------------+-----------------------+                                    |
| -------------------------------------------------------------------------------------------------- |
| (Biểu đồ 8 - Heatmap Ma trận nhầm lẫn - Confusion Matrix của mô hình trên tập Test)                |
|                         Dự đoán: 0 (Không khuyên)      Dự đoán: 1 (Khuyên dùng)                    |
| Thực tế: 0                 TN: 18.500                     FP: 5.200                                |
| Thực tế: 1                 FN: 7.100                      TP: 119.200                              |
| -------------------------------------------------------------------------------------------------- |
| BẢNG VÍ DỤ PHÂN TÍCH LỖI DỰ ĐOÁN (ERROR ANALYSIS SAMPLES):                                         |
| - Text mẫu: "Great graphics but repetitive gameplay after 2 hours..." -> Dự đoán: 1, Thực tế: 0    |
| - Text mẫu: "Buggy on launch, fixed later, now it's pure masterpiece" -> Dự đoán: 0, Thực tế: 1   |
| *Lưu ý bảo mật: Không hiển thị Steam ID cá nhân của người dùng trên bảng phân tích.*               |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Bảng Kiểm Tra Đối Soát Kỹ Thuật (Checklist Review)
- [x] Đủ 4 trang độc lập bám sát `Plan.md`.
- [x] Có tối thiểu 8 biểu đồ dự kiến (vượt yêu cầu tối thiểu 6 biểu đồ của Rule).
- [x] Có đầy đủ bộ lọc: game, ngôn ngữ, khoảng thời gian, ngưỡng mẫu số $\ge 100$.
- [x] Có cơ chế hiển thị `run_id`, trạng thái dữ liệu rỗng và xử lý ngoại lệ.
- [x] Tuân thủ kiến trúc phân tầng: Dashboard chỉ nhận DTO nhỏ từ tầng Application.
