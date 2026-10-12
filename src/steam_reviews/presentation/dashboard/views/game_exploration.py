"""
Module hiển thị Trang 2: Khám phá và xếp hạng trò chơi theo tỷ lệ khuyến nghị.
Hỗ trợ bộ lọc ngưỡng mẫu số >= 100 theo đúng quy định Plan.md.
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


def render_game_exploration_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    st.header("🎮 Khám phá & Xếp hạng Trò chơi")
    st.markdown(
        "Xếp hạng các trò chơi theo tỷ lệ người chơi khuyến nghị (`recommendation_rate`). "
        "Chỉ áp dụng xếp hạng cho các trò chơi thỏa mãn ngưỡng số lượng đánh giá tối thiểu."
    )

    # Bộ lọc tương tác
    col_filter1, col_filter2 = st.columns(2)
    threshold = col_filter1.slider("Ngưỡng số lượng đánh giá tối thiểu:", min_value=10, max_value=2000, value=100, step=10)
    
    # Lọc danh sách game
    filtered_games = [g for g in snapshot.game_summary if g.total_reviews >= threshold]
    filtered_games.sort(key=lambda x: x.recommendation_rate, reverse=True)

    col_filter2.metric("Số trò chơi thỏa mãn ngưỡng", len(filtered_games))

    if not filtered_games:
        st.warning(f"⚠️ Không có trò chơi nào có trên {threshold} lượt đánh giá. Vui lòng hạ ngưỡng lọc!")
        return

    # Hiển thị bảng xếp hạng
    table_data = [
        {
            "Thứ hạng": idx + 1,
            "App ID": g.app_id,
            "Tên trò chơi": g.app_name,
            "Tổng số review": f"{g.total_reviews:,}",
            "Số lượt Recommend": f"{g.recommended_count:,}",
            "Tỷ lệ Khuyến nghị": f"{g.recommendation_rate * 100:.2f}%",
        }
        for idx, g in enumerate(filtered_games)
    ]
    st.subheader(rf"🏆 Bảng Xếp Hạng Top Games (Ngưỡng $\ge$ {threshold} reviews)")
    st.dataframe(table_data, use_container_width=True)

    # Hiển thị xu hướng theo tháng
    st.markdown("---")
    st.subheader("📈 Xu hướng Đánh giá theo Thời gian (UTC)")
    st.markdown("*Dữ liệu tổng hợp theo từng tháng đối với các bản ghi có nhãn thời gian hợp lệ.*")
    monthly_data = [
        {
            "Tháng (UTC)": m.year_month,
            "Tổng review": m.total_reviews,
            "Lượt Recommend": m.recommended_count,
            "Tỷ lệ Recommend (%)": f"{m.recommendation_rate * 100:.2f}%",
        }
        for m in snapshot.monthly_summary
    ]
    st.dataframe(monthly_data, use_container_width=True)
