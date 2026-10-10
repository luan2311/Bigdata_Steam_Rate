# TỪ ĐIỂN DỮ LIỆU ĐỒ ÁN BIG DATA (DATA DICTIONARY V1)
## Đề tài: Phân tích dữ liệu đánh giá trò chơi trên Steam (Steam Reviews Analytics)

> **Mã nhiệm vụ:** `TV2-W02`  
> **Người chủ trì:** TV2 — Kỹ sư Xử lý dữ liệu lớn & ML  
> **Người phối hợp & review:** TV1, TV3  
> **Áp dụng:** Thống nhất định dạng giữa NiFi (Ingestion), HDFS (Storage), Spark (ETL & MLlib) và Streamlit (Dashboard).

---

## 1. Tầng dữ liệu Nguồn (Source / Bronze Layer)
- **Tên schema:** `steam_reviews_source`
- **Định dạng:** CSV thô (Landing) và CSV theo lô (HDFS Bronze: `/steam/bronze/<batch_id>/`)
- **Grain:** Mỗi dòng đại diện cho một bản ghi đánh giá thô thu thập từ Kaggle.

| Tên trường | Kiểu thô | Nullable | Đơn vị / Định dạng | Mô tả ý nghĩa |
|---|---|:---:|---|---|
| `""` (Cột 0) | `string` | Có | Số thứ tự dòng | Chỉ số tự sinh của Pandas, loại bỏ tại Silver |
| `app_id` | `string` | Không | Steam App ID | Mã định danh game của Steam Store |
| `app_name` | `string` | Không | Văn bản | Tên thương mại chính thức của game |
| `review_id` | `string` | Không | Khóa định danh | Mã số đánh giá duy nhất do Steam phát hành |
| `language` | `string` | Có | Mã ngôn ngữ | Ngôn ngữ người dùng viết đánh giá |
| `review` | `string` | Có | Chuỗi UTF-8 | Nội dung bài đánh giá |
| `timestamp_created` | `string` | Không | Unix timestamp (s) | Thời điểm viết bài đánh giá |
| `timestamp_updated` | `string` | Có | Unix timestamp (s) | Thời điểm cập nhật bài đánh giá lần cuối |
| `recommended` | `string` | Không | `'True'` / `'False'` | Nhãn người dùng có khuyến nghị game hay không |
| `votes_helpful` | `string` | Có | Số nguyên | Số lượt bình chọn hữu ích |
| `votes_funny` | `string` | Có | Số nguyên | Số lượt bình chọn hài hước |
| `weighted_vote_score` | `string` | Có | Số thực [0.0 - 1.0] | Điểm số độ tin cậy do thuật toán Steam tính |
| `comment_count` | `string` | Có | Số nguyên | Số lượng bình luận phản hồi |
| `steam_purchase` | `string` | Có | `'True'` / `'False'` | Mua trực tiếp trên Steam |
| `received_for_free` | `string` | Có | `'True'` / `'False'` | Nhận game miễn phí |
| `written_during_early_access` | `string` | Có | `'True'` / `'False'` | Viết lúc game đang trong giai đoạn Early Access |
| `author.steamid` | `string` | Có | 64-bit ID | Định danh tài khoản tác giả trên Steam |
| `author.num_games_owned` | `string` | Có | Số nguyên | Số game tác giả đang sở hữu |
| `author.num_reviews` | `string` | Có | Số nguyên | Tổng số review tác giả đã từng viết |
| `author.playtime_forever` | `string` | Có | Phút | Tổng thời gian chơi đến thời điểm cào dữ liệu |
| `author.playtime_last_two_weeks` | `string` | Có | Phút | Thời gian chơi trong 2 tuần gần nhất |
| `author.playtime_at_review` | `string` | Có | Phút | Thời gian chơi tại thời điểm viết đánh giá |
| `author.last_played` | `string` | Có | Unix timestamp (s) | Thời điểm chơi lần cuối cùng |

---

## 2. Tầng dữ liệu Làm sạch (Silver Layer)
- **Tên schema:** `steam_reviews_silver`
- **Định dạng:** Apache Parquet (Snappy compression) tại `/steam/silver/<run_id>/`
- **Grain:** Mỗi dòng đại diện cho một bài đánh giá duy nhất (Unique Review), đã deduplication theo `review_id` giữ bản cập nhật mới nhất theo `updated_at`.
- **Quy tắc làm sạch:** Loại bỏ cột index thừa; chuẩn hóa tên trường bỏ dấu chấm (`author_playtime_at_review`); ép kiểu dữ liệu chuẩn; chuyển đổi timestamp sang TimestampType (UTC).

| Tên trường | Kiểu dữ liệu | Nullable | Đơn vị / Định dạng | Mô tả ý nghĩa |
|---|---|:---:|---|---|
| `review_id` | `long` | **Không** | Khóa chính | Mã đánh giá duy nhất, không trùng lặp |
| `app_id` | `integer` | **Không** | ID số nguyên | Mã định danh game Steam |
| `app_name` | `string` | **Không** | Chuỗi UTF-8 | Tên game đã cắt bỏ khoảng trắng thừa |
| `language` | `string` | **Không** | Chữ thường (vd: 'english') | Ngôn ngữ chuẩn hóa, thiếu điền 'unknown' |
| `review_text` | `string` | Có | Chuỗi UTF-8 gốc | Nội dung gốc của bài đánh giá |
| `review_text_clean` | `string` | Có | Chuỗi UTF-8 chuẩn | Văn bản đã chuẩn hóa khoảng trắng phục vụ ML |
| `created_at` | `timestamp` | **Không** | UTC Timestamp | Thời điểm tạo bài viết |
| `updated_at` | `timestamp` | **Không** | UTC Timestamp | Thời điểm cập nhật bài viết |
| `year` | `integer` | **Không** | Năm (YYYY) | Năm tạo bài viết, dùng để partition dữ liệu |
| `month` | `integer` | **Không** | Tháng (1 - 12) | Tháng tạo bài viết |
| `recommended` | `boolean` | **Không** | True / False | Nhãn khuyến nghị chính thức |
| `label` | `double` | **Không** | `1.0` (True) / `0.0` (False) | Nhãn số học phục vụ Spark MLlib |
| `votes_helpful` | `integer` | Có | Số nguyên >= 0 | Số lượt vote hữu ích (null điền 0) |
| `votes_funny` | `integer` | Có | Số nguyên >= 0 | Số lượt vote hài hước (null điền 0) |
| `weighted_vote_score` | `double` | Có | [0.0 - 1.0] | Điểm số tín nhiệm |
| `comment_count` | `integer` | Có | Số nguyên >= 0 | Số bình luận |
| `steam_purchase` | `boolean` | Có | True / False | Mua trực tiếp trên Steam |
| `received_for_free` | `boolean` | Có | True / False | Nhận game miễn phí |
| `written_during_early_access` | `boolean` | Có | True / False | Đánh giá Early Access |
| `author_steamid` | `string` | Có | Chuỗi số | Định danh tác giả |
| `author_num_games_owned` | `integer` | Có | Số nguyên | Số game sở hữu |
| `author_num_reviews` | `integer` | Có | Số nguyên | Số bài review đã viết |
| `playtime_forever_minutes` | `double` | Có | Phút | Tổng giờ chơi |
| `playtime_at_review_minutes` | `double` | Có | Phút | Giờ chơi khi đăng bài |
| `playtime_bucket` | `string` | Có | Phân nhóm | Nhóm: `<2h`, `2-10h`, `10-50h`, `50-100h`, `>100h` |

---

## 3. Tầng dữ liệu Tổng hợp & Phục vụ ứng dụng (Gold Layer)
- **Định dạng:** Apache Parquet tại `/steam/gold/<run_id>/` và xuất snapshot JSON/Parquet cho Dashboard tại `artifacts/snapshots/`.
- **Công thức cốt lõi:**
  $$\text{recommendation\_rate} = \frac{\text{recommended\_count}}{\text{total\_reviews}}$$
  (Khi $\text{total\_reviews} = 0$, tỷ lệ là `None` hoặc `N/A`, không phát sinh lỗi chia cho 0).

### 3.1. Bảng `quality_summary`
- **Grain:** Mỗi dòng là một lần thực thi (`run_id`).
- **Các trường:** `run_id`, `dataset_version`, `total_records_read`, `invalid_structure_count`, `missing_id_count`, `duplicate_removed_count`, `valid_silver_records`, `processed_at`.

### 3.2. Bảng `game_summary`
- **Grain:** Mỗi dòng đại diện cho một tựa game (`app_id`).
- **Các trường:** `app_id`, `app_name`, `total_reviews`, `recommended_count`, `not_recommended_count`, `recommendation_rate`, `avg_playtime_hours`, `median_playtime_hours`.

### 3.3. Bảng `monthly_summary`
- **Grain:** Mỗi dòng đại diện cho một tổ hợp game theo tháng (`app_id` $\times$ `year_month`).
- **Các trường:** `app_id`, `app_name`, `year_month` (định dạng `YYYY-MM`), `total_reviews`, `recommended_count`, `recommendation_rate`.

### 3.4. Bảng `language_summary`
- **Grain:** Mỗi dòng đại diện cho một ngôn ngữ (`language`).
- **Các trường:** `language`, `total_reviews`, `language_percentage`, `recommended_count`, `recommendation_rate`.

### 3.5. Bảng `playtime_summary`
- **Grain:** Mỗi dòng đại diện cho một nhóm thời lượng chơi (`playtime_bucket`).
- **Các trường:** `playtime_bucket`, `bucket_order`, `total_reviews`, `recommended_count`, `recommendation_rate`.

### 3.6. Bảng `model_metrics`
- **Grain:** Mỗi dòng đại diện cho một mô hình (`model_name`: `'Majority Baseline'` hoặc `'Spark MLlib Logistic Regression'`).
- **Các trường:** `model_name`, `train_samples`, `test_samples`, `accuracy`, `precision`, `recall`, `macro_f1`, `pr_auc`, `confusion_matrix_tp`, `confusion_matrix_fp`, `confusion_matrix_tn`, `confusion_matrix_fn`, `evaluation_timestamp`.
