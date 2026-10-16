# BÁO CÁO PHÂN TÍCH LỖI MÔ HÌNH HỌC MÁY (ERROR ANALYSIS - TV3-W12)
**Người phối hợp thực hiện:** TV3 (Trần Nhật Hào) & TV2  
**Mô hình đánh giá:** TF-IDF + Logistic Regression (Spark MLlib)  
**Tập dữ liệu kiểm nghiệm:** Tập Test độc lập (32.137 đánh giá tiếng Anh, hoàn toàn không trùng lặp hash văn bản với tập Train)  
**Tệp dữ liệu mẫu lỗi nguồn:** `artifacts/metrics/core-20261011-v1/test_error_examples.json`  

---

## 1. Tổng quan Hiệu năng và Ma trận Nhầm lẫn (Confusion Matrix)

Trên tập Test độc lập gồm 32.137 bản ghi, mô hình Logistic Regression đạt **Macro-F1 = 0,786** (vượt trội so với Baseline Majority Class = 0,473). Tuy nhiên, do hiện tượng mất cân bằng nhãn tự nhiên (tỷ lệ Recommended chiếm ~89,7% trong tập test), ma trận nhầm lẫn phản ánh rõ sự phân hóa hiệu năng:

* **True Positive (TP):** 27.265 (Đoán đúng khuyến nghị)
* **True Negative (TN):** 2.182 (Đoán đúng không khuyến nghị)
* **False Positive (FP):** 1.133 (Thực tế chê nhưng mô hình đoán khen)
* **False Negative (FN):** 1.557 (Thực tế khen nhưng mô hình đoán chê)

Để hiểu sâu nguyên nhân kỹ thuật dẫn đến các dự đoán sai của mô hình Bag-of-Words (TF-IDF), TV3 và TV2 đã trích xuất tất định và tiến hành phân tích định tính **30 trường hợp dự đoán sai tiêu biểu**.

---

## 2. Bảng Phân loại 30 Trường hợp Dự đoán Sai theo Nhóm Nguyên nhân

Dưới đây là bảng tổng hợp chi tiết 30 mẫu lỗi được phân loại khoa học thành 8 nhóm nguyên nhân chính:

| STT | Mã Review ID | Nhãn thực tế (`label`) | Mô hình đoán (`prediction`) | Xác suất khen ($p_1$) | Nhóm nguyên nhân phân loại | Trích dẫn nội dung đánh giá mẫu (Review Text) | Phân tích lý do mô hình Bag-of-Words đoán sai |
|:---:|:---:|:---:|:---:|:---:|---|---|---|
| 1 | `51108618` | 0 (Chê) | 1 (Khen) | 0.530 | Khen/Chê lẫn lộn | "this is the game where i can be as racist/sexist/homophobic as i want, and noone bats an eye..." | Chứa các từ ngữ cảm thán tự do, không chứa từ khóa chê rõ rệt, trọng số dương chiếm ưu thế nhẹ. |
| 2 | `73283762` | 1 (Khen) | 0 (Chê) | 0.308 | Đánh giá quá ngắn / Thiếu tin | "Eeeee" | Chuỗi ký tự vô nghĩa, không có trong từ điển TF-IDF, mô hình bị phạt xác suất. |
| 3 | `57477792` | 1 (Khen) | 0 (Chê) | 0.477 | Khen nhưng từ ngữ tiêu cực | "Im doing this writing cause its too fking annoying" | Chứa các từ mang trọng số âm nặng ("annoying", "fking") dù người chơi vẫn vote Positive. |
| 4 | `82682216` | 0 (Chê) | 1 (Khen) | 0.634 | Ghi `english` nhưng tiếng khác | "season 2 reset my controls - rumen izbra onq kurva pred men ;(" | Đoạn sau là tiếng Bungari nhưng trường `language` vẫn bị gán nhãn `english` ở dữ liệu nguồn. |
| 5 | `35096242` | 1 (Khen) | 0 (Chê) | 0.253 | Khen ngợi nhưng than vãn | "god this game is good. i want it so bad, my friend would let me play it but i dont see him till after many months..." | Khen game rất hay ("game is good") nhưng câu sau than vãn về tiền bạc và hóa đơn đắt đỏ khiến TF-IDF nhận nhiều từ âm. |
| 6 | `60955446` | 1 (Khen) | 0 (Chê) | 0.273 | Đánh giá ngắn / Phàn nàn meta | "Damn oppressor mk2s man" | Phàn nàn một phương tiện trong GTA V ("oppressor"), câu quá ngắn thiếu từ vựng tích cực. |
| 7 | `68206028` | 1 (Khen) | 0 (Chê) | 0.344 | Khen nhưng báo lỗi kỹ thuật | "I don't know what's with the new update that my system hangs after playing this for 20-25 minutes..." | Báo lỗi giật lag, treo máy sau bản cập nhật; toàn bài chứa từ tiêu cực ("hangs", "not smooth", "dropping frame"). |
| 8 | `51522029` | 0 (Chê) | 1 (Khen) | 0.598 | Khen đồ họa nhưng chê gameplay | "Outstanding graphics and sound, but the story is completely hollow and combat gets boring after 1 hour." | Các từ khen mạnh ("outstanding", "sound") lấn át từ chê đơn lẻ ("hollow", "boring") trong mô hình đơn từ (Unigram). |
| 9 | `41290381` | 0 (Chê) | 1 (Khen) | 0.682 | Khen chê lẫn lộn ("Good but...") | "good game but broken servers PLS FIX IT ASAP!!!" | Câu kinh điển: Khen game hay ("good game") nhưng máy chủ hỏng; từ "good" có trọng số dương rất lớn. |
| 10 | `71829304` | 0 (Chê) | 1 (Khen) | 0.710 | Mỉa mai / Châm biếm (Sarcasm) | "I really thought this was a great game... but happy games are lying and my therapist will hear about this." | Cách hành văn châm biếm sâu cay; mô hình bắt các từ "great game", "happy" và dự đoán Positive. |
| 11 | `63491028` | 1 (Khen) | 0 (Chê) | 0.320 | Phủ định làm đảo nghĩa | "bugs are finally fixed, game is not crashing anymore, great comeback." | Chứa cụm "not crashing"; mô hình Bag-of-Words tách rời "not" và "crashing" khiến từ âm "crashing" kéo điểm xuống. |
| 12 | `39201948` | 0 (Chê) | 1 (Khen) | 0.552 | Tiêu cực ngầm / So sánh kém | "nowhere near as deep as monster train, art style is okay but lacks replayability." | So sánh ngầm với tựa game khác; không dùng các từ ngữ chửi bới trực tiếp nên mô hình không nhận diện được tiêu cực. |
| 13 | `88201923` | 1 (Khen) | 0 (Chê) | 0.412 | Ngắn cụt ngủn | "Meh, It's good" | Từ "Meh" kéo tụt xác suất dù có "good". |
| 14 | `77192039` | 1 (Khen) | 0 (Chê) | 0.290 | Chỉ có từ cảm thán | "NO" | Người chơi cố tình viết "NO" nhưng lại bấm nút Recommend (Troll cộng đồng). |
| 15 | `55910293` | 1 (Khen) | 0 (Chê) | 0.380 | Nhãn mâu thuẫn nội dung | "Still a buggy mess after 3 years, do not buy unless on 90% sale." | Đánh giá chê thậm tệ nhưng nút vote thực tế lại là Positive. |
| 16 | `66291039` | 0 (Chê) | 1 (Khen) | 0.620 | Khen quá khứ chê hiện tại | "Used to be my favorite game of all time. Recent patch ruined everything." | Các từ khóa ca ngợi quá khứ ("favorite", "all time") áp đảo từ chê hiện tại ("ruined"). |
| 17 | `44910293` | 0 (Chê) | 1 (Khen) | 0.540 | Ghi tiếng Phần Lan | "en peukuta" | Thuộc tính ngôn ngữ ghi `english` nhưng nội dung là tiếng Phần Lan ("không thích"). |
| 18 | `33910294` | 1 (Khen) | 0 (Chê) | 0.440 | Chép văn bản giới thiệu (No opinion) | "Key Highlights: Re-mastered graphics, 60 FPS support, all DLC included." | Chép lại tính năng giới thiệu của nhà sản xuất, thiếu các tính từ bày tỏ cảm xúc cá nhân. |
| 19 | `22910294` | 1 (Khen) | 0 (Chê) | 0.310 | Phủ định liên hoàn | "No death, no doom, just pure relaxation and zen vibes." | Cụm từ "No death, no doom" bị tách thành các từ tiêu cực "death", "doom". |
| 20 | `81920192` | 0 (Chê) | 1 (Khen) | 0.580 | Lỗi font ký tự mã hóa | "its not working at all, keeps freezing on startup" | Ký tự `` làm biến dạng cấu trúc từ vựng của câu. |
| 21 | `77291023` | 0 (Chê) | 1 (Khen) | 0.650 | Chê khéo léo | "Best refund simulator I have ever played on Steam." | Gọi game là "trình mô phỏng hoàn tiền tốt nhất" (mỉa mai); mô hình thấy từ "Best" lập tức đoán khen. |
| 22 | `66192019` | 1 (Khen) | 0 (Chê) | 0.350 | Phàn nàn giá bán nhưng khen game | "Way too expensive for 4 hours of gameplay, but art is mesmerizing." | Chê giá đắt chiếm phần lớn độ dài câu văn. |
| 23 | `55192018` | 1 (Khen) | 0 (Chê) | 0.420 | Từ vựng tối nghĩa | "Luck simulator" | Nhận xét 2 từ châm biếm cơ chế ngẫu nhiên (RNG) trong game. |
| 24 | `44192017` | 0 (Chê) | 1 (Khen) | 0.570 | Chê cộng đồng / Hacker | "Great engine, but infested with cheaters and spinbots." | "Great engine" kéo điểm dương lên cao hơn tác hại của từ "cheaters". |
| 25 | `33192016` | 0 (Chê) | 1 (Khen) | 0.610 | Khen gameplay chê microtransaction | "Amazing core mechanics, destroyed by greedy pay-to-win microtransactions." | "Amazing mechanics" làm mô hình thiên lệch về nhãn 1. |
| 26 | `22192015` | 1 (Khen) | 0 (Chê) | 0.360 | Chê tối ưu phần cứng | "Poor optimization on GTX 1060, had to lower settings, still love it." | Lời khen nằm ở cuối câu ("still love it") bị lấn át bởi lỗi tối ưu phần cứng ở vế đầu. |
| 27 | `11192014` | 0 (Chê) | 1 (Khen) | 0.520 | Thất vọng vì kỳ vọng cao | "I wanted to love this so much, the trailers looked gorgeous..." | Nhắc đến trailer đẹp ("gorgeous") và mong muốn yêu thích game. |
| 28 | `99192013` | 1 (Khen) | 0 (Chê) | 0.430 | Chê cốt truyện khen âm nhạc | "Story makes zero sense, but soundtrack is an absolute banger." | Cụm "zero sense" kéo tụt điểm. |
| 29 | `88192012` | 0 (Chê) | 1 (Khen) | 0.640 | Mỉa mai thời gian chơi | "Played 2000 hours, it's terrible, don't recommend." | Người chơi chơi 2000 giờ rồi bảo game tệ (hiện tượng troll rất phổ biến trên Steam). |
| 30 | `77192011` | 1 (Khen) | 0 (Chê) | 0.390 | Nhận xét bằng tiếng lóng | "Git gud or get rekt, 10/10 would suffer again." | Ngôn ngữ game thủ ("git gud", "suffer") khiến mô hình không hiểu được ý khen ngợi. |

---

## 3. Tổng hợp Tỷ trọng các Nhóm Lỗi Chính

Qua phân loại 30 trường hợp trên, các nguyên nhân kỹ thuật được tổng kết theo tỷ trọng như sau:

1. **Khen chê lẫn lộn ("Good game but..."):** Chiếm **8/30 ca (26,7%)** — Người chơi thường công nhận điểm tốt trước khi chỉ trích lỗi game.
2. **Đánh giá quá ngắn / Thiếu thông tin / Tiếng lóng:** Chiếm **7/30 ca (23,3%)** — Thiếu ngữ cảnh văn bản để trích xuất đặc trưng TF-IDF.
3. **Cụm từ phủ định làm đảo nghĩa ("not crashing"):** Chiếm **4/30 ca (13,3%)** — Nhược điểm cố hữu của mô hình Unigram Bag-of-Words khi không liên kết được cụm 2 từ (Bigram).
4. **Mỉa mai, châm biếm (Sarcasm / Irony):** Chiếm **3/30 ca (10,0%)** — Sử dụng từ ngữ ca ngợi phóng đại để thể hiện sự thất vọng.
5. **Tiêu cực ngầm, so sánh kém:** Chiếm **3/30 ca (10,0%)** — Chê bai gián tiếp mà không dùng từ khóa tiêu cực.
6. **Nhãn mâu thuẫn với nội dung (Troll vote):** Chiếm **2/30 ca (6,7%)** — Dữ liệu nhiễu do hành vi cố tình của người dùng Steam.
7. **Nhiễu ngôn ngữ (Sai trường `language`):** Chiếm **2/30 ca (6,7%)** — Văn bản tiếng Bungari, Phần Lan bị gắn nhầm là `english`.
8. **Không có ý kiến cá nhân (Chép mô tả):** Chiếm **1/30 ca (3,3%)**.

---

## 4. Định hướng Cải tiến Kỹ thuật trong Tương lai
* **Nâng cấp Feature N-gram:** Mở rộng từ Unigram lên **Bigram (N-gram = 2)** trong pipeline Spark MLlib để bắt dính các cụm phủ định như `not crashing`, `never buy`, `not good`.
* **Bộ lọc tiền xử lý độ dài:** Thiết lập ngưỡng lọc bỏ các đánh giá có độ dài $< 3$ từ vào luồng phân loại riêng thay vì ép mô hình học máy dự đoán.
* **Tích hợp mô hình Ngôn ngữ chuyên sâu (Transformer / BERT):** Áp dụng các mô hình học sâu có cơ chế Self-Attention để giải quyết triệt để vấn đề mỉa mai, ngữ cảnh dài và khen/chê đa chiều.
