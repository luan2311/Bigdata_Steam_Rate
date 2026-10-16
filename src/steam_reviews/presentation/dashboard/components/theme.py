"""
Hệ thống thiết kế giao diện (Design System) & Theme Telemetry cho Steam Reviews Dashboard.
Định hướng thẩm mỹ: "Cyber-Industrial Telemetry / Steam Dark Engine".
Màu chủ đạo: Deep Charcoal (#0B0E14, #121722), Neon Cyan (#00E5FF), Electric Amber (#FFB300), Coral Red (#FF5252).
"""
from typing import Optional, Any
import plotly.graph_objects as go

# Design Tokens
COLOR_BG_ROOT = "#0B0E14"
COLOR_BG_CARD = "#121722"
COLOR_BG_SURFACE = "#182030"
COLOR_BORDER = "#222D42"
COLOR_CYAN = "#00E5FF"
COLOR_CYAN_MUTED = "rgba(0, 229, 255, 0.15)"
COLOR_AMBER = "#FFB300"
COLOR_CORAL = "#FF5252"
COLOR_GREEN = "#00E676"
COLOR_VIOLET = "#7C4DFF"
COLOR_TEXT_PRIMARY = "#F0F6FC"
COLOR_TEXT_MUTED = "#8B9BB4"
COLOR_GRID = "rgba(255, 255, 255, 0.06)"

FONT_CODE = "'JetBrains Mono', 'SF Mono', Consolas, monospace"
FONT_DISPLAY = "'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def inject_custom_css(st: Any) -> None:
    """Tiêm CSS định kiểu giao diện Cyber-Industrial Telemetry vào Streamlit."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Nền tổng thể và font chữ */
    .stApp {{
        background-color: {COLOR_BG_ROOT};
        color: {COLOR_TEXT_PRIMARY};
        font-family: {FONT_DISPLAY};
    }}

    /* Tiêu đề góc cạnh, nổi bật */
    h1, h2, h3, h4 {{
        font-family: {FONT_DISPLAY} !important;
        letter-spacing: -0.02em;
        font-weight: 700;
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* Card Telemetry HUD */
    .hud-card {{
        background: linear-gradient(135deg, {COLOR_BG_CARD} 0%, {COLOR_BG_SURFACE} 100%);
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}
    .hud-card:hover {{
        border-color: {COLOR_CYAN};
        transform: translateY(-2px);
    }}
    .hud-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: {COLOR_CYAN};
    }}
    .hud-card.accent-amber::before {{
        background: {COLOR_AMBER};
    }}
    .hud-card.accent-coral::before {{
        background: {COLOR_CORAL};
    }}
    .hud-card.accent-violet::before {{
        background: {COLOR_VIOLET};
    }}

    .hud-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {COLOR_TEXT_MUTED};
        font-family: {FONT_CODE};
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .hud-value {{
        font-size: 1.85rem;
        font-weight: 700;
        color: {COLOR_TEXT_PRIMARY};
        font-family: {FONT_CODE};
        line-height: 1.1;
    }}
    .hud-subtext {{
        font-size: 0.8rem;
        color: {COLOR_TEXT_MUTED};
        margin-top: 6px;
        display: flex;
        gap: 6px;
        align-items: center;
    }}
    .hud-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-family: {FONT_CODE};
        font-weight: 600;
        text-transform: uppercase;
    }}
    .hud-badge-cyan {{
        background: {COLOR_CYAN_MUTED};
        color: {COLOR_CYAN};
        border: 1px solid rgba(0, 229, 255, 0.3);
    }}
    .hud-badge-amber {{
        background: rgba(255, 179, 0, 0.15);
        color: {COLOR_AMBER};
        border: 1px solid rgba(255, 179, 0, 0.3);
    }}
    .hud-badge-green {{
        background: rgba(0, 230, 118, 0.15);
        color: {COLOR_GREEN};
        border: 1px solid rgba(0, 230, 118, 0.3);
    }}

    /* Sidebar Telemetry */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_BG_CARD};
        border-right: 1px solid {COLOR_BORDER};
    }}

    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLOR_BG_ROOT};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLOR_BORDER};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLOR_CYAN};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def apply_plotly_theme(
    fig: go.Figure,
    height: int = 380,
    title: Optional[str] = None,
    show_legend: bool = True,
) -> go.Figure:
    """
    Áp dụng đồng bộ bộ theme Cyber-Industrial Telemetry cho biểu đồ Plotly:
    - Nền trong suốt / tiệp màu card #121722
    - Lưới mờ xám slate
    - Typography JetBrains Mono / Space Grotesk
    - Tooltip nổi bật phong cách HUD
    """
    layout_update = {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(18, 23, 34, 0.6)",
        "font": {
            "family": FONT_CODE,
            "color": COLOR_TEXT_PRIMARY,
            "size": 11,
        },
        "margin": {"l": 45, "r": 35, "t": 45 if title else 25, "b": 40},
        "height": height,
        "showlegend": show_legend,
        "hoverlabel": {
            "bgcolor": COLOR_BG_ROOT,
            "bordercolor": COLOR_CYAN,
            "font": {"family": FONT_CODE, "size": 12, "color": COLOR_TEXT_PRIMARY},
        },
        "xaxis": {
            "gridcolor": COLOR_GRID,
            "zerolinecolor": COLOR_BORDER,
            "tickfont": {"family": FONT_CODE, "size": 10, "color": COLOR_TEXT_MUTED},
            "title_font": {"family": FONT_DISPLAY, "size": 12, "color": COLOR_TEXT_PRIMARY},
        },
        "yaxis": {
            "gridcolor": COLOR_GRID,
            "zerolinecolor": COLOR_BORDER,
            "tickfont": {"family": FONT_CODE, "size": 10, "color": COLOR_TEXT_MUTED},
            "title_font": {"family": FONT_DISPLAY, "size": 12, "color": COLOR_TEXT_PRIMARY},
        },
    }

    if title:
        layout_update["title"] = {
            "text": title,
            "font": {"family": FONT_DISPLAY, "size": 14, "color": COLOR_TEXT_PRIMARY},
            "x": 0.02,
            "xanchor": "left",
        }

    if show_legend:
        layout_update["legend"] = {
            "bgcolor": "rgba(18, 23, 34, 0.7)",
            "bordercolor": COLOR_BORDER,
            "borderwidth": 1,
            "font": {"family": FONT_CODE, "size": 10, "color": COLOR_TEXT_MUTED},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0,
        }

    fig.update_layout(**layout_update)
    return fig


def render_hud_card(
    st: Any,
    label: str,
    value: str,
    subtext: str = "",
    badge: Optional[str] = None,
    accent: str = "cyan",
) -> None:
    """Render một thẻ chỉ số Telemetry HUD đồng bộ."""
    badge_html = f'<span class="hud-badge hud-badge-{accent}">{badge}</span>' if badge else ""
    html = f"""
    <div class="hud-card accent-{accent}">
        <div class="hud-label">
            <span>{label}</span>
            {badge_html}
        </div>
        <div class="hud-value">{value}</div>
        <div class="hud-subtext">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
