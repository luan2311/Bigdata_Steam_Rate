# TV2-D03…D09: Kết quả ETL, gold và mô hình ở mức Core

- **Run:** `core-20261011-v1`, chạy ngày 11/10/2026 bằng Spark 3.5.3 `local[*]` trên máy TV2 (11,7 GB RAM)
- **Đầu vào:** `data/sample/core.csv`, 1.044.450 dòng, SHA-256 `cdb6e5a3…d5140`, là mẫu 4,8% theo hash `review_id` của dataset Full
- **Phạm vi:** **Core (subset), chưa chạy trên cụm**. Mọi số dưới đây chỉ đại diện cho mẫu này
- **Số liệu gốc:** `artifacts/metrics/core-20261011-v1/*.json`; cách chạy lại xem [runbook](../runbooks/tv2_local_pipeline.md)

## 1. ETL → silver (D03, D04)

| Chỉ số | Giá trị |
|---|---:|
| Dòng đọc được (`rows_parsed`) | 1.044.450 |
| Quarantine (theo lý do) | 0 (dataset sạch về ID/nhãn) |
| Hợp lệ trước dedup | 1.044.450 |
| Trùng bị loại | 6.379 (toàn bộ là khối Hollow Knight bị lặp) |
| **Silver** | **1.038.071** |
| Text rỗng (giữ lại, loại khỏi ML) | 1.616 |
| Thiếu `playtime_at_review` | 1.181 |

Đối soát V4: `1.044.450 = 0 + 1.044.450` và `1.038.071 = 1.044.450 − 6.379`. Không có lỗi.

Fixture `tests/fixtures/reviews_edge_cases.csv` (16 dòng) kiểm tra: CSV nhiều dòng, dấu nháy kép, Unicode/emoji, nhãn rỗng hoặc lạ, ID rỗng hoặc không phải số, thiếu app, trùng ID có `updated` khác nhau và bằng nhau, text toàn khoảng trắng, thiếu timestamp. Mọi ca đều cho đúng kết quả mong đợi (`tests/integration/test_spark_cleaning.py`).

## 2. Gold v1 (D05)

| Bảng | Số dòng |
|---|---:|
| game_summary | 315 |
| monthly_summary | 109.113 |
| language_summary | 28 |
| playtime_summary | 22.019 |
| quality_summary | 8 |

**Kiểm tra độc lập:** `scripts/verify_gold.py` tính lại toàn bộ 4 bảng bằng pandas trực tiếp từ CSV, không dùng code Spark. Kết quả **0 dòng lệch** ở cả 4 bảng, công thức `recommended_rate` đúng (`artifacts/metrics/core-20261011-v1/verify_gold.json`). Mẫu smoke cũng khớp 0 lệch.

### Số liệu sơ bộ cho TV3 (Core, chỉ là quan sát trên mẫu)

1. **Tỷ lệ khuyến nghị chung** 87,4% trên 1.038.071 review. Nhãn mất cân bằng mạnh.
2. **Q1:** PUBG có nhiều review nhất mẫu (79.145) nhưng tỷ lệ khuyến nghị chỉ 54,1%. Terraria (32.399 review, 97,8%) và Garry's Mod (31.490, 96,5%) cao hơn hẳn. Thấp nhất trong các game ≥ 100 review: Umbrella Corps 23,3% (120 review), RollerCoaster Tycoon World 25,5% (251 review).
3. **Q2:** năm 2020 có 375.217 review (36% mẫu). Tỷ lệ khuyến nghị giảm từ trên 94% (2010–2014) xuống khoảng 78–80% (2017–2018), rồi tăng lại 91,4% năm 2020. Tháng 01/2021 chỉ có dữ liệu đến ngày 23.
4. **Q3:** tiếng Anh 460.912 review (44%), tỷ lệ 89,1%. Tiếng Trung giản thể 178.308 review, tỷ lệ thấp nhất trong nhóm lớn (76,9%). Tiếng Bồ Đào Nha (Brazil) 94,4%.
5. **Q4:** người chơi dưới 2 giờ lúc viết review có tỷ lệ khuyến nghị 70,6%, thấp nhất. Nhóm 10–50 giờ cao nhất (91,1%), nhóm từ 100 giờ trở lên giảm còn 83,9%. Đây là **liên hệ, không phải nhân quả**.

Các nhận xét trên dùng được cho slide tiến độ, nhưng phải ghi rõ "mẫu Core 4,8%". Khi có run Full trên cụm thì thay bằng số liệu Full.

## 3. Dữ liệu ML và chia tập (D06, D07)

| Bước | Số dòng |
|---|---:|
| Silver | 1.038.071 |
| Không phải tiếng Anh (loại) | 577.159 |
| Tiếng Anh nhưng text rỗng (loại) | 830 |
| Vượt giới hạn 200.000 dòng (loại theo hash `review_id`, tất định) | 260.082 |
| **Tập ML** | **200.000** |

| Split | Dòng | Tỷ lệ | Nhãn 1 (khuyến nghị) | Nhãn 0 |
|---|---:|---:|---:|---:|
| train | 138.661 | 69,3% | 123.491 (89,1%) | 15.170 |
| validation | 29.202 | 14,6% | 26.003 (89,0%) | 3.199 |
| test | 32.137 | 16,1% | 28.822 (89,7%) | 3.315 |

- **Cách chia:** bucket = `pmod(xxhash64("steam2021-tv2", normalize(text)), 10000)`. Bucket < 7000 vào train, < 8500 vào validation, còn lại vào test. Các review có text giống nhau sau chuẩn hóa luôn nằm cùng một tập. Tỷ lệ thực tế lệch nhẹ so với 70/15/15 vì các text ngắn hay lặp lại (ví dụ "good game") tạo thành nhóm lớn.
- **Kiểm tra rò rỉ (D07):** số `review_id` nằm ở nhiều tập = **0**; số text hash nằm ở nhiều tập = **0**.
- **Feature** chỉ là `review_text`. Không dùng ID, votes, playtime, thời gian. IDF và LR chỉ fit trên train.

## 4. Baseline và chọn cấu hình trên validation (D06, D08)

Pipeline: RegexTokenizer → StopWordsRemover (giữ các từ phủ định: not, no, don't, …) → HashingTF (2^16) → IDF → LogisticRegression (maxIter 30).

| Cấu hình | regParam | Trọng số lớp | Val macro-F1 | Val recall(0) | Val recall(1) | Val PR-AUC(1) |
|---|---:|---|---:|---:|---:|---:|
| baseline đa số (luôn đoán 1) | — | — | 0,4710 | 0,000 | 1,000 | 0,890 |
| lr_reg001 | 0,01 | không | 0,7476 | 0,432 | 0,979 | 0,974 |
| lr_reg01 | 0,1 | không | 0,6698 | 0,259 | 0,991 | 0,980 |
| lr_reg001_weighted | 0,01 | có | 0,7740 | 0,688 | 0,928 | 0,970 |
| **lr_reg01_weighted** | **0,1** | **có** | **0,7840** | 0,667 | 0,940 | 0,975 |

- Chọn **lr_reg01_weighted** vì có macro-F1 trên validation cao nhất. Tập test **chưa được dùng** khi chọn.
- Trọng số lớp `n / (2·n_c)` (tính trên train) làm recall lớp "không khuyến nghị" tăng từ 0,26–0,43 lên 0,67–0,69, đổi lại recall lớp 1 giảm nhẹ.
- So với baseline, macro-F1 trên validation tăng **+0,313**, vượt mục tiêu nội bộ +0,10 trong Plan.md.

## 5. Đánh giá trên test (D09)

Chấm đúng một lần sau khi đã chốt cấu hình, baseline và mô hình dùng cùng 32.137 dòng test. Lớp dương là 1 (khuyến nghị).

| Mô hình | Macro-F1 | Accuracy | P(1) | R(1) | F1(1) | P(0) | R(0) | F1(0) | PR-AUC(1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline đa số | 0,4728 | 0,8968 | 0,897 | 1,000 | 0,946 | 0,000 | 0,000 | 0,000 | 0,897* |
| **lr_reg01_weighted** | **0,7858** | **0,9163** | 0,960 | 0,946 | 0,953 | 0,584 | 0,658 | 0,619 | 0,978 |

\* Baseline cho cùng một điểm cho mọi dòng, nên PR-AUC của nó bằng tỷ lệ lớp dương.

Confusion matrix của mô hình: TP 27.265, FN 1.557, FP 1.133, TN 2.182.

**Diễn giải trung thực:**
- Accuracy chỉ tăng từ 89,7% lên 91,6%, vì baseline đã đạt gần 90% nhờ mất cân bằng nhãn. Đây là lý do dùng macro-F1 làm thước đo chính.
- Lớp "không khuyến nghị" vẫn là điểm yếu: F1 = 0,62. Mô hình bắt được 66% review chê, và khi đoán "chê" thì đúng 58%.
- Model đã lưu tại `artifacts/models/core-20261011-v1/lr_reg01_weighted`. Thư mục này không commit lên Git; tạo lại bằng lệnh `ml-train` của runbook.

## 6. Phân tích 30 lỗi trên test (D09)

Mẫu lỗi lấy tất định (sắp theo hash `review_id`), lưu trong `test_error_examples.json`. Phân nhóm thủ công như sau:

| Nhóm lỗi | Số ca | Ví dụ (rút gọn) |
|---|---:|---|
| Khen chê lẫn lộn ("good game but …") | 8 | "good game but broken servers PLS FIX…" (nhãn 0, p₁ = 0,68) |
| Quá ngắn, thiếu thông tin | 7 | "Eeeee", "NO", "Meh, It's good", "Luck simulator" |
| Phủ định làm đảo nghĩa | 4 | "bugs fixed … not crashing anymore" (nhãn 1, p₁ = 0,32); "No death no doom…" |
| Mỉa mai, troll | 3 | "I really thought this was a great game… but happy games are lying" (nhãn 0) |
| Tiêu cực ngầm, so sánh, không có từ khóa chê | 3 | "nowhere near as deep as monster train…" |
| Nhãn mâu thuẫn với nội dung | 2 | "Still a buggy mess" nhưng nhãn 1 |
| Ghi `english` nhưng không phải tiếng Anh | 2 | "rumen izbra onq kurva…", "en peukuta" |
| Không có ý kiến (chép mô tả game) | 1 | "Key Highlights: Re-mastered for…" |

Ngoài ra có review chứa ký tự lỗi mã hóa `�` (ví dụ "it�s") ngay trong dữ liệu nguồn.

**Hướng cải thiện (chưa làm):** dùng n-gram 2 để bắt "not crashing" và "but broken"; xử lý review quá ngắn riêng; lọc ngôn ngữ thật thay vì tin cột `language`. Không đổi tập test để cải thiện điểm.

## 7. Giới hạn

- Mới chạy **Core trên máy local**, chưa chạy trên cụm 2 worker. Việc chạy Full và benchmark làm ở D10–D11 cùng TV1.
- Mô hình chỉ học **nhãn khuyến nghị từ văn bản tiếng Anh**. Không áp dụng cho ngôn ngữ khác, và đây không phải phân tích cảm xúc.
- Chia tập theo nhóm text nên test không chứa text trùng với train. Đây **không** phải phép thử dự báo theo thời gian.
- Nhận xét ở mục 2 là mô tả trên dữ liệu quan sát, không suy ra cho toàn bộ người chơi Steam và không suy ra quan hệ nhân quả.
