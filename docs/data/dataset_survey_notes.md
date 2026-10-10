# GHI CHÚ KHẢO SÁT BỘ DỮ LIỆU STEAM REVIEWS 2021 (TV2-W01)
## Đề tài: Phân tích dữ liệu đánh giá trò chơi trên Steam (Steam Reviews Analytics)

> **Mã nhiệm vụ:** `TV2-W01`  
> **Người thực hiện:** TV2 — Kỹ sư Xử lý dữ liệu lớn & Machine Learning  
> **Người review chéo:** TV1, TV3  
> **Nguồn dữ liệu:** [Kaggle — najzeko/steam-reviews-2021](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021/data)  
> **Tệp dữ liệu thực tế:** `data/landing/steam_reviews.csv` (Dung lượng: 8,171,787,229 bytes ~ 8.17 GiB)

---

## 1. Thông tin chung về bộ dữ liệu

- **Quy mô toàn bộ (Full Tier):** Khoảng 21.6 triệu bản ghi đánh giá của hơn 300 tựa game trên nền tảng Steam, thu thập qua Steam Web API chính thức.
- **Dung lượng tệp CSV thô:** 8.17 GB (chưa nén).
- **Mã hóa ký tự:** UTF-8 với sự đa dạng ngôn ngữ rất lớn (tiếng Anh, Trung, Nga, Thổ Nhĩ Kỳ, Ba Lan, Việt Nam, Hàn Quốc...).
- **Giấy phép:** GPL-2.0.

---

## 2. Khảo sát cấu trúc Header thực tế (23 Cột)

Đối chiếu trực tiếp từ header của tệp `data/landing/steam_reviews.csv`:

```csv
,app_id,app_name,review_id,language,review,timestamp_created,timestamp_updated,recommended,votes_helpful,votes_funny,weighted_vote_score,comment_count,steam_purchase,received_for_free,written_during_early_access,author.steamid,author.num_games_owned,author.num_reviews,author.playtime_forever,author.playtime_last_two_weeks,author.playtime_at_review,author.last_played
```

| STT | Tên cột thực tế trong CSV | Kiểu dữ liệu thô | Ý nghĩa nghiệp vụ | Mức độ quan trọng |
|:---:|---|---|---|:---:|
| 0 | `""` (Cột không tên đầu tiên) | `integer` | Chỉ số dòng (index) sinh ra khi xuất từ Pandas DataFrame; sẽ được loại bỏ trong tầng Silver. | Phụ |
| 1 | `app_id` | `string/int` | ID định danh trò chơi trên Steam Store (ví dụ: `292030` cho The Witcher 3). | **Cốt lõi** |
| 2 | `app_name` | `string` | Tên thương mại đầy đủ của trò chơi. | **Cốt lõi** |
| 3 | `review_id` | `string/int` | ID duy nhất của bài đánh giá do Steam cấp. Khóa chính để Deduplication. | **Cốt lõi** |
| 4 | `language` | `string` | Ngôn ngữ bài viết (ví dụ: `english`, `schinese`, `russian`...). | **Cốt lõi** |
| 5 | `review` | `string` | Nội dung văn bản đánh giá. Có thể chứa xuống dòng, ký tự Unicode, emoji. | **Cốt lõi** |
| 6 | `timestamp_created` | `integer` | Thời điểm tạo bài đánh giá (Unix epoch timestamp, tính bằng giây). | **Cốt lõi** |
| 7 | `timestamp_updated` | `integer` | Thời điểm cập nhật bài đánh giá gần nhất (Unix epoch timestamp). | **Cốt lõi** |
| 8 | `recommended` | `boolean` | Nhãn khuyến nghị (`True`: Khuyên chơi, `False`: Không khuyên chơi). Nhãn mục tiêu của ML. | **Cốt lõi** |
| 9 | `votes_helpful` | `integer` | Số lượng người dùng khác bình chọn đánh giá này hữu ích. | Mở rộng |
| 10 | `votes_funny` | `integer` | Số lượng người dùng bình chọn đánh giá này hài hước. | Mở rộng |
| 11 | `weighted_vote_score` | `float` | Điểm số trọng số mức độ tin cậy của đánh giá do thuật toán Steam tính. | Mở rộng |
| 12 | `comment_count` | `integer` | Số lượng bình luận trao đổi bên dưới bài đánh giá. | Mở rộng |
| 13 | `steam_purchase` | `boolean` | Người dùng mua game trực tiếp trên Steam (`True`) hay kích hoạt qua key ngoài (`False`). | Mở rộng |
| 14 | `received_for_free` | `boolean` | Nhận game miễn phí (do tặng hoặc promotional gift). | Mở rộng |
| 15 | `written_during_early_access` | `boolean` | Đánh giá được viết trong giai đoạn Early Access (thử nghiệm sớm) hay bản phát hành chính thức. | Mở rộng |
| 16 | `author.steamid` | `string` | Định danh tài khoản Steam của tác giả (64-bit int). | Mở rộng |
| 17 | `author.num_games_owned` | `integer` | Tổng số lượng tựa game mà tác giả sở hữu trong tài khoản Steam. | Mở rộng |
| 18 | `author.num_reviews` | `integer` | Tổng số bài đánh giá mà tác giả đã từng viết trên Steam. | Mở rộng |
| 19 | `author.playtime_forever` | `float` | Tổng thời gian chơi game tính đến thời điểm cào dữ liệu (đơn vị: phút). | **Cốt lõi** |
| 20 | `author.playtime_last_two_weeks` | `float` | Thời gian chơi trong 2 tuần gần nhất (đơn vị: phút). | Mở rộng |
| 21 | `author.playtime_at_review` | `float` | Thời gian chơi tại thời điểm người dùng bấm nút đăng bài đánh giá (đơn vị: phút). | **Cốt lõi** |
| 22 | `author.last_played` | `float` | Thời điểm lần cuối người dùng chơi game (Unix epoch timestamp). | Mở rộng |

---

## 3. Bảy trường dữ liệu trọng tâm phục vụ 5 câu hỏi phân tích

Nhóm chốt 7 nhóm trường dữ liệu cốt lõi bắt buộc phải có mặt và làm sạch ở tầng Silver:
1. **`review_id`:** Khóa chính duy nhất. Mọi bản ghi thiếu `review_id` sẽ bị loại vào Quarantine. Dùng để Deduplication giữ bản ghi có `timestamp_updated` mới nhất.
2. **`app_id` & `app_name`:** Chiều phân tích theo tựa game (Game dimension), phục vụ xếp hạng trò chơi và bộ lọc Dashboard.
3. **`language`:** Chiều phân tích cộng đồng ngôn ngữ, phân loại thị trường game.
4. **`review`:** Dữ liệu văn bản nguồn để trích xuất đặc trưng (TF-IDF) cho mô hình học máy Spark MLlib.
5. **`recommended`:** Nhãn mục tiêu nhị phân (`True`/`False`), dùng để tính tỷ lệ hài lòng và huấn luyện mô hình phân loại.
6. **`timestamp_created` & `timestamp_updated`:** Chiều phân tích thời gian theo tháng/năm.
7. **`author.playtime_at_review` (và `author.playtime_forever` dự phòng):** Chiều phân tích mối tương quan giữa độ gắn bó (thời lượng chơi) và mức độ hài lòng.

---

## 4. Kết quả Phân tích thống kê trên Mẫu thực tế (10.000 bản ghi)

Được đo lường trực tiếp qua công cụ Python trên `data/sample/steam_reviews_sample_10k.csv`:

### 4.1. Phân bố ngôn ngữ (Top 5 Languages)
- Tiếng Trung giản thể (`schinese`): 2,470 bản ghi (24.70%)
- Tiếng Anh (`english`): 2,330 bản ghi (23.30%)
- Tiếng Nga (`russian`): 1,728 bản ghi (17.28%)
- Tiếng Thổ Nhĩ Kỳ (`turkish`): 961 bản ghi (9.61%)
- Tiếng Ba Lan (`polish`): 718 bản ghi (7.18%)
- Các ngôn ngữ khác: 1,793 bản ghi (17.93%)

*Nhận xét:* Dữ liệu phản ánh tính toàn cầu mạnh mẽ. Tập con tiếng Anh chiếm khoảng 23.3%, là tập dữ liệu mục tiêu lý tưởng cho mô hình NLP Spark MLlib.

### 4.2. Phân bố nhãn khuyến nghị (Target Distribution)
- `recommended = True`: 9,710 bản ghi (**97.10%**)
- `recommended = False`: 290 bản ghi (**2.90%**)

*Cảnh báo kỹ thuật quan trọng:*
Tựa game *The Witcher 3: Wild Hunt* có tỷ lệ đánh giá tích cực áp đảo (97.1%). Hiện tượng này cho thấy dữ liệu đánh giá game có hiện tượng **mất cân bằng lớp nghiêm trọng (Severe Class Imbalance)**.
- Mô hình Majority Baseline (luôn đoán True) sẽ đạt độ chính xác (Accuracy) giả tạo tới 97.1%, nhưng Macro-F1 hoặc Recall của lớp False sẽ bằng 0!
- Do đó, độ đo quyết định cho mô hình MLlib của nhóm **bắt buộc phải là Macro-F1 và PR-AUC**, đồng thời cần thử nghiệm kỹ thuật đánh trọng số lớp (`classWeightCol`) trong Logistic Regression.

### 4.3. Chất lượng dữ liệu & Tỷ lệ giá trị thiếu (Missing Values)
- `review_id`, `app_id`, `app_name`, `recommended`: **0% null** (100% hợp lệ).
- `review` (văn bản): **41 bản ghi rỗng** (0.41%). Đánh giá không có nội dung chữ vẫn hợp lệ cho thống kê tỷ lệ khuyến nghị, nhưng phải lọc bỏ trước khi đưa vào pipeline TF-IDF của Spark MLlib.
- `author.playtime_at_review`: Có giá trị thực tế trải dài từ 0 phút đến hàng trăm nghìn phút (xuất hiện hiện tượng treo máy AFK sinh ra outlier, cần giữ nguyên trong Silver và xử lý phân nhóm bucket ở Gold).

---

## 5. Kết luận khảo sát cho các giai đoạn tiếp theo

1. Bộ dữ liệu hoàn toàn khớp với hợp đồng dữ liệu dự kiến và phù hợp xuất sắc cho 5 câu hỏi phân tích của đề tài.
2. Việc sử dụng `CSVReader` theo Record trong NiFi và PySpark là bắt buộc vì bài đánh giá chứa nhiều dòng text xuống dòng (`\n`).
3. Đã xác định rõ tiêu chí lọc: giữ toàn bộ cho thống kê Gold, chỉ lọc `language == 'english'` và `review IS NOT NULL` khi huấn luyện mô hình phân loại văn bản Spark MLlib.
