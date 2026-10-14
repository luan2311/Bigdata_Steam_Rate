import sys
import unittest
from pathlib import Path

# Thêm src vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from steam_reviews.bootstrap.dashboard_container import create_dashboard_use_case
from steam_reviews.application.dto.dashboard_dto import DashboardSnapshotDTO


class TestDashboardUseCase(unittest.TestCase):
    def test_load_fixture_snapshot_successfully(self):
        use_case = create_dashboard_use_case()
        snapshot: DashboardSnapshotDTO = use_case.execute()

        # Kiểm tra metadata
        self.assertIsNotNone(snapshot.metadata)
        self.assertTrue(snapshot.metadata.is_fixture)
        self.assertEqual(snapshot.metadata.total_valid_reviews, 10000)

        # Kiểm tra quality summary
        self.assertEqual(snapshot.quality_summary.raw_records, 10500)
        self.assertEqual(snapshot.quality_summary.duplicate_records, 350)

        # Kiểm tra game summary
        self.assertGreater(len(snapshot.game_summary), 0)
        first_game = snapshot.game_summary[0]
        self.assertEqual(first_game.app_id, "730")
        self.assertGreater(first_game.total_reviews, 0)
        self.assertTrue(0.0 <= first_game.recommendation_rate <= 1.0)

        # Kiểm tra monthly summary
        self.assertGreater(len(snapshot.monthly_summary), 0)

        # Kiểm tra model metrics
        self.assertIn("macro_f1", snapshot.model_metrics.baseline_metrics)
        self.assertIn("macro_f1", snapshot.model_metrics.model_metrics)
        self.assertGreater(
            snapshot.model_metrics.model_metrics["macro_f1"],
            snapshot.model_metrics.baseline_metrics["macro_f1"],
        )


if __name__ == "__main__":
    unittest.main()
