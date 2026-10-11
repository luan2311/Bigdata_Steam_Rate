# TV2-D01 — Bài toán dữ liệu

**Nguồn:** [Steam Reviews Dataset 2021](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021) (`najzeko/steam-reviews-2021`, phiên bản 1, giấy phép GPL 2).
**Truy cập Kaggle:** đã kiểm tra 11/10/2026. Dataset công khai, `kagglehub` tải được không cần token. Dataset gồm **một tệp `steam_reviews.csv` 8.171.787.229 byte**. Con số 3.193.406.910 byte trong Plan.md là dung lượng bản nén ZIP.

## 1. Năm câu hỏi phân tích

| # | Câu hỏi | Bảng gold | Cột nguồn cần |
|---|---|---|---|
| Q1 | Game nào có nhiều đánh giá, tỷ lệ khuyến nghị cao/thấp (luôn kèm số lượng, ngưỡng mặc định ≥ 100)? | `game_summary` | `app_id`, `app_name`, `recommended` |
| Q2 | Số đánh giá và tỷ lệ khuyến nghị thay đổi thế nào theo tháng (UTC) trong khoảng thời gian thực có? | `monthly_summary` | `timestamp_created`, `recommended`, `app_id`, `language` |
| Q3 | Phân bố ngôn ngữ và khác biệt tỷ lệ khuyến nghị giữa các ngôn ngữ? | `language_summary` | `language`, `recommended` |
| Q4 | Thời gian chơi tại lúc đánh giá liên hệ thế nào với khuyến nghị (liên hệ, không nhân quả)? | `playtime_summary` | `author.playtime_at_review`, `recommended` |
| Q5 | Mô hình TF-IDF + Logistic Regression trên review tiếng Anh dự đoán `recommended` tốt hơn baseline đa số bao nhiêu (macro-F1)? | `model_metrics` | `review`, `language`, `recommended`, `review_id` |

Ngoài ra, `quality_summary` trả lời câu hỏi nền: bao nhiêu dòng đọc được, lỗi, trùng, thiếu văn bản/thời gian.

## 2. Nhãn khuyến nghị và cảm xúc

- `recommended` là **hành vi khuyến nghị nhị phân** do người viết tự chọn (Recommended / Not Recommended). Đây không phải nhãn cảm xúc ba lớp tích cực/trung lập/tiêu cực.
- Không tạo lớp "trung lập". Không đổi nhãn thiếu/không hợp lệ thành `false`; các dòng như vậy vào quarantine.
- Mô hình Q5 học cách dự đoán nhãn khuyến nghị từ văn bản. Khi trình bày, gọi là "dự đoán khuyến nghị" và tránh gọi là "phân tích cảm xúc". Văn bản tiêu cực vẫn có thể đi với nhãn khuyến nghị (mỉa mai, meme), đây là nguồn lỗi cần phân tích ở D9.

## 3. Phạm vi EDA và ML

| Phần | Phạm vi | Lý do |
|---|---|---|
| EDA / gold | Mọi ngôn ngữ, mọi game trong mức dữ liệu đã chọn (smoke → Core → Full) | Q1–Q4 mô tả toàn tập quan sát |
| ML | Chỉ `language = english`, văn bản không rỗng, nhãn hợp lệ, đã dedup; tối đa ~200.000 dòng ở mức Core | Tokenizer/stopword theo tiếng Anh; vừa RAM máy local 11,7 GB |
| Feature ML | Chỉ văn bản review | Tránh rò rỉ: không dùng ID, votes, playtime, thời gian |
| Không làm | Nhãn cảm xúc 3 lớp, dịch đa ngôn ngữ, BERT, crawl Steam, suy ra doanh thu/số người mua | Ngoài phạm vi Plan.md §2.2 |

## 4. Môi trường TV2 đã khóa (local mode)

| Thành phần | Phiên bản | Ghi chú |
|---|---|---|
| Python | 3.11.9 (`.venv`) | PySpark 3.5 chưa hỗ trợ ổn định 3.13 |
| Java | Temurin 17.0.18 | Tương thích Spark 3.5 |
| PySpark | 3.5.3 | Đề xuất TV1 dùng cùng dòng Spark 3.5.x trên cụm |
| numpy / pandas / pyarrow | 1.26.4 / 2.2.3 / 17.0.0 | Bản tương thích PySpark 3.5 |
| kagglehub | 1.0.2 | Tải dataset |

Cài lại: `py -3.11 -m venv .venv` rồi `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

Kết quả kiểm kê thực tế (header, số dòng, nhãn, ngôn ngữ, thời gian) nằm trong [02_kiem_ke_du_lieu.md](02_kiem_ke_du_lieu.md).
