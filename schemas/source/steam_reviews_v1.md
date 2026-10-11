# Schema source-v1: `steam_reviews.csv`

- **Version:** source-v1 (trạng thái: chờ TV1/TV3 review)
- **Dataset:** `najzeko/steam-reviews-2021` v1, SHA-256 `0e6f8e9c…e882759`
- **Grain:** 1 dòng = 1 review (có 134.927 dòng trùng `review_id`, xem docs/data/02)
- **Định dạng:** CSV UTF-8, có header, phân cách `,`, quote `"`, escape `"` (nhân đôi), review có thể xuống dòng trong dấu nháy. **Phải dùng parser theo record**, không cắt theo dòng.
- **Code tương ứng:** `src/steam_reviews/infrastructure/spark/source_schema.py`

## Header (đúng thứ tự, 23 cột)

```
,app_id,app_name,review_id,language,review,timestamp_created,timestamp_updated,recommended,votes_helpful,votes_funny,weighted_vote_score,comment_count,steam_purchase,received_for_free,written_during_early_access,author.steamid,author.num_games_owned,author.num_reviews,author.playtime_forever,author.playtime_last_two_weeks,author.playtime_at_review,author.last_played
```

| # | Cột | Dạng giá trị thô | Ví dụ |
|---|---|---|---|
| 0 | *(rỗng)* | số nguyên | `3` |
| 1 | app_id | số nguyên | `292030` |
| 2 | app_name | chuỗi | `The Witcher 3: Wild Hunt` |
| 3 | review_id | số nguyên | `85184605` |
| 4 | language | mã ngôn ngữ Steam | `english` |
| 5 | review | chuỗi, có thể rỗng/nhiều dòng | `"One of the best RPG's of all time, ..."` |
| 6–7 | timestamp_created / _updated | epoch giây | `1611379970` |
| 8 | recommended | `True` / `False` | `True` |
| 9–10, 12 | votes_helpful, votes_funny, comment_count | số nguyên | `0` |
| 11 | weighted_vote_score | số thực | `0.0` |
| 13–15 | steam_purchase, received_for_free, written_during_early_access | `True` / `False` | `False` |
| 16 | author.steamid | số 17 chữ số | *(định danh cá nhân)* |
| 17–18 | author.num_games_owned, author.num_reviews | số nguyên | `5` |
| 19–21 | author.playtime_forever / _last_two_weeks / _at_review | số thực, **phút** | `5524.0` |
| 22 | author.last_played | epoch giây (số thực) | `1611383744.0` |

## Gợi ý cho TV1 (NiFi)

- CSVReader: `Treat First Line as Header = true`, quote `"`, escape `"`, encoding UTF-8. Cột đầu không có tên, nên dùng schema tường minh hoặc đặt tên khi suy luận.
- Không dùng SplitText (cắt theo dòng), vì review có xuống dòng bên trong dấu nháy.
- Kiểm tra header của mỗi lô khớp đúng 23 cột trên. Nếu khác, đó là lỗi cấp tệp và chuyển sang nhánh lỗi.
- Dùng `tests/fixtures/reviews_edge_cases.csv` (16 dòng, gồm review nhiều dòng, dấu nháy, Unicode, nhãn sai, ID trùng) để thử luồng.
