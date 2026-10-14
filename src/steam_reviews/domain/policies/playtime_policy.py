"""Chính sách nghiệp vụ phân nhóm thời lượng chơi (Playtime Policy)."""

from typing import Optional

# Các khoảng thời lượng chơi chuẩn hóa (tính bằng phút)
BUCKET_LESS_THAN_2H = "<2h"       # 0 đến < 120 phút (thời hạn Refund của Steam)
BUCKET_2H_TO_10H = "2-10h"         # 120 đến < 600 phút
BUCKET_10H_TO_50H = "10-50h"       # 600 đến < 3000 phút
BUCKET_50H_TO_100H = "50-100h"     # 3000 đến < 6000 phút
BUCKET_MORE_THAN_100H = ">100h"    # >= 6000 phút
BUCKET_UNKNOWN = "unknown"

BUCKET_ORDER_MAP = {
    BUCKET_LESS_THAN_2H: 1,
    BUCKET_2H_TO_10H: 2,
    BUCKET_10H_TO_50H: 3,
    BUCKET_50H_TO_100H: 4,
    BUCKET_MORE_THAN_100H: 5,
    BUCKET_UNKNOWN: 6,
}


def categorize_playtime_bucket(playtime_minutes: Optional[float]) -> str:
    """
    Phân loại thời lượng chơi (phút) vào các nhóm chuẩn hóa theo logic nghiệp vụ của Steam:
    - '<2h': Dưới 2 giờ (chính sách hoàn tiền của Steam).
    - '2-10h': Trải nghiệm ban đầu.
    - '10-50h': Người chơi hoàn thành cốt truyện cơ bản.
    - '50-100h': Người chơi gắn bó, cày cuốc.
    - '>100h': Người chơi kỳ cựu (hardcore gamer).
    - 'unknown': Không có thông tin hoặc giá trị âm bất thường.
    """
    if playtime_minutes is None or playtime_minutes < 0:
        return BUCKET_UNKNOWN
    if playtime_minutes < 120.0:
        return BUCKET_LESS_THAN_2H
    if playtime_minutes < 600.0:
        return BUCKET_2H_TO_10H
    if playtime_minutes < 3000.0:
        return BUCKET_10H_TO_50H
    if playtime_minutes < 6000.0:
        return BUCKET_50H_TO_100H
    return BUCKET_MORE_THAN_100H


def get_playtime_bucket_order(bucket: str) -> int:
    """Trả về thứ tự sắp xếp của nhóm thời lượng chơi để hiển thị đúng trên biểu đồ."""
    return BUCKET_ORDER_MAP.get(bucket, 99)


def minutes_to_hours(minutes: Optional[float]) -> Optional[float]:
    """Quy đổi từ phút sang giờ, làm tròn 2 chữ số thập phân."""
    if minutes is None or minutes < 0:
        return None
    return round(minutes / 60.0, 2)
