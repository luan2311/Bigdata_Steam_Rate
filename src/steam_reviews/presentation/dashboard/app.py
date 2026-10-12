"""
Entry point chính của Streamlit Dashboard.
Chạy ứng dụng: streamlit run src/steam_reviews/presentation/dashboard/app.py
Tuân thủ Clean Architecture: chỉ sử dụng use case từ bootstrap, không import Spark/HDFS.
"""
import sys
from pathlib import Path

# Thêm đường dẫn src vào sys.path để import chuẩn package
SRC_PATH = Path(__file__).resolve().parents[3]
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    import streamlit as st
except ImportError:
    # Trường hợp chạy kiểm thử qua script hoặc chưa cài đặt Streamlit
    st = None

from steam_reviews.bootstrap.dashboard_container import create_dashboard_use_case
from steam_reviews.presentation.dashboard.pages.overview import render_overview_page
from steam_reviews.presentation.dashboard.pages.game_exploration import render_game_exploration_page
from steam_reviews.presentation.dashboard.pages.playtime_quality import render_playtime_quality_page
from steam_reviews.presentation.dashboard.pages.model_evaluation import render_model_evaluation_page


def main() -> None:
    st.set_page_layout = getattr(st, "set_page_config", lambda **kw: None)
    st.set_page_config(
        page_title="Steam Reviews Big Data Dashboard",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Khởi tạo use case và lấy snapshot dữ liệu thông qua Bootstrap container
    use_case = create_dashboard_use_case()
    snapshot = use_case.execute()

    # Thanh điều hướng Sidebar
    st.sidebar.title("🎮 Steam Analytics")
    st.sidebar.markdown(f"**Run ID:** `{snapshot.metadata.run_id}`")
    st.sidebar.markdown(f"**Bản ghi:** `{snapshot.metadata.total_valid_reviews:,}`")

    pages = {
        "1. Tổng quan Thị trường": render_overview_page,
        "2. Khám phá Trò chơi": render_game_exploration_page,
        "3. Giờ chơi & Chất lượng dữ liệu": render_playtime_quality_page,
        "4. Hiệu năng Mô hình ML": render_model_evaluation_page,
    }

    selection = st.sidebar.radio("Chọn màn hình phân tích:", list(pages.keys()))

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Nhóm thực hiện:** Big Data Team")
    st.sidebar.markdown("**Phụ trách UI/Hồ sơ:** TV3 (Trần Nhật Hào)")

    # Render màn hình được chọn
    render_func = pages[selection]
    render_func(st, snapshot)


if __name__ == "__main__":
    main()
