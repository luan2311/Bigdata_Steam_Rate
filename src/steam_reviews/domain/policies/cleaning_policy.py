"""Chính sách nghiệp vụ làm sạch dữ liệu và kiểm tra hợp lệ bản ghi."""

import re
from typing import Any, Optional


def is_valid_review_id(review_id: Any) -> bool:
    """Kiểm tra mã đánh giá có hợp lệ hay không (phải là số nguyên dương)."""
    if review_id is None:
        return False
    try:
        val = int(str(review_id).strip())
        return val > 0
    except (ValueError, TypeError):
        return False


def is_valid_app_id(app_id: Any) -> bool:
    """Kiểm tra mã trò chơi có hợp lệ hay không (phải là số nguyên dương)."""
    if app_id is None:
        return False
    try:
        val = int(str(app_id).strip())
        return val > 0
    except (ValueError, TypeError):
        return False


def clean_review_text(text: Optional[str]) -> Optional[str]:
    """
    Chuẩn hóa nội dung bài đánh giá:
    - Loại bỏ ký tự byte rác (\x00)
    - Loại bỏ khoảng trắng đầu/cuối và rút gọn khoảng trắng liên tiếp
    - Trả về None nếu nội dung rỗng sau khi làm sạch
    """
    if not text:
        return None
    cleaned = text.replace("\x00", "").strip()
    # Rút gọn khoảng trắng
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned if cleaned else None


def is_review_eligible_for_ml(
    review_text: Optional[str],
    language: Optional[str],
    min_length: int = 5,
    target_language: str = "english",
) -> bool:
    """
    Xác định bài đánh giá có đủ điều kiện đưa vào tập huấn luyện NLP hay không:
    - Phải đúng ngôn ngữ mục tiêu (mặc định 'english')
    - Văn bản phải tồn tại và có độ dài ký tự tối thiểu >= min_length
    """
    if not language or language.strip().lower() != target_language.lower():
        return False
    cleaned = clean_review_text(review_text)
    if not cleaned:
        return False
    return len(cleaned) >= min_length
