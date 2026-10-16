"""
Unit tests kiểm thử độc lập cho các hàm tạo biểu đồ Plotly trên Dashboard.
Đảm bảo tất cả các hàm khởi tạo đúng figure, xử lý an toàn dữ liệu rỗng và không vi phạm Clean Architecture.
"""
import sys
import unittest
from pathlib import Path

# Thêm src vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from steam_reviews.bootstrap.dashboard_container import create_dashboard_use_case
from steam_reviews.presentation.dashboard.components.charts import (
    create_language_distribution_chart,
    create_language_donut_chart,
    create_market_sentiment_gauge,
    create_game_bubble_scatter,
    create_top_games_bar,
    create_monthly_trend_chart,
    create_quality_funnel_chart,
    create_quarantine_pie,
    create_playtime_impact_chart,
    create_model_comparison_bar,
    create_confusion_matrix_heatmap,
    create_split_manifest_donut,
)


class TestDashboardCharts(unittest.TestCase):
    def setUp(self):
        use_case = create_dashboard_use_case()
        self.snapshot = use_case.execute()

    def test_language_charts_render_valid_figures(self):
        fig_bar = create_language_distribution_chart(self.snapshot.language_summary)
        self.assertIsNotNone(fig_bar)
        self.assertGreater(len(fig_bar.data), 0)

        fig_donut = create_language_donut_chart(self.snapshot.language_summary)
        self.assertIsNotNone(fig_donut)
        self.assertGreater(len(fig_donut.data), 0)

        # Xử lý trường hợp rỗng an toàn
        empty_fig = create_language_distribution_chart([])
        self.assertIsNotNone(empty_fig)

    def test_market_sentiment_gauge_renders_valid_figure(self):
        fig_gauge = create_market_sentiment_gauge(86.5)
        self.assertIsNotNone(fig_gauge)
        self.assertEqual(len(fig_gauge.data), 1)

    def test_game_charts_render_valid_figures(self):
        fig_bubble = create_game_bubble_scatter(self.snapshot.game_summary, threshold=100)
        self.assertIsNotNone(fig_bubble)
        self.assertGreater(len(fig_bubble.data), 0)

        fig_top = create_top_games_bar(self.snapshot.game_summary, top_n=5)
        self.assertIsNotNone(fig_top)
        self.assertGreater(len(fig_top.data), 0)

        # Xử lý rỗng an toàn
        empty_bubble = create_game_bubble_scatter([], threshold=50000)
        self.assertIsNotNone(empty_bubble)

    def test_monthly_trend_chart_renders_valid_figure(self):
        fig_month = create_monthly_trend_chart(self.snapshot.monthly_summary)
        self.assertIsNotNone(fig_month)
        self.assertEqual(len(fig_month.data), 2)  # Bar + Line

        empty_month = create_monthly_trend_chart([])
        self.assertIsNotNone(empty_month)

    def test_quality_and_playtime_charts_render_valid_figures(self):
        fig_funnel = create_quality_funnel_chart(self.snapshot.quality_summary)
        self.assertIsNotNone(fig_funnel)
        self.assertEqual(len(fig_funnel.data), 1)

        fig_pie = create_quarantine_pie(self.snapshot.quality_summary.quarantine_by_reason)
        self.assertIsNotNone(fig_pie)
        self.assertEqual(len(fig_pie.data), 1)

        fig_playtime = create_playtime_impact_chart(self.snapshot.playtime_summary)
        self.assertIsNotNone(fig_playtime)
        self.assertEqual(len(fig_playtime.data), 2)  # Bar + Line

    def test_model_evaluation_charts_render_valid_figures(self):
        m = self.snapshot.model_metrics
        fig_comp = create_model_comparison_bar(m.baseline_metrics, m.model_metrics)
        self.assertIsNotNone(fig_comp)
        self.assertEqual(len(fig_comp.data), 2)  # Baseline trace + Model trace

        fig_cm = create_confusion_matrix_heatmap(m.confusion_matrix)
        self.assertIsNotNone(fig_cm)
        self.assertEqual(len(fig_cm.data), 1)  # Heatmap

        fig_split = create_split_manifest_donut(m.split_manifest)
        self.assertIsNotNone(fig_split)
        self.assertEqual(len(fig_split.data), 1)  # Donut


if __name__ == "__main__":
    unittest.main()
