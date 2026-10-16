"""
Module hiển thị Trang 3: Thời gian chơi và Chất lượng dữ liệu.
Trực quan hóa phễu làm sạch, cơ cấu lỗi cách ly và phân tích các khoảng giờ chơi [0, 2), [2, 10),...
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO
from steam_reviews.presentation.dashboard.components.theme import render_hud_card
from steam_reviews.presentation.dashboard.components.charts import (
    create_quality_funnel_chart,
    create_quarantine_pie,
    create_playtime_impact_chart,
)


def render_playtime_quality_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    st.header("Thời gian Chơi & Đối soát Chất lượng Dữ liệu (Data Quality & Telemetry)")

    q = snapshot.quality_summary

    # HÀNG KPI ĐỐI SOÁT CHẤT LƯỢNG TIỀN XỬ LÝ
    st.subheader("1. Đối soát Chất lượng Tiền xử lý Dữ liệu (Data Pipeline Audit)")
    st.markdown(
        "Báo cáo đối soát độc lập các công đoạn lọc rửa dữ liệu từ Bronze (HDFS Raw) "
        "sang Silver (Parquet sạch). Đảm bảo tính toàn vẹn và chống suy diễn sai lệch."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_hud_card(
            st,
            label="Bản Ghi Nạp Thô",
            value=f"{q.raw_records:,}",
            subtext="Tập dữ liệu gốc từ HDFS Bronze",
            badge="BRONZE RAW",
            accent="cyan",
        )
    with col2:
        dup_pct = (q.duplicate_records / q.raw_records * 100) if q.raw_records > 0 else 0.0
        render_hud_card(
            st,
            label="Bản Ghi Trùng Lặp",
            value=f"{q.duplicate_records:,}",
            subtext=f"Tỷ lệ trùng: {dup_pct:.2f}%",
            badge="DEDUP DROPPED",
            accent="amber",
        )
    with col3:
        quar_pct = (q.quarantine_records / q.raw_records * 100) if q.raw_records > 0 else 0.0
        render_hud_card(
            st,
            label="Bản Ghi Cách Ly",
            value=f"{q.quarantine_records:,}",
            subtext=f"Tỷ lệ lỗi: {quar_pct:.3f}%",
            badge="QUARANTINE",
            accent="coral",
        )
    with col4:
        retention_pct = (q.valid_records / q.raw_records * 100) if q.raw_records > 0 else 0.0
        render_hud_card(
            st,
            label="Bản Ghi Hợp Lệ (Silver)",
            value=f"{q.valid_records:,}",
            subtext=f"Tỷ lệ giữ lại: {retention_pct:.2f}%",
            badge="SILVER READY",
            accent="green",
        )

    # KHỐI BIỂU ĐỒ CHẤT LƯỢNG: Phễu làm sạch & Cơ cấu cách ly
    col_funnel, col_quar = st.columns([1.3, 1])
    with col_funnel:
        fig_funnel = create_quality_funnel_chart(q)
        st.plotly_chart(fig_funnel, use_container_width=True)
    with col_quar:
        if q.quarantine_by_reason:
            fig_pie = create_quarantine_pie(q.quarantine_by_reason)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Không ghi nhận lỗi cách ly nào trong đợt nạp này.")

    if q.quarantine_by_reason:
        with st.expander("Chi tiết phân loại nguyên nhân cách ly (Quarantine Breakdown)"):
            reason_data = [
                {
                    "Nguyên nhân cách ly": k,
                    "Số bản ghi vi phạm": f"{v:,}",
                    "Tỷ lệ trên tổng lỗi": f"{(v / q.quarantine_records * 100):.1f}%" if q.quarantine_records > 0 else "0.0%",
                }
                for k, v in q.quarantine_by_reason.items()
            ]
            st.dataframe(reason_data, use_container_width=True)

    # KHỐI 2: TƯƠNG QUAN GIỜ CHƠI VÀ MỨC ĐỘ HÀI LÒNG
    st.markdown("---")
    st.subheader("2. Mối liên hệ giữa Giờ chơi (`playtime_forever`) và Tỷ lệ Khuyến nghị")
    st.caption(
        "*Ghi chú phương pháp: Đây là phân tích tương quan quan sát trên tập dữ liệu, "
        "không đưa ra kết luận quan hệ nhân quả. Các khoảng giờ chơi không chồng chéo nhau.*"
    )

    fig_playtime = create_playtime_impact_chart(snapshot.playtime_summary)
    st.plotly_chart(fig_playtime, use_container_width=True)

    col_insight1, col_insight2 = st.columns(2)
    with col_insight1:
        st.markdown(
            "> **Hiện tượng Cửa sổ Hoàn tiền (< 2 giờ):**\n"
            "> Theo chính sách của Valve Steam, người chơi được phép hoàn tiền nếu chơi dưới 2 giờ. "
            "Dữ liệu cho thấy nhóm `[0, 2h)` có tỷ lệ khuyến nghị thấp nhất (~68%), phản ánh những người chơi "
            "gặp lỗi kĩ thuật, crash game hoặc không thích lối chơi và hoàn trả sản phẩm."
        )
    with col_insight2:
        st.markdown(
            "> **Lòng trung thành theo Thời lượng chơi (> 50 giờ):**\n"
            "> Người chơi tích lũy trên 50 giờ chơi và hơn 100 giờ thể hiện mức độ hài lòng vượt trội (>91% đến 94%). "
            "Thời lượng chơi là một trong những tín hiệu quan trọng nhất thể hiện giá trị gắn kết của trò chơi."
        )

    with st.expander("📋 Xem Bảng thống kê chi tiết theo từng Khoảng Giờ chơi"):
        playtime_data = [
            {
                "Khoảng thời gian chơi": item.bin_label,
                "Giờ tối thiểu (>=)": f"{item.min_hours:.1f}h",
                "Giờ tối đa (<)": f"{item.max_hours:.1f}h" if item.max_hours is not None else "+inf",
                "Số lượng đánh giá": f"{item.total_reviews:,}",
                "Tỷ lệ Khuyến nghị": f"{item.recommendation_rate * 100:.2f}%",
            }
            for item in snapshot.playtime_summary
        ]
        st.dataframe(playtime_data, use_container_width=True)
