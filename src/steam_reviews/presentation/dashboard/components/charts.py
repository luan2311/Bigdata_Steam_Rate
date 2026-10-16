"""
Tập hợp các hàm khởi tạo biểu đồ Plotly phục vụ trực quan hóa dữ liệu thống kê trên Dashboard.
Tuân thủ Clean Architecture: chỉ nhận các DTO từ application.dto, không import pyspark/infrastructure.
"""
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from steam_reviews.presentation.dashboard.components.theme import (
    apply_plotly_theme,
    COLOR_CYAN,
    COLOR_AMBER,
    COLOR_CORAL,
    COLOR_GREEN,
    COLOR_VIOLET,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_BORDER,
    COLOR_BG_CARD,
)
from steam_reviews.application.dto.dashboard_dto import (
    LanguageDistributionItemDTO,
    GameAnalyticsItemDTO,
    MonthlyTrendItemDTO,
    PlaytimeBinItemDTO,
    DataQualitySummaryDTO,
)


# ==============================================================================
# 1. BIỂU ĐỒ TRANG 1: TỔNG QUAN THỊ TRƯỜNG
# ==============================================================================

def create_language_distribution_chart(
    languages: List[LanguageDistributionItemDTO],
) -> go.Figure:
    """Biểu đồ thanh ngang phân bố ngôn ngữ, tô màu theo tỷ lệ khuyến nghị."""
    if not languages:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Chưa có dữ liệu ngôn ngữ")

    # Sắp xếp theo số lượng review giảm dần
    sorted_langs = sorted(languages, key=lambda x: x.total_reviews, reverse=False)

    y_langs = [item.language for item in sorted_langs]
    x_counts = [item.total_reviews for item in sorted_langs]
    rec_rates = [item.recommendation_rate * 100 for item in sorted_langs]

    hover_texts = [
        f"<b>Ngôn ngữ:</b> {item.language}<br>"
        f"<b>Tổng đánh giá:</b> {item.total_reviews:,}<br>"
        f"<b>Tỷ lệ Khuyến nghị:</b> {item.recommendation_rate * 100:.2f}%"
        for item in sorted_langs
    ]

    fig = go.Figure(
        go.Bar(
            x=x_counts,
            y=y_langs,
            orientation="h",
            marker=dict(
                color=rec_rates,
                colorscale=[[0.0, COLOR_CORAL], [0.5, COLOR_AMBER], [1.0, COLOR_CYAN]],
                cmin=min(rec_rates) if rec_rates else 50,
                cmax=max(rec_rates) if rec_rates else 100,
                colorbar=dict(
                    title=dict(text="Tỷ lệ Tích cực (%)", side="top"),
                    tickfont=dict(size=9, color=COLOR_TEXT_MUTED),
                    thickness=12,
                    len=0.7,
                ),
                line=dict(color=COLOR_BORDER, width=1),
            ),
            hovertext=hover_texts,
            hoverinfo="text",
            text=[f"{rate:.1f}% rec" for rate in rec_rates],
            textposition="auto",
            textfont=dict(color="#0B0E14", size=10, family="monospace"),
        )
    )

    fig.update_layout(
        xaxis_title="Số lượng Đánh giá (Reviews)",
        yaxis_title="Ngôn ngữ",
    )
    return apply_plotly_theme(fig, height=360, title="Phân bố Đánh giá & Tỷ lệ Hài lòng theo Ngôn ngữ")


def create_language_donut_chart(
    languages: List[LanguageDistributionItemDTO],
) -> go.Figure:
    """Biểu đồ Donut thể hiện thị phần top ngôn ngữ."""
    if not languages:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Chưa có dữ liệu")

    # Giữ top 4 và gộp các ngôn ngữ còn lại vào 'others'
    sorted_langs = sorted(languages, key=lambda x: x.total_reviews, reverse=True)
    top_langs = sorted_langs[:4]
    other_count = sum(x.total_reviews for x in sorted_langs[4:])

    labels = [x.language for x in top_langs]
    values = [x.total_reviews for x in top_langs]
    if other_count > 0:
        labels.append("other_languages")
        values.append(other_count)

    colors = [COLOR_CYAN, COLOR_AMBER, COLOR_VIOLET, COLOR_GREEN, "#64748B"]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color=COLOR_BORDER, width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, family="monospace"),
            hoverinfo="label+value+percent",
        )
    )

    fig.update_layout(
        annotations=[
            dict(
                text="LANG<br>SHARE",
                x=0.5,
                y=0.5,
                font=dict(size=13, family="monospace", color=COLOR_TEXT_PRIMARY),
                showarrow=False,
            )
        ]
    )
    return apply_plotly_theme(fig, height=360, title="Thị phần Ngôn ngữ Chính", show_legend=False)


def create_market_sentiment_gauge(overall_rate: float) -> go.Figure:
    """Đồng hồ hiển thị mức độ lạc quan của thị trường Steam."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_rate,
            delta={"reference": 80.0, "increasing": {"color": COLOR_CYAN}},
            number={"suffix": "%", "font": {"family": "monospace", "size": 36, "color": COLOR_CYAN}},
            title={"text": "Tỷ lệ Đánh giá Tích cực Toàn Thị trường", "font": {"size": 13, "color": COLOR_TEXT_MUTED}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": COLOR_TEXT_MUTED, "tickwidth": 1},
                "bar": {"color": COLOR_CYAN, "thickness": 0.28},
                "bgcolor": COLOR_BG_CARD,
                "borderwidth": 1,
                "bordercolor": COLOR_BORDER,
                "steps": [
                    {"range": [0, 60], "color": "rgba(255, 82, 82, 0.25)"},
                    {"range": [60, 80], "color": "rgba(255, 179, 0, 0.25)"},
                    {"range": [80, 100], "color": "rgba(0, 229, 255, 0.2)"},
                ],
                "threshold": {
                    "line": {"color": COLOR_AMBER, "width": 3},
                    "thickness": 0.75,
                    "value": 85.0,
                },
            },
        )
    )
    return apply_plotly_theme(fig, height=240, show_legend=False)


# ==============================================================================
# 2. BIỂU ĐỒ TRANG 2: KHÁM PHÁ TRÒ CHƠI
# ==============================================================================

def create_game_bubble_scatter(
    games: List[GameAnalyticsItemDTO],
    threshold: int,
) -> go.Figure:
    """Biểu đồ phân tán (Scatter Matrix) đối chiếu Quy mô Đánh giá vs Tỷ lệ Hài lòng."""
    if not games:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Không có trò chơi thỏa mãn ngưỡng lọc")

    app_names = [g.app_name for g in games]
    reviews = [g.total_reviews for g in games]
    rates = [g.recommendation_rate * 100 for g in games]
    recs = [g.recommended_count for g in games]

    # Tính bán kính bubble tỉ lệ tương đối
    max_rev = max(reviews) if reviews else 1
    bubble_sizes = [max(12, min(50, int((r / max_rev) * 45) + 12)) for r in reviews]

    hover_texts = [
        f"<b>{g.app_name}</b> (ID: {g.app_id})<br>"
        f"• Tổng đánh giá: {g.total_reviews:,}<br>"
        f"• Lượt Khuyến nghị: {g.recommended_count:,}<br>"
        f"• Tỷ lệ Khuyến nghị: {g.recommendation_rate * 100:.2f}%"
        for g in games
    ]

    avg_rate = sum(rates) / len(rates) if rates else 80.0

    fig = go.Figure()

    # Đường chuẩn trung bình
    fig.add_hline(
        y=avg_rate,
        line_dash="dot",
        line_color=COLOR_AMBER,
        annotation_text=f"Benchmark TB: {avg_rate:.1f}%",
        annotation_position="bottom right",
        annotation_font=dict(color=COLOR_AMBER, size=10, family="monospace"),
    )

    fig.add_trace(
        go.Scatter(
            x=reviews,
            y=rates,
            mode="markers+text",
            marker=dict(
                size=bubble_sizes,
                color=rates,
                colorscale=[[0.0, COLOR_CORAL], [0.5, COLOR_AMBER], [1.0, COLOR_CYAN]],
                showscale=True,
                colorbar=dict(
                    title=dict(text="Tỷ lệ Rec (%)", side="top"),
                    thickness=10,
                    tickfont=dict(size=9, color=COLOR_TEXT_MUTED),
                ),
                line=dict(color=COLOR_BORDER, width=1.5),
                opacity=0.88,
            ),
            text=[name if len(name) <= 18 else name[:16] + ".." for name in app_names],
            textposition="top center",
            textfont=dict(family="monospace", size=9, color=COLOR_TEXT_MUTED),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )

    fig.update_layout(
        xaxis_title="Tổng số lượng Đánh giá (Quy mô người chơi)",
        yaxis_title="Tỷ lệ Khuyến nghị (%)",
        xaxis_type="log" if max_rev > 50000 else "linear",
    )
    return apply_plotly_theme(
        fig,
        height=450,
        title=f"Bản đồ Ma trận Hài lòng vs Quy mô (Ngưỡng lọc >= {threshold:,} reviews)",
        show_legend=False,
    )


def create_top_games_bar(
    games: List[GameAnalyticsItemDTO],
    top_n: int = 8,
) -> go.Figure:
    """Biểu đồ xếp hạng Top N Games theo tỷ lệ hài lòng cao nhất."""
    if not games:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Chưa có dữ liệu")

    # Lấy top N đã sắp xếp theo tỷ lệ
    top_subset = sorted(games, key=lambda x: (x.recommendation_rate, x.total_reviews), reverse=True)[:top_n]
    top_subset.reverse()  # Đảo chiều để thanh cao nhất nằm trên cùng

    names = [g.app_name if len(g.app_name) <= 24 else g.app_name[:22] + ".." for g in top_subset]
    rates = [g.recommendation_rate * 100 for g in top_subset]
    revs = [f"{g.total_reviews:,} revs" for g in top_subset]

    fig = go.Figure(
        go.Bar(
            y=names,
            x=rates,
            orientation="h",
            marker=dict(
                color=rates,
                colorscale=[[0.0, COLOR_AMBER], [1.0, COLOR_CYAN]],
                line=dict(color=COLOR_BORDER, width=1),
            ),
            text=[f"{r:.1f}% ({v})" for r, v in zip(rates, revs)],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(family="monospace", size=10, color="#0B0E14"),
            hoverinfo="x+y",
        )
    )

    fig.update_layout(
        xaxis_title="Tỷ lệ Khuyến nghị (%)",
        yaxis_title="Tên Trò chơi",
        xaxis_range=[min(60, min(rates) - 5) if rates else 0, 102],
    )
    return apply_plotly_theme(fig, height=360, title=f"Top {len(top_subset)} Trò chơi được Đánh giá Cao nhất", show_legend=False)


def create_monthly_trend_chart(
    monthly_data: List[MonthlyTrendItemDTO],
) -> go.Figure:
    """Biểu đồ trục kép: Số lượng đánh giá theo tháng & Đường xu hướng tỷ lệ tích cực."""
    if not monthly_data:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Chưa có dữ liệu xu hướng thời gian")

    sorted_months = sorted(monthly_data, key=lambda x: x.year_month)
    dates = [m.year_month for m in sorted_months]
    reviews = [m.total_reviews for m in sorted_months]
    rates = [m.recommendation_rate * 100 for m in sorted_months]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Cột khối lượng đánh giá (Primary Y)
    fig.add_trace(
        go.Bar(
            x=dates,
            y=reviews,
            name="Tổng số Review",
            marker=dict(color="rgba(0, 229, 255, 0.35)", line=dict(color=COLOR_CYAN, width=1.5)),
            hoverinfo="x+y",
        ),
        secondary_y=False,
    )

    # Đường tỷ lệ hài lòng (Secondary Y)
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=rates,
            name="Tỷ lệ Khuyến nghị (%)",
            mode="lines+markers",
            line=dict(color=COLOR_AMBER, width=3),
            marker=dict(size=7, color=COLOR_AMBER, symbol="diamond"),
            hoverinfo="x+y",
        ),
        secondary_y=True,
    )

    fig.update_xaxes(title_text="Tháng (UTC)", gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Khối lượng Đánh giá", secondary_y=False, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Tỷ lệ Khuyến nghị (%)", secondary_y=True, range=[50, 100], showgrid=False)

    return apply_plotly_theme(fig, height=380, title="Xu hướng Đánh giá & Độ Hài lòng qua các Tháng")


# ==============================================================================
# 3. BIỂU ĐỒ TRANG 3: GIỜ CHƠI & CHẤT LƯỢNG DỮ LIỆU
# ==============================================================================

def create_quality_funnel_chart(q: DataQualitySummaryDTO) -> go.Figure:
    """Biểu đồ phễu lọc chất lượng dữ liệu tiền xử lý (Pipeline Ingestion Funnel)."""
    stages = [
        "1. Nạp Thô (Raw Ingestion)",
        "2. Khử Trùng lặp (Deduplicated)",
        "3. Lọc Cách ly (Quarantine Filtered)",
        "4. Dữ liệu Hợp lệ (Silver Cleaned)",
    ]

    post_dedup = q.raw_records - q.duplicate_records
    post_quarantine = post_dedup - q.quarantine_records
    values = [q.raw_records, post_dedup, post_quarantine, q.valid_records]

    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            texttemplate="%{value:,.0f} bản ghi<br>(%{percentInitial:.1%})",
            textfont=dict(family="monospace", size=11, color=COLOR_TEXT_PRIMARY),
            marker=dict(
                color=[COLOR_CYAN, COLOR_AMBER, COLOR_VIOLET, COLOR_GREEN],
                line=dict(color=COLOR_BORDER, width=1.5),
            ),
            connector=dict(line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot")),
        )
    )

    return apply_plotly_theme(fig, height=350, title="Phễu Làm sạch Dữ liệu Lớn (Data Pipeline Audit)", show_legend=False)


def create_quarantine_pie(quarantine_by_reason: Dict[str, int]) -> go.Figure:
    """Biểu đồ Donut phân tích các nguyên nhân bản ghi bị cách ly (Quarantine)."""
    if not quarantine_by_reason:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Không có bản ghi cách ly")

    labels = list(quarantine_by_reason.keys())
    values = list(quarantine_by_reason.values())

    colors = [COLOR_CORAL, COLOR_AMBER, COLOR_VIOLET, "#64748B"]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color=COLOR_BORDER, width=1.5)),
            textinfo="label+value",
            textfont=dict(size=10, family="monospace"),
            hoverinfo="label+value+percent",
        )
    )

    fig.update_layout(
        annotations=[
            dict(
                text="QUARANTINE<br>REASONS",
                x=0.5,
                y=0.5,
                font=dict(size=11, family="monospace", color=COLOR_TEXT_PRIMARY),
                showarrow=False,
            )
        ]
    )
    return apply_plotly_theme(fig, height=350, title="Cơ cấu Lỗi Dữ liệu Cách ly", show_legend=False)


def create_playtime_impact_chart(
    playtime_summary: List[PlaytimeBinItemDTO],
) -> go.Figure:
    """Biểu đồ kết hợp: Phân bố số lượng review và Tỷ lệ Khuyến nghị theo khoảng giờ chơi."""
    if not playtime_summary:
        fig = go.Figure()
        return apply_plotly_theme(fig, title="Chưa có dữ liệu thời gian chơi")

    bins = [item.bin_label for item in playtime_summary]
    reviews = [item.total_reviews for item in playtime_summary]
    rates = [item.recommendation_rate * 100 for item in playtime_summary]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Cột số lượng review
    fig.add_trace(
        go.Bar(
            x=bins,
            y=reviews,
            name="Số lượng Đánh giá",
            marker=dict(color="rgba(124, 77, 255, 0.45)", line=dict(color=COLOR_VIOLET, width=1.5)),
            hoverinfo="x+y",
        ),
        secondary_y=False,
    )

    # Đường cong tỷ lệ khuyến nghị
    fig.add_trace(
        go.Scatter(
            x=bins,
            y=rates,
            name="Tỷ lệ Khuyến nghị (%)",
            mode="lines+markers+text",
            line=dict(color=COLOR_CYAN, width=3),
            marker=dict(size=8, color=COLOR_CYAN, symbol="circle"),
            text=[f"{r:.1f}%" for r in rates],
            textposition="top center",
            textfont=dict(family="monospace", size=10, color=COLOR_CYAN),
            hoverinfo="x+y",
        ),
        secondary_y=True,
    )

    # Chú thích mốc hoàn tiền 2 giờ của Steam
    if len(bins) > 0:
        fig.add_annotation(
            x=bins[0],
            y=rates[0],
            text="Mốc hoàn tiền Steam (<2h):<br>Tỷ lệ hài lòng thấp nhất",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor=COLOR_CORAL,
            ax=40,
            ay=-50,
            font=dict(family="monospace", size=10, color=COLOR_CORAL),
            bgcolor="rgba(18, 23, 34, 0.9)",
            bordercolor=COLOR_CORAL,
            borderwidth=1,
            secondary_y=True,
        )

    fig.update_xaxes(title_text="Khoảng thời gian chơi (playtime_forever)", gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Tổng số Đánh giá", secondary_y=False, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Tỷ lệ Khuyến nghị (%)", secondary_y=True, range=[50, 105], showgrid=False)

    return apply_plotly_theme(fig, height=420, title="Tương quan giữa Thời lượng Chơi và Đánh giá Tích cực")


# ==============================================================================
# 4. BIỂU ĐỒ TRANG 4: ĐÁNH GIÁ MÔ HÌNH ML
# ==============================================================================

def create_model_comparison_bar(
    baseline_metrics: Dict[str, float],
    model_metrics: Dict[str, float],
) -> go.Figure:
    """Biểu đồ cột so sánh Baseline (Majority Class) vs Spark MLlib Logistic Regression."""
    metrics_list = ["Macro-F1", "Precision (Lớp 1)", "Recall (Lớp 1)", "PR-AUC"]
    
    base_vals = [
        baseline_metrics.get("macro_f1", 0.0),
        baseline_metrics.get("accuracy", 0.0),  # Baseline majority precision = accuracy
        1.0,  # Baseline majority recall is 100%
        baseline_metrics.get("accuracy", 0.0),
    ]

    model_vals = [
        model_metrics.get("macro_f1", 0.0),
        model_metrics.get("precision_class_1", 0.0),
        model_metrics.get("recall_class_1", 0.0),
        model_metrics.get("pr_auc", 0.0),
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Baseline (Lớp Đa số)",
            x=metrics_list,
            y=base_vals,
            marker=dict(color="#475569", line=dict(color=COLOR_BORDER, width=1)),
            text=[f"{v:.3f}" for v in base_vals],
            textposition="auto",
            textfont=dict(family="monospace", size=10, color=COLOR_TEXT_PRIMARY),
        )
    )

    fig.add_trace(
        go.Bar(
            name="Logistic Regression + TF-IDF",
            x=metrics_list,
            y=model_vals,
            marker=dict(color=COLOR_VIOLET, line=dict(color=COLOR_CYAN, width=1.5)),
            text=[f"{v:.3f}" for v in model_vals],
            textposition="auto",
            textfont=dict(family="monospace", size=10, color=COLOR_TEXT_PRIMARY),
        )
    )

    fig.update_layout(
        barmode="group",
        yaxis_title="Điểm số Chỉ số (0.0 - 1.0)",
        yaxis_range=[0.0, 1.15],
    )
    return apply_plotly_theme(fig, height=380, title="So sánh Hiệu năng: Baseline vs Mô hình Đề xuất trên Tập Test")


def create_confusion_matrix_heatmap(confusion_matrix: Dict[str, int]) -> go.Figure:
    """Ma trận nhầm lẫn dạng Heatmap tương tác trực quan."""
    tn = confusion_matrix.get("true_negatives", 0)
    fp = confusion_matrix.get("false_positives", 0)
    fn = confusion_matrix.get("false_negatives", 0)
    tp = confusion_matrix.get("true_positives", 0)
    total = tn + fp + fn + tp if (tn + fp + fn + tp) > 0 else 1

    z_vals = [[tn, fp], [fn, tp]]
    x_labels = ["Dự đoán: 0 (Negative)", "Dự đoán: 1 (Positive)"]
    y_labels = ["Thực tế: 0 (Không khuyên)", "Thực tế: 1 (Khuyên dùng)"]

    annotations_text = [
        [f"<b>TN = {tn:,}</b><br>({tn/total:.1%})", f"<b>FP = {fp:,}</b><br>({fp/total:.1%})"],
        [f"<b>FN = {fn:,}</b><br>({fn/total:.1%})", f"<b>TP = {tp:,}</b><br>({tp/total:.1%})"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_vals,
            x=x_labels,
            y=y_labels,
            colorscale=[[0.0, "#131b2a"], [0.5, "rgba(0, 229, 255, 0.5)"], [1.0, COLOR_CYAN]],
            showscale=False,
            hoverongaps=False,
        )
    )

    for i in range(2):
        for j in range(2):
            fig.add_annotation(
                x=x_labels[j],
                y=y_labels[i],
                text=annotations_text[i][j],
                showarrow=False,
                font=dict(family="monospace", size=13, color="#0B0E14" if z_vals[i][j] > total * 0.4 else COLOR_TEXT_PRIMARY),
            )

    fig.update_layout(
        xaxis=dict(side="bottom", tickfont=dict(size=11, family="monospace")),
        yaxis=dict(tickfont=dict(size=11, family="monospace"), autorange="reversed"),
    )
    return apply_plotly_theme(fig, height=360, title="Confusion Matrix trên Tập Test Độc lập", show_legend=False)


def create_split_manifest_donut(split_manifest: Dict[str, int]) -> go.Figure:
    """Biểu đồ phân chia tập dữ liệu Train / Validation / Test."""
    labels = ["Train (70%)", "Validation (15%)", "Test (15%)"]
    values = [
        split_manifest.get("train_count", 7000),
        split_manifest.get("val_count", 1500),
        split_manifest.get("test_count", 1500),
    ]
    colors = [COLOR_CYAN, COLOR_AMBER, COLOR_GREEN]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color=COLOR_BORDER, width=2)),
            textinfo="label+value",
            texttemplate="%{label}<br>%{value:,} mẫu",
            textfont=dict(size=10, family="monospace"),
            hoverinfo="label+value+percent",
        )
    )

    fig.update_layout(
        annotations=[
            dict(
                text="DATA<br>SPLIT",
                x=0.5,
                y=0.5,
                font=dict(size=12, family="monospace", color=COLOR_TEXT_PRIMARY),
                showarrow=False,
            )
        ]
    )
    return apply_plotly_theme(fig, height=340, title="Phân chia Tập Dữ liệu (Hash-based Anti-leakage)", show_legend=False)
