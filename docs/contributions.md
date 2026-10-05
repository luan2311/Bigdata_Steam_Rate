# Nhật ký và đóng góp của nhóm (2 sinh viên)

## 1. Thành viên

| Mã | Họ tên | MSSV | Vai trò chính | Người review chéo |
|---|---|---|---|---|
| **TV1** | Chưa điền | Chưa điền | Hạ tầng (Docker, HDFS), Ingestion (NiFi), Dashboard (Streamlit/Plotly), Điều phối & Hồ sơ | TV2 |
| **TV2** | Chưa điền | Chưa điền | Hợp đồng dữ liệu (Schema), Spark ETL/Processing, Spark MLlib, Metrics & Đánh giá | TV1 |

## 2. Nhật ký làm việc hàng ngày

Thêm dòng cho mỗi công việc thực hiện. Sử dụng mã nhiệm vụ trong `Checklist.md`. Đường dẫn bằng chứng là tệp trong repo, commit hoặc log/ảnh thực nghiệm.

| Ngày thực tế | Tuần học phần | Thành viên | Mã nhiệm vụ | Công việc đã làm | Giờ thực tế | Sản phẩm / Bằng chứng | Người review & Kết quả | Vướng mắc / Bước tiếp theo |
|---|---|---|---|---|---|---|---|---|
| — | Tuần 1 | — | — | Chưa ghi nhận | — | — | — | — |

## 3. Tổng hợp tiến độ theo tuần (Khung 10 tuần)

| Giai đoạn | Tuần | TV1 (Hạ tầng, NiFi, Dashboard) | TV2 (Spark ETL, MLlib, Phân tích) | Mốc nghiệm thu | Điều chỉnh (nếu có) |
|---|---|---|---|---|---|
| **Giai đoạn chuẩn bị** | Tuần 1–3 | Phân công, lập kế hoạch chi tiết, chuẩn bị hạ tầng container | Chọn bài toán, khảo sát dataset Steam Reviews, phác thảo pipeline | Đề tài được duyệt; Kế hoạch chi tiết hoàn chỉnh | — |
| **Lý thuyết & Thiết kế** | Tuần 4–5 | Dựng môi trường cụm (HDFS/NiFi/Spark), xây luồng NiFi mẫu vào WebHDFS | Khảo sát dữ liệu, chốt Schema v1, viết tài liệu thuật toán (TF-IDF + LR) | Tài liệu tóm tắt thuật toán & ví dụ; Smoke cluster chạy thông suốt | — |
| **Giai đoạn 1 (30% điểm đồ án)** | Tuần 6–7 | Hoàn thiện luồng NiFi có chia lô/retry/manifest, nạp bronze/silver; demo hạ tầng | Xây dựng baseline model, đánh giá sơ bộ, xác định điểm cần cải thiện | **Báo cáo tiến độ GĐ1 nộp Tuần 6-7** (CLO1, CLO2) | — |
| **Hoàn thiện & Giai đoạn 2 (70% điểm đồ án)** | Tuần 8–9 | Hoàn thiện Dashboard 4 trang, kết nối Gold data, viết báo cáo Word & Slide | Tối ưu mô hình MLlib, phân tích lỗi, đối soát số liệu Gold | **Báo cáo hoàn chỉnh GĐ2 nộp Tuần 9** (Source code, Word, PPT) | — |
| **Báo cáo cuối kỳ** | Tuần 10 | Chuẩn bị kịch bản Demo, diễn tập thuyết trình, kiểm tra môi trường offline | Chuẩn bị trả lời phản biện về dữ liệu, Spark MLlib và thuật toán | **Thuyết trình & Demo trước lớp** (CLO3, CLO4, CLO5) | — |

## 4. Bảng phân công và tỷ lệ đóng góp cuối kỳ

| Thành viên | Sản phẩm chính đã nghiệm thu | Giờ thực tế | Tỷ lệ đóng góp thống nhất | Xác nhận của nhóm |
|---|---|---|---|---|
| **TV1** | Hạ tầng cụm, Luồng NiFi, Dashboard Streamlit, Hồ sơ Word & PPT | — | 50% | [ ] Đồng thuận |
| **TV2** | Schema, Pipeline Spark ETL, Mô hình Spark MLlib, Metrics & Đánh giá | — | 50% | [ ] Đồng thuận |

*Ghi chú: Tỷ lệ đóng góp đánh giá dựa trên toàn bộ quá trình (kỹ thuật, tài liệu, review, thuyết trình), tổng hai thành viên phải đạt 100%.*
