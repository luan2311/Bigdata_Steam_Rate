"""
Module hiển thị Trang 1: Tổng quan dữ liệu thị trường Steam.
Tuân thủ Clean Architecture: chỉ nhận DashboardSnapshotDTO, không import Spark/HDFS.
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


def render_overview_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    meta = snapshot.metadata
    st.header("📊 Tổng quan Tập dữ liệu Đánh giá Trò chơi trên Steam")
    st.markdown(
        f"**Phiên bản dữ liệu:** `{meta.dataset_version}` | "
        f"**Run ID:** `{meta.run_id}` | "
        f"**Thời điểm trích xuất:** `{meta.created_at}`"
    )

    if meta.is_fixture:
        st.info("ℹ️ **Lưu ý:** Dashboard đang hiển thị dữ liệu fixture kiểm thử minh họa (TV3-D02/D03).")

    # Hàng KPI
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng đánh giá hợp lệ", f"{meta.total_valid_reviews:,}")
    col2.metric("Số lượng Trò chơi", f"{meta.total_games}")
    
    # Tính tỷ lệ khuyến nghị trung bình
    total_recs = sum(g.recommended_count for g in snapshot.game_summary)
    total_revs = sum(g.total_reviews for g in snapshot.game_summary)
    overall_rate = (total_recs / total_revs * 100) if total_revs > 0 else 0.0
    col3.metric("Tỷ lệ Khuyến nghị Chung", f"{overall_rate:.1f}%")

    st.markdown("---")

    # Phân bố Ngôn ngữ & Top Game
    st.subheader("🌐 Phân bố Ngôn ngữ Đánh giá (Top Languages)")
    st.markdown(
        "*Ghi chú phương pháp: Giữ nguyên nhóm `unknown` cho bản ghi khuyết ngôn ngữ; "
        "không suy đoán ngôn ngữ thành quốc tịch người chơi.*"
    )
    
    lang_data = [
        {"Ngôn ngữ": item.language, "Số lượng review": item.total_reviews, "Tỷ lệ Recommend (%)": round(item.recommendation_rate * 100, 2)}
        for item in snapshot.language_summary
    ]
    st.dataframe(lang_data, use_container_width=True)
