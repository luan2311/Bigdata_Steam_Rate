"""Chính sách nghiệp vụ về nhãn khuyến nghị và tính toán tỷ lệ an toàn mẫu số 0."""

from typing import Any, Iterable, Optional, Tuple


def safe_recommendation_rate(recommended_count: int, total_reviews: int) -> Optional[float]:
    """
    Tính tỷ lệ khuyến nghị an toàn tuyệt đối với mẫu số 0 (Zero-Division Safe).
    Nếu total_reviews <= 0 thì trả về None thay vì ném ra ngoại lệ ZeroDivisionError.
    
    Công thức:
        ratio = recommended_count / total_reviews
    """
    if total_reviews <= 0:
        return None
    if recommended_count < 0:
        return 0.0
    if recommended_count > total_reviews:
        return 1.0
    return round(float(recommended_count) / float(total_reviews), 4)


def parse_recommended_label(raw_value: Any) -> bool:
    """
    Chuẩn hóa nhãn khuyến nghị từ dữ liệu thô sang boolean chuẩn.
    Xử lý an toàn các định dạng chuỗi: 'True', 'true', '1', 't', 'False', 'false', '0', 'f'.
    """
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, (int, float)):
        return bool(raw_value != 0)
    if isinstance(raw_value, str):
        val = raw_value.strip().lower()
        if val in ("true", "1", "t", "yes", "y"):
            return True
        if val in ("false", "0", "f", "no", "n"):
            return False
    raise ValueError(f"Không thể phân tích nhãn khuyến nghị từ giá trị: {raw_value!r}")


def label_to_numeric(recommended: bool) -> float:
    """Chuyển đổi nhãn boolean sang định dạng số thực cho mô hình MLlib (1.0 hoặc 0.0)."""
    return 1.0 if recommended else 0.0


def aggregate_recommendation_rate(pairs: Iterable[Tuple[int, int]]) -> Optional[float]:
    """
    Quy tắc gộp tỷ lệ khuyến nghị chuẩn:
    Cộng tổng tử số và tổng mẫu số của tất cả các nhóm rồi mới chia.
    Tuyệt đối KHÔNG lấy trung bình cộng các tỷ lệ của từng nhóm/lô.
    
    Input: Iterable các cặp (recommended_count, total_reviews)
    """
    total_rec = 0
    total_rev = 0
    for rec, rev in pairs:
        total_rec += rec
        total_rev += rev
    return safe_recommendation_rate(total_rec, total_rev)
