# Data dictionary (source-v1 → silver-v1)

Null/giá trị đo trên toàn bộ 21.747.371 dòng nguồn ([profile_report.json](../../artifacts/manifests/profile_report.json)).

| Cột nguồn | Cột silver | Kiểu silver | Ý nghĩa | Null nguồn | Quy tắc |
|---|---|---|---|---:|---|
| *(không tên)* | `source_row` | long | Số thứ tự dòng trong tệp | 0 | Chỉ dùng truy vết và phá hòa khi dedup; không phải khóa |
| `app_id` | `app_id` | string | Mã game Steam | 0 | Bắt buộc, chỉ gồm chữ số; nếu sai thì quarantine |
| `app_name` | `app_name` | string | Tên game | 0 | Mỗi `app_id` có đúng 1 tên |
| `review_id` | `review_id` | string | Mã review Steam (recommendationid) | 0 | Khóa; bắt buộc, chỉ gồm chữ số; dedup theo cột này |
| `language` | `language` | string | Ngôn ngữ review (mã của Steam) | 0 | Cắt khoảng trắng, chữ thường; thiếu thì gán `unknown` |
| `review` | `review_text` | string | Nội dung review | 33.742 | Giữ nguyên bản gốc; `review_text_blank` = rỗng/khoảng trắng |
| — | `review_text_blank` | boolean | Text rỗng | — | Loại khỏi ML, vẫn dùng cho thống kê nhãn |
| `timestamp_created` | `created_at` | timestamp UTC | Thời điểm viết | 0 | Epoch giây; giá trị không dương thì để null |
| — | `created_month` | string `yyyy-MM` | Tháng UTC của `created_at` | — | Grain của `monthly_summary` |
| `timestamp_updated` | `updated_at` | timestamp UTC | Lần sửa cuối | 0 | Có giá trị lỗi tới 2042; chỉ dùng để dedup |
| `recommended` | `recommended` | boolean | Khuyến nghị (nhãn) | 0 | Chỉ chấp nhận `True`/`False`; khác thì quarantine, không đổi thành `false` |
| `votes_helpful` | `votes_helpful` | long | Lượt "hữu ích" | 0 | Chỉ dùng mô tả; **không** dùng làm feature |
| `votes_funny` | `votes_funny` | long | Lượt "hài hước" | 0 | Như trên |
| `weighted_vote_score` | `weighted_vote_score` | double | Điểm hữu ích Steam | 0 | Như trên |
| `comment_count` | `comment_count` | long | Số bình luận | 0 | Như trên |
| `steam_purchase` | `steam_purchase` | boolean | Mua trên Steam | 0 | |
| `received_for_free` | `received_for_free` | boolean | Nhận miễn phí | 0 | |
| `written_during_early_access` | `written_during_early_access` | boolean | Viết khi Early Access | 0 | |
| `author.steamid` | *(bỏ)* | — | Định danh người viết | 0 | Định danh cá nhân: không lưu ở silver |
| `author.num_games_owned` | `author_num_games_owned` | long | Số game sở hữu (lúc thu thập) | 0 | |
| `author.num_reviews` | `author_num_reviews` | long | Số review đã viết | 0 | |
| `author.playtime_forever` | `playtime_forever_minutes` | double | Tổng phút chơi lúc thu thập | 2 | Không thay ngầm cho playtime lúc review |
| `author.playtime_last_two_weeks` | `playtime_last_two_weeks_minutes` | double | Phút chơi 2 tuần gần nhất | 2 | |
| `author.playtime_at_review` | `playtime_at_review_minutes` | double | Phút chơi lúc viết review | 25.682 | Dùng cho Q4; giá trị âm/thiếu tách thành nhóm riêng |
| `author.last_played` | `author_last_played_at` | timestamp UTC | Lần chơi cuối | 2 | |
| *(lineage)* | `dataset_version`, `batch_id`, `source_file`, `ingested_at`, `run_id` | | Truy vết | — | `batch_id = <version>-<sha256[:12]>-<level>` khi chạy local; NiFi cấp khi chạy cụm |

**Cột có dấu chấm** (`author.*`) là cột phẳng, không phải struct lồng nhau. Spark ánh xạ theo vị trí sang tên an toàn sau khi đã kiểm tra header.
