"""
Entry point chính của Streamlit Dashboard.
Chạy ứng dụng: streamlit run src/steam_reviews/presentation/dashboard/app.py
Tuân thủ Clean Architecture: chỉ sử dụng use case từ bootstrap, không import Spark/HDFS/infrastructure.
Định hướng thiết kế: Cyber-Industrial Telemetry (Plotly, HUD Cards, Dark Engine).
"""
import sys
from pathlib import Path
from typing import Dict

# Thêm đường dẫn src vào sys.path để import chuẩn package
SRC_PATH = Path(__file__).resolve().parents[3]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    import streamlit as st
except ImportError:
    st = None

from steam_reviews.bootstrap.dashboard_container import create_dashboard_use_case
from steam_reviews.presentation.dashboard.components.theme import inject_custom_css
from steam_reviews.presentation.dashboard.views.overview import render_overview_page
from steam_reviews.presentation.dashboard.views.game_exploration import render_game_exploration_page
from steam_reviews.presentation.dashboard.views.playtime_quality import render_playtime_quality_page
from steam_reviews.presentation.dashboard.views.model_evaluation import render_model_evaluation_page


def _discover_available_snapshots() -> Dict[str, Path]:
    """Tìm kiếm tự động các tệp snapshot khả dụng trong hệ thống."""
    snapshots: Dict[str, Path] = {}
    
    # 1. Snapshots thực thi trên cụm / lake
    snapshot_dir = PROJECT_ROOT / "artifacts" / "snapshots"
    if snapshot_dir.exists():
        for f in sorted(snapshot_dir.glob("*.json")):
            if "full-cluster" in f.name:
                snapshots["Full Cluster (21.6 Triệu Reviews - Run: full-cluster-01)"] = f
            elif "core-cluster" in f.name:
                snapshots["Core Cluster (10,000 Reviews - Run: core-cluster-01)"] = f
            elif "core-20261011" in f.name:
                snapshots["Core Lake Run (1.03 Triệu Reviews - Run: core-20261011-v1)"] = f
            else:
                snapshots[f"Snapshot: {f.stem}"] = f

    # 2. Fixture mẫu
    fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "dashboard_snapshot_fixture.json"
    if fixture_path.exists():
        snapshots["Fixture Kiểm thử Offline (10,000 Reviews - Smoke Test)"] = fixture_path

    return snapshots


def main() -> None:
    if st is None:
        print("Error: Streamlit chưa được cài đặt trong môi trường chạy.")
        return

    st.set_page_config(
        page_title="Steam Reviews Big Data Dashboard",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Tiêm CSS giao diện Cyber-Industrial Telemetry
    inject_custom_css(st)

    # Thanh điều hướng Sidebar
    st.sidebar.markdown(
        """
        <div style="font-family: monospace; font-size: 1.25rem; font-weight: 700; color: #00E5FF; margin-bottom: 2px;">
            STEAM TELEMETRY
        </div>
        <div style="font-family: monospace; font-size: 0.72rem; color: #8B9BB4; letter-spacing: 0.08em; margin-bottom: 15px;">
            BIG DATA ANALYTICS COCKPIT
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Chọn nguồn snapshot
    available_snapshots = _discover_available_snapshots()
    chosen_snapshot_path = None
    if available_snapshots:
        st.sidebar.markdown("**Nguồn Dữ Liệu Phân Tích:**")
        selected_label = st.sidebar.selectbox(
            "Chọn Snapshot:",
            options=list(available_snapshots.keys()),
            index=0,
            label_visibility="collapsed",
        )
        chosen_snapshot_path = available_snapshots[selected_label]

    # Khởi tạo use case và nạp dữ liệu snapshot
    use_case = create_dashboard_use_case(snapshot_path=chosen_snapshot_path)
    snapshot = use_case.execute()

    # Thông tin trạng thái luồng xử lý
    meta = snapshot.metadata
    status_color = "#00E676" if not meta.is_fixture else "#FFB300"
    status_label = "CLUSTER GOLD SYNCED" if not meta.is_fixture else "FIXTURE EMULATOR"

    st.sidebar.markdown(
        f"""
        <div style="background: rgba(18, 23, 34, 0.9); border: 1px solid #222D42; border-radius: 8px; padding: 10px 14px; margin: 12px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.7rem; font-family: monospace; color: #8B9BB4;">STATUS</span>
                <span style="font-size: 0.68rem; font-family: monospace; color: {status_color}; font-weight: bold;">● {status_label}</span>
            </div>
            <div style="font-family: monospace; font-size: 0.8rem; color: #F0F6FC;">
                Run: <b>{meta.run_id}</b>
            </div>
            <div style="font-family: monospace; font-size: 0.8rem; color: #00E5FF;">
                Reviews: <b>{meta.total_valid_reviews:,}</b>
            </div>
            <div style="font-family: monospace; font-size: 0.75rem; color: #8B9BB4;">
                Games: <b>{meta.total_games:,}</b> | Ver: <b>{meta.dataset_version}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pages = {
        "1. Tổng quan Thị trường": render_overview_page,
        "2. Khám phá Trò chơi": render_game_exploration_page,
        "3. Giờ chơi & Chất lượng dữ liệu": render_playtime_quality_page,
        "4. Hiệu năng Mô hình ML": render_model_evaluation_page,
    }

    selection = st.sidebar.radio("Điều hướng phân tích:", list(pages.keys()))

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.75rem; color: #8B9BB4; font-family: monospace;">
            <b>Nhóm thực hiện:</b> 8<br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render màn hình được chọn
    render_func = pages[selection]
    render_func(st, snapshot)


if __name__ == "__main__":
    main()
