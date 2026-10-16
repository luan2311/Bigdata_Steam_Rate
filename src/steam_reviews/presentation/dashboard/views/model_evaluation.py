"""
Module hiển thị Trang 4: Đánh giá mô hình máy học (Spark MLlib).
Hiển thị so sánh Baseline vs Logistic Regression, confusion matrix heatmap và phân tích lỗi.
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO
from steam_reviews.presentation.dashboard.components.theme import render_hud_card
from steam_reviews.presentation.dashboard.components.charts import (
    create_model_comparison_bar,
    create_confusion_matrix_heatmap,
    create_split_manifest_donut,
)


def render_model_evaluation_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    st.header("Hiệu năng Mô hình Phân loại Đánh giá (Spark MLlib)")
    st.markdown(
        "**Bài toán:** Phân loại nhị phân đánh giá người chơi (`recommended` 1/0) dựa trên văn bản tiếng Anh (`review_text`).  \n"
        "**Cơ chế chống rò rỉ:** Phân chia Train/Validation/Test theo MurmurHash văn bản nhằm triệt tiêu hoàn toàn rò rỉ dữ liệu qua các bài review trùng lặp."
    )

    m = snapshot.model_metrics
    split = m.split_manifest

    # HÀNG KPI TỔNG HỢP HIỆU NĂNG
    base_f1 = m.baseline_metrics.get("macro_f1", 0.0)
    model_f1 = m.model_metrics.get("macro_f1", 0.0)
    improvement = model_f1 - base_f1
    pr_auc = m.model_metrics.get("pr_auc", 0.0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_hud_card(
            st,
            label="Macro-F1 Score",
            value=f"{model_f1:.3f}",
            subtext=f"Baseline đa số: {base_f1:.3f}",
            badge=f"+{improvement:.3f} GAIN",
            accent="violet",
        )
    with col2:
        render_hud_card(
            st,
            label="PR-AUC (Lớp Dương)",
            value=f"{pr_auc:.3f}",
            subtext="Độ đo chuẩn cho dữ liệu mất cân bằng",
            badge="BENCHMARK",
            accent="cyan",
        )
    with col3:
        p1 = m.model_metrics.get("precision_class_1", 0.0)
        render_hud_card(
            st,
            label="Precision (Class 1)",
            value=f"{p1:.3f}",
            subtext="Độ chính xác khi dự đoán Thích",
            badge="ACCURACY",
            accent="green",
        )
    with col4:
        r1 = m.model_metrics.get("recall_class_1", 0.0)
        render_hud_card(
            st,
            label="Recall (Class 1)",
            value=f"{r1:.3f}",
            subtext="Tỷ lệ bao phủ đúng phản hồi tích cực",
            badge="COVERAGE",
            accent="amber",
        )

    st.markdown("---")

    # KHỐI 1: SO SÁNH HIỆU NĂNG MÔ HÌNH VÀ PHÂN CHIA TẬP DỮ LIỆU
    st.subheader("1. So sánh Hiệu năng trên Tập Test Độc lập & Cấu trúc Phân chia")

    col_chart_comp, col_chart_split = st.columns([1.5, 1])
    with col_chart_comp:
        fig_comp = create_model_comparison_bar(m.baseline_metrics, m.model_metrics)
        st.plotly_chart(fig_comp, use_container_width=True)
    with col_chart_split:
        fig_split = create_split_manifest_donut(split)
        st.plotly_chart(fig_split, use_container_width=True)

    # Bảng số liệu chi tiết
    with st.expander("Xem Bảng đối chiếu chi tiết các chỉ số đánh giá"):
        comp_data = [
            {
                "Chỉ số đánh giá": "Macro-F1",
                "Baseline (Lớp đa số)": f"{base_f1:.3f}",
                "Logistic Regression + TF-IDF": f"{model_f1:.3f}",
                "Mức cải thiện": f"+{improvement:.3f}",
                "Ý nghĩa": "Trung bình điều hòa F1 giữa 2 lớp; phản ánh mô hình không đoán mù.",
            },
            {
                "Chỉ số đánh giá": "Precision (Lớp 1)",
                "Baseline (Lớp đa số)": f"{m.baseline_metrics.get('accuracy', 0.0):.3f}",
                "Logistic Regression + TF-IDF": f"{m.model_metrics.get('precision_class_1', 0.0):.3f}",
                "Mức cải thiện": f"+{(m.model_metrics.get('precision_class_1', 0.0) - m.baseline_metrics.get('accuracy', 0.0)):.3f}",
                "Ý nghĩa": "Tỷ lệ dự đoán đúng trong số các bài gán nhãn tích cực.",
            },
            {
                "Chỉ số đánh giá": "Recall (Lớp 1)",
                "Baseline (Lớp đa số)": "1.000",
                "Logistic Regression + TF-IDF": f"{m.model_metrics.get('recall_class_1', 0.0):.3f}",
                "Mức cải thiện": "-",
                "Ý nghĩa": "Khả năng phát hiện các bài đánh giá tích cực trong thực tế.",
            },
            {
                "Chỉ số đánh giá": "PR-AUC (Lớp 1)",
                "Baseline (Lớp đa số)": "-",
                "Logistic Regression + TF-IDF": f"{m.model_metrics.get('pr_auc', 0.0):.3f}",
                "Mức cải thiện": "-",
                "Ý nghĩa": "Diện tích dưới đường Precision-Recall; tối quan trọng với phân bố lệch.",
            },
        ]
        st.dataframe(comp_data, use_container_width=True)

    # KHỐI 2: MA TRẬN NHẦM LẪN (CONFUSION MATRIX)
    st.markdown("---")
    st.subheader("2. Ma trận Nhầm lẫn trên Tập Test (Confusion Matrix Heatmap)")

    col_cm, col_cm_explain = st.columns([1.2, 1])
    with col_cm:
        fig_cm = create_confusion_matrix_heatmap(m.confusion_matrix)
        st.plotly_chart(fig_cm, use_container_width=True)
    with col_cm_explain:
        cm = m.confusion_matrix
        tn, fp, fn, tp = cm.get("true_negatives", 0), cm.get("false_positives", 0), cm.get("false_negatives", 0), cm.get("true_positives", 0)
        total_test = tn + fp + fn + tp if (tn + fp + fn + tp) > 0 else 1

        st.markdown("#### Phân tích Phân loại:")
        st.markdown(
            f"- **True Positives (TP):** `{tp:,}` mẫu ({tp/total_test:.1%}) — Dự đoán chính xác các bài khen ngợi.\n"
            f"- **True Negatives (TN):** `{tn:,}` mẫu ({tn/total_test:.1%}) — Phát hiện thành công phản hồi tiêu cực dù lớp thiểu số.\n"
            f"- **False Positives (FP):** `{fp:,}` mẫu ({fp/total_test:.1%}) — Báo động nhầm (nói tiêu cực nhưng đoán tích cực).\n"
            f"- **False Negatives (FN):** `{fn:,}` mẫu ({fn/total_test:.1%}) — Bỏ sót phản hồi tích cực."
        )

    # KHỐI 3: PHÂN TÍCH LỖI (ERROR ANALYSIS)
    if m.sample_errors:
        st.markdown("---")
        st.subheader("3. Mẫu Phân tích Lỗi Dự đoán (Qualitative Error Analysis)")
        st.markdown(
            "*Lưu ý bảo mật & đạo đức dữ liệu: Đã loại bỏ hoàn toàn `steamid` và thông tin định danh cá nhân.*"
        )

        for idx, e in enumerate(m.sample_errors):
            actual = e.get("actual_label")
            predicted = e.get("predicted_label")
            err_type = e.get("error_type", "")
            text = e.get("review_text", "")

            badge_color = "amber" if predicted == 1 else "coral"
            st.markdown(
                f"""
                <div class="hud-card accent-{badge_color}" style="margin-bottom: 10px;">
                    <div style="font-family: monospace; font-size: 0.8rem; color: #8B9BB4; margin-bottom: 4px;">
                        CASE #{idx + 1} | Thực tế: <b>{actual}</b> ➔ Mô hình dự đoán: <b>{predicted}</b> | <i>{err_type}</i>
                    </div>
                    <div style="font-style: italic; color: #F0F6FC; font-size: 0.95rem;">
                        "{text}"
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
