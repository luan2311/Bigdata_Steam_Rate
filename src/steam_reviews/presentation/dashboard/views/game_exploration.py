"""
Module hiển thị Trang 2: Khám phá và xếp hạng trò chơi theo tỷ lệ khuyến nghị.
Hỗ trợ bộ lọc ngưỡng mẫu số >= 100 theo đúng quy định Plan.md và biểu đồ trực quan hóa Plotly.
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO
from steam_reviews.presentation.dashboard.components.theme import render_hud_card
from steam_reviews.presentation.dashboard.components.charts import (
    create_game_bubble_scatter,
    create_top_games_bar,
    create_monthly_trend_chart,
)


def render_game_exploration_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    st.header("Khám phá & Xếp hạng Trò chơi (Game Exploration)")
    st.markdown(
        "Khám phá mối tương quan giữa quy mô cộng đồng người chơi và mức độ hài lòng (`recommendation_rate`). "
        "Áp dụng ngưỡng lọc tối thiểu nhằm loại trừ sai số mẫu nhỏ theo đúng phương pháp luận nghiên cứu."
    )

    all_games = snapshot.game_summary
    max_rev_in_data = max([g.total_reviews for g in all_games], default=2000)
    slider_max = max(2000, min(50000, max_rev_in_data // 2))

    # BỘ LỌC TƯƠNG TÁC
    with st.container():
        col_filter1, col_filter2, col_filter3 = st.columns([2, 1.5, 1.5])
        with col_filter1:
            threshold = st.slider(
                "Ngưỡng số lượng đánh giá tối thiểu (Review Threshold):",
                min_value=10,
                max_value=slider_max,
                value=min(100, slider_max),
                step=10 if slider_max <= 2000 else 50,
                help="Chỉ tính toán và xếp hạng các tựa game có số lượng review >= ngưỡng này",
            )
        with col_filter2:
            search_query = st.text_input(
                "Tìm kiếm theo tên game:",
                placeholder="VD: Counter-Strike, Dota, Witcher...",
            ).strip().lower()
        with col_filter3:
            sort_by = st.selectbox(
                "Sắp xếp theo:",
                ["Tỷ lệ Khuyến nghị (Cao nhất)", "Tổng số Đánh giá (Nhiều nhất)", "Số lượt Khuyên dùng"],
            )

    # Lọc và sắp xếp danh sách game
    filtered_games = [g for g in all_games if g.total_reviews >= threshold]
    if search_query:
        filtered_games = [g for g in filtered_games if search_query in g.app_name.lower()]

    if "Tỷ lệ Khuyến nghị" in sort_by:
        filtered_games.sort(key=lambda x: (x.recommendation_rate, x.total_reviews), reverse=True)
    elif "Tổng số Đánh giá" in sort_by:
        filtered_games.sort(key=lambda x: x.total_reviews, reverse=True)
    else:
        filtered_games.sort(key=lambda x: x.recommended_count, reverse=True)

    # Hàng chỉ số tóm tắt kết quả lọc
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        render_hud_card(
            st,
            label="Game Thỏa Mãn Ngưỡng",
            value=f"{len(filtered_games)} / {len(all_games)}",
            subtext=f"Ngưỡng lọc >= {threshold:,} reviews",
            badge="FILTERED",
            accent="cyan",
        )
    with col_kpi2:
        top_rate = f"{filtered_games[0].recommendation_rate * 100:.1f}%" if filtered_games else "N/A"
        top_name = filtered_games[0].app_name if filtered_games else "N/A"
        render_hud_card(
            st,
            label="Game Dẫn Đầu Hài Lòng",
            value=top_rate,
            subtext=top_name[:28] if len(top_name) > 28 else top_name,
            badge="TOP RATED",
            accent="green",
        )
    with col_kpi3:
        avg_filtered_rate = (
            sum(g.recommendation_rate for g in filtered_games) / len(filtered_games) * 100
            if filtered_games
            else 0.0
        )
        render_hud_card(
            st,
            label="Tỷ Lệ Hài Lòng TB Nhóm Lọc",
            value=f"{avg_filtered_rate:.1f}%",
            subtext="Mức chuẩn đối chiếu phân khúc",
            badge="BENCHMARK",
            accent="amber",
        )

    if not filtered_games:
        st.warning(
            f"Không có trò chơi nào thỏa mãn điều kiện (Ngưỡng >= {threshold:,} reviews"
            + (f" và từ khóa '{search_query}'" if search_query else "")
            + "). Vui lòng điều chỉnh lại bộ lọc!"
        )
        return

    st.markdown("---")

    # BIỂU ĐỒ 1: MA TRẬN PHÂN TÁN (Bubble Plot)
    st.subheader(rf"1. Ma trận Định vị Hài lòng vs Quy mô Cộng đồng (Ngưỡng $\ge$ {threshold:,} reviews)")
    st.caption("Trục tung: Tỷ lệ Khuyến nghị (%) | Trục hoành: Quy mô đánh giá (Log scale nếu dữ liệu lớn) | Kích thước bóng: Số lượng review.")
    fig_bubble = create_game_bubble_scatter(filtered_games, threshold)
    st.plotly_chart(fig_bubble, use_container_width=True)

    # BIỂU ĐỒ 2: TOP GAMES XẾP HẠNG
    col_chart1, col_chart2 = st.columns([1.2, 1])
    with col_chart1:
        fig_top = create_top_games_bar(filtered_games, top_n=8)
        st.plotly_chart(fig_top, use_container_width=True)
    with col_chart2:
        st.markdown("#### Tiêu chuẩn Xếp hạng Nghiên cứu")
        st.markdown(
            "- **Ngưỡng lọc:** Giúp loại bỏ hiện tượng các game chỉ có 1-2 review nhưng đạt 100% tỷ lệ khuyến nghị.\n"
            "- **Tính đại diện:** Các tựa game đạt trên 100 reviews phản ánh đúng trải nghiệm của cộng đồng người chơi.\n"
            "- **Độ tin cậy:** Với mẫu số đủ lớn, tỷ lệ khuyến nghị hội tụ về giá trị kỳ vọng thực tế của sản phẩm."
        )

    # BẢNG XẾP HẠNG CHI TIẾT
    with st.expander(f"Bảng Xếp Hạng Chi Tiết ({len(filtered_games)} trò chơi)", expanded=False):
        table_data = [
            {
                "Thứ hạng": idx + 1,
                "App ID": g.app_id,
                "Tên trò chơi": g.app_name,
                "Tổng số review": f"{g.total_reviews:,}",
                "Số lượt Khuyến nghị": f"{g.recommended_count:,}",
                "Tỷ lệ Khuyến nghị": f"{g.recommendation_rate * 100:.2f}%",
            }
            for idx, g in enumerate(filtered_games)
        ]
        st.dataframe(table_data, use_container_width=True)

    # KHỐI 3: XU HƯỚNG THEO THỜI GIAN (Monthly Trend)
    st.markdown("---")
    st.subheader("2. Xu hướng Đánh giá & Độ Hài lòng theo Thời gian (Monthly Evolution)")
    st.caption("*Dữ liệu thời gian tổng hợp theo từng tháng (UTC) cho các bản ghi có nhãn thời gian hợp lệ.*")

    fig_month = create_monthly_trend_chart(snapshot.monthly_summary)
    st.plotly_chart(fig_month, use_container_width=True)

    with st.expander("Xem Bảng dữ liệu chuỗi thời gian chi tiết"):
        monthly_data = [
            {
                "Tháng (UTC)": m.year_month,
                "Tổng số Review": f"{m.total_reviews:,}",
                "Lượt Recommend": f"{m.recommended_count:,}",
                "Tỷ lệ Khuyến nghị (%)": f"{m.recommendation_rate * 100:.2f}%",
            }
            for m in snapshot.monthly_summary
        ]
        st.dataframe(monthly_data, use_container_width=True)
