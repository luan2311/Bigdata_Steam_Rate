# Schema silver-v1: `reviews`

- **Vị trí:** `<lake>/silver/<run_id>/` (Parquet, snappy). Local: `data/lake/...`; cụm: `hdfs://.../steam/silver/<run_id>/`
- **Grain:** 1 dòng = 1 `review_id` duy nhất (đã dedup)
- **Khóa:** `review_id`
- **Code:** `src/steam_reviews/infrastructure/spark/cleaning.py`; quy tắc trong `domain/policies/{labels,quality,dedup}.py`

| Cột | Kiểu | Null | Ghi chú |
|---|---|---|---|
| review_id | string | không | chỉ gồm chữ số |
| app_id | string | không | chỉ gồm chữ số |
| app_name | string | có | |
| language | string | không | chữ thường; `unknown` nếu thiếu |
| review_text | string | có | nguyên bản |
| review_text_blank | boolean | không | |
| recommended | boolean | không | nhãn |
| created_at, updated_at | timestamp (UTC) | có | |
| created_month | string `yyyy-MM` | có | null khi thiếu `created_at` |
| votes_helpful, votes_funny, comment_count | long | có | |
| weighted_vote_score | double | có | |
| steam_purchase, received_for_free, written_during_early_access | boolean | có | |
| author_num_games_owned, author_num_reviews | long | có | |
| playtime_forever_minutes, playtime_last_two_weeks_minutes, playtime_at_review_minutes | double | có | phút; giữ outlier |
| author_last_played_at | timestamp | có | |
| dataset_version, batch_id, source_file, source_row, ingested_at, run_id | lineage | không | |

## Quarantine `<lake>/quarantine/<run_id>/`

Gồm các cột thô của nguồn cộng thêm `quarantine_reason` và `run_id`. Mỗi bản ghi lỗi có **đúng một** lý do; lý do được xét theo thứ tự `malformed_record, missing_review_id, invalid_review_id, missing_app_id, invalid_app_id, invalid_label`.

## Dedup

Với mỗi `review_id`, giữ bản đứng đầu khi sắp theo thứ tự: `updated_at` giảm dần (null xếp cuối) → `created_at` giảm dần → `source_file` tăng dần → `source_row` tăng dần.

## Đối soát (V4)

- `rows_parsed = Σ invalid_by_reason + valid_pre_dedup`
- `silver_rows = valid_pre_dedup − duplicates_removed`

Trong đó `duplicates_removed` được đếm độc lập (tổng của `count − 1` theo `review_id`), còn `silver_rows` đếm lại từ Parquet đã ghi. Nếu hai vế lệch nhau, lệnh trả exit code 1 và không tạo gold.
