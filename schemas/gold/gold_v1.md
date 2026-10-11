# Schema gold-v1: bảng tổng hợp cho dashboard (bản nháp, chờ TV3 duyệt)

- **Vị trí:** `<lake>/gold/<run_id>/<bảng>/` (Parquet, mỗi bảng 1 tệp)
- **Code:** `src/steam_reviews/infrastructure/spark/analytics.py`
- **Cột chung mọi bảng:** `run_id`, `schema_version = "gold-v1"`
- **Nguyên tắc:** mọi bảng đều lưu **số đếm** `review_count` và `recommended_count`, không chỉ lưu tỷ lệ. Khi dashboard lọc hoặc gộp nhóm thì **cộng tử số và mẫu số trước rồi mới chia**. `recommended_rate` là null khi mẫu số bằng 0 (hiển thị N/A).

| Bảng | Grain (1 dòng =) | Cột | Câu hỏi |
|---|---|---|---|
| `game_summary` | 1 game | app_id, app_name, review_count, recommended_count, recommended_rate, first_review_at, last_review_at | Q1 |
| `monthly_summary` | game × tháng UTC × ngôn ngữ | app_id, created_month, language, review_count, recommended_count, recommended_rate | Q2 (lọc theo game/ngôn ngữ/tháng) |
| `language_summary` | 1 ngôn ngữ | language, review_count, recommended_count, recommended_rate | Q3 |
| `playtime_summary` | game × ngôn ngữ × nhóm giờ chơi | app_id, language, playtime_bucket, review_count, recommended_count, recommended_rate | Q4 |
| `quality_summary` | 1 chỉ số | metric, value | Trang chất lượng dữ liệu |

- `playtime_bucket` lấy theo `playtime_at_review_minutes / 60`: `[0,2)`, `[2,10)`, `[10,50)`, `[50,100)`, `[100,inf)`, cộng thêm `missing` và `negative`.
- `monthly_summary` chỉ gồm review có `created_at`. Tổng của bảng này bằng số dòng silver trừ số dòng thiếu ngày.
- Các metric trong `quality_summary`: `rows_parsed`, `invalid_records`, `valid_pre_dedup`, `duplicates_removed`, `silver_rows`, `blank_text`, `missing_created_at`, `missing_playtime_at_review`, và `invalid_<lý do>`.
- Ngưỡng xếp hạng game mặc định là ≥ 100 review (`MIN_REVIEWS_FOR_RANKING`); dashboard có thể cho người dùng đổi ngưỡng.

**Kiểm tra tự động khi build:** tổng `review_count` của `game_summary`, `language_summary` và `playtime_summary` phải bằng số dòng silver; tổng của `monthly_summary` phải bằng số dòng silver có ngày. Nếu lệch, lệnh trả exit code 1.

**Model metrics** nằm ở `artifacts/metrics/<run_id>/` (`model_selection.json`, `test_metrics.json`), không nằm trong lake.
