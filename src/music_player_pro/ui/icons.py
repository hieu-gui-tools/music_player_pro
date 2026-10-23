"""Vector SVG icons for the music player UI."""
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, QSize, Qt

# SVG Definitions with clean modern geometry (viewBox 0 0 24 24)
SVG_PLAY = """
<svg viewBox="0 0 24 24" fill="{color}">
    <path d="M8 5.14v13.72a1 1 0 0 0 1.5.86l11-6.86a1 1 0 0 0 0-1.72l-11-6.86A1 1 0 0 0 8 5.14z"/>
</svg>
"""

SVG_PAUSE = """
<svg viewBox="0 0 24 24" fill="{color}">
    <rect x="6" y="5" width="4" height="14" rx="1"/>
    <rect x="14" y="5" width="4" height="14" rx="1"/>
</svg>
"""

SVG_PREV = """
<svg viewBox="0 0 24 24" fill="{color}">
    <path d="M6 5a1 1 0 0 1 1 1v12a1 1 0 1 1-2 0V6a1 1 0 0 1 1-1zm12.5 1.14a1 1 0 0 0-1.5-.86l-9 5.86a1 1 0 0 0 0 1.72l9 5.86a1 1 0 0 0 1.5-.86V6.14z"/>
</svg>
"""

SVG_NEXT = """
<svg viewBox="0 0 24 24" fill="{color}">
    <path d="M18 5a1 1 0 0 1 1 1v12a1 1 0 1 1-2 0V6a1 1 0 0 1 1-1zM5.5 6.14a1 1 0 0 1 1.5-.86l9 5.86a1 1 0 0 1 0 1.72l-9 5.86a1 1 0 0 1-1.5-.86V6.14z"/>
</svg>
"""

SVG_SHUFFLE = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="16 3 21 3 21 8"/>
    <line x1="4" y1="20" x2="21" y2="3"/>
    <polyline points="21 16 21 21 16 21"/>
    <line x1="15" y1="15" x2="21" y2="21"/>
    <line x1="4" y1="4" x2="9" y2="9"/>
</svg>
"""

SVG_REPEAT = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="17 1 21 5 17 9"/>
    <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
    <polyline points="7 23 3 19 7 15"/>
    <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
</svg>
"""

SVG_REPEAT_ONE = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="17 1 21 5 17 9"/>
    <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
    <polyline points="7 23 3 19 7 15"/>
    <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
    <text x="10" y="15" font-size="7" font-weight="bold" fill="{color}" stroke="none">1</text>
</svg>
"""

SVG_VOLUME_HIGH = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
</svg>
"""

SVG_VOLUME_MUTE = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
    <line x1="23" y1="9" x2="17" y2="15"/>
    <line x1="17" y1="9" x2="23" y2="15"/>
</svg>
"""

SVG_FOLDER = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
</svg>
"""

SVG_FOLDER_ADD = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
    <line x1="12" y1="11" x2="12" y2="17"/>
    <line x1="9" y1="14" x2="15" y2="14"/>
</svg>
"""

SVG_PLAYLIST = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="8" y1="6" x2="21" y2="6"/>
    <line x1="8" y1="12" x2="21" y2="12"/>
    <line x1="8" y1="18" x2="16" y2="18"/>
    <polyline points="3 6 4 7 3 8"/>
    <polyline points="3 12 4 13 3 14"/>
    <polyline points="3 18 4 19 3 20"/>
</svg>
"""

SVG_PLAYLIST_ADD = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="4" y1="6" x2="16" y2="6"/>
    <line x1="4" y1="12" x2="14" y2="12"/>
    <line x1="4" y1="18" x2="10" y2="18"/>
    <line x1="19" y1="11" x2="19" y2="17"/>
    <line x1="16" y1="14" x2="22" y2="14"/>
</svg>
"""

SVG_MUSIC = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M9 18V5l12-2v13"/>
    <circle cx="6" cy="18" r="3"/>
    <circle cx="18" cy="16" r="3"/>
</svg>
"""

SVG_SEARCH = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
"""

SVG_TRASH = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
</svg>
"""

SVG_HISTORY = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12 6 12 12 16 14"/>
</svg>
"""

SVG_DISC = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <circle cx="12" cy="12" r="3"/>
</svg>
"""

SVG_EQUALIZER = """
<svg viewBox="0 0 24 24" fill="{color}">
    <rect x="4" y="10" width="3" height="10" rx="1.5"/>
    <rect x="10.5" y="4" width="3" height="16" rx="1.5"/>
    <rect x="17" y="8" width="3" height="12" rx="1.5"/>
</svg>
"""

SVG_TRAY = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 14h4l2 3h4l2-3h4v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-5z"/>
    <line x1="12" y1="3" x2="12" y2="12"/>
    <polyline points="9 9 12 12 15 9"/>
</svg>
"""

SVG_SETTINGS = """
<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
</svg>
"""


def render_svg_pixmap(svg_template: str, color: str = "#ffffff", size: int = 24) -> QPixmap:
    """Render an SVG string with color into a QPixmap."""
    svg_code = svg_template.format(color=color).strip()
    renderer = QSvgRenderer(QByteArray(svg_code.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def render_svg_icon(svg_template: str, normal_color: str = "#94a3b8", active_color: str = "#10b981", size: int = 24) -> QIcon:
    """Create a QIcon with normal and active state pixmaps."""
    icon = QIcon()
    pix_normal = render_svg_pixmap(svg_template, color=normal_color, size=size)
    pix_active = render_svg_pixmap(svg_template, color=active_color, size=size)
    icon.addPixmap(pix_normal, QIcon.Mode.Normal)
    icon.addPixmap(pix_active, QIcon.Mode.Active)
    icon.addPixmap(pix_active, QIcon.Mode.Selected)
    return icon
