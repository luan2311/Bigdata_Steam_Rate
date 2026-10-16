"""
Module hiển thị Trang 3: Thời gian chơi và Chất lượng dữ liệu.
Trực quan hóa phễu làm sạch và phân tích các khoảng giờ chơi [0, 2), [2, 10),...
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


def render_playtime_quality_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    st.header("Thời gian Chơi & Báo cáo Chất lượng Dữ liệu")

    st.subheader("1. Đối soát Chất lượng Tiền xử lý Dữ liệu (Pipeline Audit)")
    q = snapshot.quality_summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng bản ghi nạp thô", f"{q.raw_records:,}")
    col2.metric("Bản ghi hợp lệ (Silver)", f"{q.valid_records:,}")
    col3.metric("Bản ghi trùng lặp lọc bỏ", f"{q.duplicate_records:,}")
    col4.metric("Bản ghi cách ly (Quarantine)", f"{q.quarantine_records:,}")

    if q.quarantine_by_reason:
        st.markdown("**Phân loại lý do cách ly / lỗi cấu trúc:**")
        reason_data = [{"Lý do cách ly": k, "Số bản ghi": v} for k, v in q.quarantine_by_reason.items()]
        st.table(reason_data)

    st.markdown("---")
    st.subheader("2. Mối liên hệ giữa Giờ chơi (`playtime_forever`) và Tỷ lệ Khuyến nghị")
    st.markdown(
        "*Ghi chú phương pháp: Đây là phân tích tương quan quan sát trên tập dữ liệu, "
        "không đưa ra kết luận quan hệ nhân quả. Các khoảng giờ chơi không chồng chéo nhau.*"
    )

    playtime_data = [
        {
            "Khoảng thời gian chơi": item.bin_label,
            "Số lượng đánh giá": f"{item.total_reviews:,}",
            "Tỷ lệ Khuyến nghị (%)": f"{item.recommendation_rate * 100:.2f}%",
        }
        for item in snapshot.playtime_summary
    ]
    st.table(playtime_data)
