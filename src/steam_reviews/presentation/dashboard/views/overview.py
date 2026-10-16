"""
Module hiển thị Trang 1: Tổng quan dữ liệu thị trường Steam.
Định hướng thẩm mỹ: Cyber-Industrial Telemetry (Plotly Charts, Telemetry HUD Cards).
Tuân thủ Clean Architecture: chỉ nhận DashboardSnapshotDTO, không import Spark/HDFS/infrastructure.
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO
from steam_reviews.presentation.dashboard.components.theme import render_hud_card
from steam_reviews.presentation.dashboard.components.charts import (
    create_language_distribution_chart,
    create_language_donut_chart,
    create_market_sentiment_gauge,
    create_top_games_bar,
)


def render_overview_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    meta = snapshot.metadata
    st.header("Tổng quan Toàn cảnh Thị trường Steam Reviews")
    st.caption(
        f"**Phiên bản dữ liệu:** `{meta.dataset_version}` | "
        f"**Run ID:** `{meta.run_id}` | "
        f"**Trích xuất:** `{meta.created_at}`"
    )

    if meta.is_fixture:
        st.info("**Chế độ Fixture:** Dashboard đang hiển thị tập dữ liệu mẫu offline (Smoke Test 10K bản ghi).")

    # Tính toán chỉ số tổng hợp
    total_recs = sum(g.recommended_count for g in snapshot.game_summary)
    total_revs = sum(g.total_reviews for g in snapshot.game_summary)
    overall_rate = (total_recs / total_revs * 100) if total_revs > 0 else 0.0

    # Hàng thẻ Telemetry HUD
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_hud_card(
            st,
            label="Tổng Đánh Giá Hợp Lệ",
            value=f"{meta.total_valid_reviews:,}",
            subtext="Đã qua khử trùng & cách ly",
            badge="SILVER CLEAN",
            accent="cyan",
        )
    with col2:
        render_hud_card(
            st,
            label="Số Lượng Trò Chơi",
            value=f"{meta.total_games:,}",
            subtext="App ID danh mục chuẩn Steam",
            badge="GOLD AGGREGATED",
            accent="amber",
        )
    with col3:
        render_hud_card(
            st,
            label="Tỷ Lệ Khuyến Nghị",
            value=f"{overall_rate:.1f}%",
            subtext=f"{total_recs:,} lượt thumbs up",
            badge="SENTIMENT POSITIVE",
            accent="green",
        )
    with col4:
        created_display = meta.created_at[:10] if meta.created_at else "N/A"
        render_hud_card(
            st,
            label="Phiên Bản Pipeline",
            value=meta.run_id,
            subtext=f"Ngày xử lý: {created_display}",
            badge=f"VER {meta.dataset_version}",
            accent="violet",
        )

    st.markdown("---")

    # KHỐI 1: PHÂN BỐ NGÔN NGỮ (Plotly Visualizations)
    st.subheader("1. Bản đồ Phân bố Ngôn ngữ Đánh giá (Language Share & Sentiment)")
    st.caption(
        "*Ghi chú phương pháp: Giữ nguyên nhóm `unknown` cho bản ghi khuyết ngôn ngữ; "
        "không suy đoán ngôn ngữ thành quốc tịch người chơi.*"
    )

    col_lang1, col_lang2 = st.columns([1.5, 1])
    with col_lang1:
        fig_lang = create_language_distribution_chart(snapshot.language_summary)
        st.plotly_chart(fig_lang, use_container_width=True)
    with col_lang2:
        fig_donut = create_language_donut_chart(snapshot.language_summary)
        st.plotly_chart(fig_donut, use_container_width=True)

    # KHỐI 2: ĐỘNG THÁI THỊ TRƯỜNG & TOP GAMES
    st.markdown("---")
    st.subheader("2. Tâm lý Thị trường & Điểm sáng Đánh giá (Market Pulse & Top Titles)")

    col_pulse1, col_pulse2 = st.columns([1, 1.4])
    with col_pulse1:
        fig_gauge = create_market_sentiment_gauge(overall_rate)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(
            "> **Đặc điểm phân bố:** Dữ liệu Steam có hiện tượng mất cân bằng tự nhiên "
            "(~80-87% đánh giá là tích cực), người dùng có xu hướng đánh giá khi yêu thích game."
        )
    with col_pulse2:
        fig_top_bar = create_top_games_bar(snapshot.game_summary, top_n=6)
        st.plotly_chart(fig_top_bar, use_container_width=True)

    # Bảng chi tiết ngôn ngữ
    with st.expander("Xem Bảng số liệu chi tiết phân bố Ngôn ngữ"):
        lang_data = [
            {
                "Mã ngôn ngữ": item.language,
                "Số lượng review": f"{item.total_reviews:,}",
                "Tỷ lệ Khuyến nghị": f"{item.recommendation_rate * 100:.2f}%",
                "Tỷ trọng ước tính": f"{(item.total_reviews / meta.total_valid_reviews * 100):.2f}%" if meta.total_valid_reviews > 0 else "0.00%",
            }
            for item in snapshot.language_summary
        ]
        st.dataframe(lang_data, use_container_width=True)
