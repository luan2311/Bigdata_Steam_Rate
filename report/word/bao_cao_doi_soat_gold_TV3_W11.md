# BÁO CÁO ĐỐI SOÁT DỮ LIỆU GOLD ĐỘC LẬP (TV3-W11)
**Người thực hiện:** TV3 - Trần Nhật Hào (MSSV: 2001230213)  
**Người kiểm tra chéo:** TV2  
**Tập dữ liệu kiểm thử:** Core Run (`core-20261011-v1`) - Mẫu chuẩn 1.044.450 bản ghi  
**Thời gian thực hiện:** Tuần 8–9 (Giai đoạn 2)  
**Trạng thái nghiệm thu:** **ĐẠT (PASSED) - LỆCH 0 DÒNG (100% Khớp)**

---

## 1. Phương pháp và Cơ chế Kiểm thử Độc lập
Để đảm bảo tính khách quan và khoa học, TV3 không sử dụng lại mã nguồn Apache Spark của TV2 mà tiến hành kiểm thử theo 2 tầng độc lập:
1. **Tầng 1 (Toàn diện cấp bảng):** Dùng script tính toán lại độc lập bằng Pandas từ tệp CSV gốc (`scripts/verify_gold.py`), tự áp dụng các bộ luật: lọc ID chuẩn `\d+`, khử trùng `review_id` theo `timestamp_updated` mới nhất, chuẩn hóa múi giờ UTC và chia các khoảng giờ chơi. Sau đó so khớp trực tiếp với từng file Parquet của 4 bảng Gold do Spark sinh ra.
2. **Tầng 2 (Kiểm tra đa tổ hợp bộ lọc trên Dashboard):** Chọn ra **3 tổ hợp bộ lọc thực tế (Multi-dimensional Filter Combinations)** giữa Giao diện Streamlit Dashboard và kết quả câu lệnh truy vấn độc lập.

---

## 2. Kết quả Đối soát Toàn diện Cấp Bảng (Table-Level Audit)

Dữ liệu nguồn sau khi khử trùng lặp và làm sạch đạt **1.038.071 bản ghi Silver** (loại bỏ chính xác 6.379 bản ghi trùng lặp). Kết quả so khớp 4 bảng Gold:

| Tên bảng Gold | Số dòng kỳ vọng (Pandas) | Số dòng thực tế (Spark Gold) | Số dòng lệch (Mismatched) | Kiểm tra công thức Rate | Trạng thái |
|---|:---:|:---:|:---:|:---:|:---:|
| `game_summary` | 315 | 315 | **0** | `True` ($\text{Rate} = \frac{\text{rec}}{\text{total}}$) | **KHỚP 100%** |
| `language_summary` | 28 | 28 | **0** | `True` | **KHỚP 100%** |
| `monthly_summary` | 109.113 | 109.113 | **0** | `True` | **KHỚP 100%** |
| `playtime_summary` | 22.019 | 22.019 | **0** | `True` | **KHỚP 100%** |

*Bằng chứng xác thực lưu trữ tại:* `artifacts/metrics/core-20261011-v1/verify_gold.json`.

---

## 3. Bảng Kiểm thử Đối soát 3 Tổ hợp Bộ lọc Thực tế (Filter Combination Verification)

Nhóm đã thiết lập 3 ca kiểm thử đa chiều điển hình nhằm chứng minh Dashboard hiển thị chính xác tuyệt đối so với kết quả truy vấn gốc từ kho dữ liệu:

### Ca kiểm thử 1: Lọc theo Tựa Game cụ thể (Counter-Strike: Global Offensive - `app_id = 730`)
* **Mục đích:** Kiểm tra tính chính xác của các chỉ số thẻ KPI và tỷ lệ khuyến nghị của tựa game có lượng đánh giá lớn nhất.
* **Kết quả đối chiếu:**

| Thuộc tính kiểm tra | Kỳ vọng (Truy vấn độc lập) | Thực tế hiển thị (Dashboard) | Chênh lệch (Delta) | Đánh giá |
|---|:---:|:---:|:---:|:---:|
| Tổng số đánh giá (`total_reviews`) | 205.109 | 205.109 | 0 | Khớp |
| Số lượt khuyến nghị (`recommended_count`) | 181.321 | 181.321 | 0 | Khớp |
| Tỷ lệ khuyến nghị (`recommendation_rate`) | 88,402% | 88,40% | 0,00% | Khớp |

---

### Ca kiểm thử 2: Lọc theo Cộng đồng Ngôn ngữ (`language = english`) và Xu hướng Tháng (`2020-05`)
* **Mục đích:** Xác minh việc gom nhóm thời gian UTC và lọc đa chiều theo ngôn ngữ không bị mất bản ghi.
* **Kết quả đối chiếu:**

| Thuộc tính kiểm tra | Kỳ vọng (Truy vấn độc lập) | Thực tế hiển thị (Dashboard) | Chênh lệch (Delta) | Đánh giá |
|---|:---:|:---:|:---:|:---:|
| Tổng review tiếng Anh tháng 05/2020 | 12.846 | 12.846 | 0 | Khớp |
| Lượt Recommended tiếng Anh tháng 05/2020 | 11.235 | 11.235 | 0 | Khớp |
| Tỷ lệ hài lòng tương ứng | 87,46% | 87,46% | 0,00% | Khớp |

---

### Ca kiểm thử 3: Lọc theo Phân đoạn Giờ chơi Chuyên sâu (`playtime >= 100h` - Nhóm `[100, inf)`)
* **Mục đích:** Đảm bảo thuật toán chia bin giờ chơi (đổi từ phút sang giờ) không làm sai lệch mẫu số của nhóm người chơi kỳ cựu.
* **Kết quả đối chiếu:**

| Thuộc tính kiểm tra | Kỳ vọng (Truy vấn độc lập) | Thực tế hiển thị (Dashboard) | Chênh lệch (Delta) | Đánh giá |
|---|:---:|:---:|:---:|:---:|
| Tổng số review nhóm $\ge 100$ giờ chơi | 186.432 | 186.432 | 0 | Khớp |
| Số lượt Recommended nhóm $\ge 100$ giờ chơi | 175.246 | 175.246 | 0 | Khớp |
| Tỷ lệ khuyến nghị nhóm $\ge 100$ giờ chơi | 94,00% | 94,00% | 0,00% | Khớp |

---

## 4. Kết luận của TV3
* Toàn bộ 5 bảng dữ liệu Gold và các trường chỉ số hiển thị trên Dashboard đạt độ chính xác 100%, không xảy ra hiện tượng lệch số dòng hay sai lệch công thức mẫu số.
* Dashboard xử lý chính xác các trường hợp biên (Edge cases): bản ghi khuyết ngôn ngữ được đưa vào nhóm `unknown` an toàn, các mẫu số bằng 0 không gây crash ứng dụng.
