# TV2-D02: Kiểm kê dữ liệu nguồn

**Nguồn số liệu:** [`artifacts/manifests/source_manifest.json`](../../artifacts/manifests/source_manifest.json) và [`artifacts/manifests/profile_report.json`](../../artifacts/manifests/profile_report.json). Cả hai được sinh bởi `scripts/download_dataset.py` và `scripts/profile_dataset.py` ngày 11/10/2026.
Mọi số dưới đây là số **thô, trước làm sạch**, đọc toàn bộ tệp (Full). Không phải số ước lượng từ mẫu.

## 1. Tệp nguồn

| Thuộc tính | Giá trị |
|---|---|
| Tệp | `steam_reviews.csv` (một tệp duy nhất) |
| Kích thước | 8.171.787.229 byte (bản nén ZIP 3.193.406.910 byte) |
| SHA-256 | `0e6f8e9c791337cc19265deec0d6437f6ab84a840953d47f220acd8e0e882759` |
| Mã hóa / định dạng | UTF-8, CSV chuẩn RFC 4180 (dấu nháy kép nhân đôi, review có xuống dòng trong dấu nháy) |
| Số cột | 23 (cột đầu không tên là số thứ tự dòng) |
| Số bản ghi | **21.747.371**; 0 dòng lỗi cấu trúc khi parse |
| Thời gian đọc toàn bộ | 534 giây (pandas, đọc theo khối 500.000 dòng) |

## 2. Phát hiện chính

| # | Phát hiện | Số liệu | Quyết định |
|---|---|---|---|
| F1 | **Trùng `review_id`** | 134.927 ID xuất hiện đúng 2 lần. Toàn bộ là review của **Hollow Knight**, hai bản giống hệt nhau ở mọi cột, cách nhau đúng 17.861.097 dòng, tức một khối dữ liệu bị lặp | Dedup theo `review_id` là bắt buộc. Nếu không, Hollow Knight bị đếm 269.854 thay vì 134.927 |
| F2 | Nhãn mất cân bằng | `True` 19.022.610 (87,47%), `False` 2.724.761 (12,53%). Không có giá trị null hoặc lạ | Không có dòng nào vào quarantine vì nhãn. ML phải báo cáo recall từng lớp, macro-F1 và thử trọng số lớp |
| F3 | Text rỗng | 33.742 null; 39.963 rỗng hoặc chỉ có khoảng trắng | Giữ lại cho thống kê nhãn, loại khỏi ML |
| F4 | Thời gian | `timestamp_created` từ 2010-11-19 đến 2021-01-23 UTC (123 tháng). Năm 2020 chiếm 7,88 triệu (36%), tháng 01/2021 chỉ có đến ngày 23 | Biểu đồ tháng phải ghi chú tháng cuối chưa đủ; không gọi dataset là "review năm 2021" |
| F5 | `timestamp_updated` bất thường | Giá trị lớn nhất là 2042-05-11; 1 dòng có `updated < created` | Chỉ dùng `updated_at` để chọn bản mới khi dedup; không vẽ biểu đồ theo `updated_at` |
| F6 | Thời gian chơi | `playtime_at_review` null 25.682 dòng, không có giá trị âm, lớn nhất 3.228.103 phút (khoảng 53.800 giờ) | Đủ dữ liệu cho Q4. Giữ outlier, nhóm `[100,inf)` gom phần đuôi |
| F7 | Ngôn ngữ | 28 giá trị, không null. `english` 9.635.437 (44,3%), `schinese` 3.764.967, `russian` 2.348.900 | Phạm vi ML là tiếng Anh |
| F8 | Game | 315 `app_id`, mỗi ID chỉ một tên. Ít nhất 200 review/game, trung vị 22.437. PUBG nhiều nhất (1.644.255 review, tỷ lệ khuyến nghị 53,9%) | Ngưỡng xếp hạng mặc định 100 review không loại game nào ở mức Full; ở mẫu Core thì có game bị loại |
| F9 | Cột chứa định danh cá nhân | `author.steamid` | Bỏ khỏi silver, không đưa lên dashboard |

## 3. Phân bố nhãn theo ngôn ngữ (top 10, số thô)

| Ngôn ngữ | Review | Tỷ lệ khuyến nghị |
|---|---:|---:|
| english | 9.635.437 | 89,1% |
| schinese | 3.764.967 | 77,1% |
| russian | 2.348.900 | 89,2% |
| brazilian | 837.524 | 94,4% |
| spanish | 813.320 | 92,8% |
| german | 752.596 | 88,5% |
| turkish | 635.868 | 90,3% |
| koreana | 613.632 | 84,2% |
| french | 541.751 | 90,5% |
| polish | 495.529 | 94,6% |

Steam dùng mã ngôn ngữ riêng (`schinese`, `brazilian`, `latam`, `koreana`). Ngôn ngữ là ngôn ngữ review, **không suy ra quốc gia**.

## 4. Mẫu tái lập

| Mẫu | Quy tắc | Số dòng | Dùng cho |
|---|---|---:|---|
| smoke | `hash_pandas_object(review_id, hash_key='steam2021tv2seed') % 100000 < 48` | 10.485 | Thử nhanh toàn luồng, fixture cho TV1/TV3 |
| core | cùng hash, `< 4800` | 1.044.450 | ETL/EDA mức Core; ML lấy tối đa 200.000 review tiếng Anh |

Mẫu lấy theo hash ID nên không phụ thuộc thứ tự dòng, và smoke nằm trọn trong core. Hai bản trùng của cùng một ID luôn rơi vào cùng mẫu, nhờ đó kiểm thử được bước dedup. Mẫu là lấy ngẫu nhiên đều, không cân bằng nhãn, nên tỷ lệ trên mẫu đại diện được cho toàn tập (sai số lấy mẫu).

## 5. Tài liệu liên quan

- Data dictionary: [03_data_dictionary.md](03_data_dictionary.md)
- Schema: [source](../../schemas/source/steam_reviews_v1.md), [silver](../../schemas/silver/reviews_v1.md), [gold](../../schemas/gold/gold_v1.md)
