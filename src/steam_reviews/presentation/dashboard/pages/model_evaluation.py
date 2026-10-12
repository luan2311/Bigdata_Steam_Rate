"""
Module hiển thị Trang 4: Đánh giá mô hình máy học (Spark MLlib).
Hiển thị so sánh Baseline vs Logistic Regression, confusion matrix và ví dụ phân tích lỗi.
"""
from typing import Any
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


def render_model_evaluation_page(st: Any, snapshot: DashboardSnapshotDTO) -> None:
    st.header("🤖 Hiệu năng Mô hình Máy học (Spark MLlib)")
    st.markdown(
        "**Bài toán:** Phân loại nhị phân đánh giá người chơi (`recommended` 1/0) dựa trên văn bản tiếng Anh (`review_text`).  \n"
        "**Quy trình phân chia:** Hash-based Split cố định seed: 70% Train / 15% Validation / 15% Test (Chống rò rỉ dữ liệu qua văn bản trùng)."
    )

    m = snapshot.model_metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Tập Train", f"{m.split_manifest.get('train_count', 0):,} mẫu")
    col2.metric("Tập Validation", f"{m.split_manifest.get('val_count', 0):,} mẫu")
    col3.metric("Tập Test độc lập", f"{m.split_manifest.get('test_count', 0):,} mẫu")

    st.markdown("---")
    st.subheader("1. So sánh Hiệu năng trên Tập Test Độc lập")

    base_f1 = m.baseline_metrics.get("macro_f1", 0.0)
    model_f1 = m.model_metrics.get("macro_f1", 0.0)
    improvement = model_f1 - base_f1

    comp_data = [
        {"Chỉ số đánh giá": "Macro-F1", "Baseline (Lớp đa số)": f"{base_f1:.3f}", "Logistic Regression + TF-IDF": f"{model_f1:.3f}", "Mức cải thiện": f"+{improvement:.3f}"},
        {"Chỉ số đánh giá": "Precision (Lớp 1)", "Baseline (Lớp đa số)": f"{m.baseline_metrics.get('accuracy', 0.0):.3f}", "Logistic Regression + TF-IDF": f"{m.model_metrics.get('precision_class_1', 0.0):.3f}", "Mức cải thiện": "-"},
        {"Chỉ số đánh giá": "Recall (Lớp 1)", "Baseline (Lớp đa số)": "1.000", "Logistic Regression + TF-IDF": f"{m.model_metrics.get('recall_class_1', 0.0):.3f}", "Mức cải thiện": "-"},
        {"Chỉ số đánh giá": "PR-AUC (Lớp dương 1)", "Baseline (Lớp đa số)": "-", "Logistic Regression + TF-IDF": f"{m.model_metrics.get('pr_auc', 0.0):.3f}", "Mức cải thiện": "-"},
    ]
    st.table(comp_data)

    st.markdown("---")
    st.subheader("2. Ma trận Nhầm lẫn trên Tập Test (Confusion Matrix)")
    cm = m.confusion_matrix
    cm_display = [
        {"Nhãn thực tế": "Thực tế: 0 (Không khuyên)", "Dự đoán: 0 (Negative)": f"TN = {cm.get('true_negatives', 0):,}", "Dự đoán: 1 (Positive)": f"FP = {cm.get('false_positives', 0):,}"},
        {"Nhãn thực tế": "Thực tế: 1 (Khuyên dùng)", "Dự đoán: 0 (Negative)": f"FN = {cm.get('false_negatives', 0):,}", "Dự đoán: 1 (Positive)": f"TP = {cm.get('true_positives', 0):,}"},
    ]
    st.table(cm_display)

    if m.sample_errors:
        st.markdown("---")
        st.subheader("3. Mẫu Phân tích Lỗi Dự đoán (Error Analysis)")
        st.markdown("*Lưu ý bảo mật: Không hiển thị ID cá nhân hoặc Steam ID của người đánh giá.*")
        err_list = [
            {
                "Nội dung đánh giá mẫu": e.get("review_text", ""),
                "Thực tế": e.get("actual_label"),
                "Mô hình đoán": e.get("predicted_label"),
                "Nguyên nhân dự kiến": e.get("error_type", ""),
            }
            for e in m.sample_errors
        ]
        st.table(err_list)
