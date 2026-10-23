"""Modern Dark Theme stylesheet and color palettes."""

DARK_STYLESHEET = """
/* Global Window Styling */
QMainWindow, QDialog {
    background-color: #0d0f15;
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
}

QWidget {
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
}

/* Sidebar Styling */
QFrame#sidebar_frame {
    background-color: #12151e;
    border-right: 1px solid #1e2330;
}

QLabel#sidebar_header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #64748b;
    padding-top: 14px;
    padding-bottom: 6px;
    padding-left: 8px;
    text-transform: uppercase;
}

/* Lists and Trees */
QListWidget, QTreeWidget {
    background-color: transparent;
    border: none;
    outline: none;
    color: #cbd5e1;
    font-size: 13px;
}

QListWidget::item {
    height: 36px;
    padding-left: 10px;
    padding-right: 8px;
    border-radius: 8px;
    margin: 2px 4px;
}

QListWidget::item:hover {
    background-color: #1e2330;
    color: #ffffff;
}

QListWidget::item:selected {
    background-color: #1e293b;
    color: #10b981;
    font-weight: 600;
}

/* Header Banner */
QFrame#header_banner {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a202c, stop:1 #12151e);
    border-bottom: 1px solid #1e2330;
    border-radius: 0px;
}

QLabel#banner_title {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#banner_subtitle {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#banner_resume_badge {
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #10b981;
    font-size: 11px;
    font-weight: 600;
    border-radius: 12px;
    padding: 3px 10px;
}

/* Track Table */
QTableWidget {
    background-color: #0d0f15;
    border: none;
    gridline-color: transparent;
    selection-background-color: #1e2330;
    selection-color: #10b981;
    outline: none;
}

QHeaderView::section {
    background-color: #0d0f15;
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    border: none;
    border-bottom: 1px solid #1e2330;
    padding: 8px 6px;
}

QTableWidget::item {
    border-bottom: 1px solid #151822;
    padding: 6px;
    color: #cbd5e1;
}

QTableWidget::item:selected {
    background-color: #1e2330;
    color: #ffffff;
}

QTableWidget::item:hover {
    background-color: #171b26;
}

/* Bottom Player Bar */
QFrame#player_bar {
    background-color: #12151e;
    border-top: 1px solid #1e2330;
}

QLabel#track_title {
    font-size: 14px;
    font-weight: 600;
    color: #f8fafc;
}

QLabel#track_artist {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#time_label {
    font-size: 11px;
    color: #64748b;
    font-family: "Cascadia Code", "Consolas", monospace;
}

/* Buttons */
QPushButton {
    background-color: #1e2330;
    color: #e2e8f0;
    border: 1px solid #2d3345;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #272e40;
    border-color: #3b445c;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #171b26;
}

QPushButton#btn_primary {
    background-color: #10b981;
    color: #ffffff;
    border: none;
    font-weight: 600;
}

QPushButton#btn_primary:hover {
    background-color: #059669;
}

QPushButton#btn_primary:pressed {
    background-color: #047857;
}

QPushButton#btn_circle_play {
    background-color: #10b981;
    border-radius: 22px;
    border: none;
}

QPushButton#btn_circle_play:hover {
    background-color: #059669;
}

QPushButton#btn_circle_play:pressed {
    background-color: #047857;
}

QPushButton#btn_icon_ghost {
    background-color: transparent;
    border: none;
    border-radius: 16px;
}

QPushButton#btn_icon_ghost:hover {
    background-color: #1e2330;
}

QPushButton#btn_icon_active {
    background-color: rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.5);
    border-radius: 16px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 4px;
    background: #272e40;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #10b981;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QSlider::handle:horizontal:hover {
    background: #10b981;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

/* Search Input */
QLineEdit#search_input {
    background-color: #161922;
    border: 1px solid #272e40;
    border-radius: 16px;
    padding: 6px 14px;
    color: #f8fafc;
    font-size: 12px;
}

QLineEdit#search_input:focus {
    border: 1px solid #10b981;
    background-color: #1a1e2b;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #272e40;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #3b445c;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #272e40;
    min-width: 25px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #3b445c;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Context Menu */
QMenu {
    background-color: #161922;
    border: 1px solid #272e40;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 7px 24px 7px 12px;
    border-radius: 6px;
    color: #cbd5e1;
}

QMenu::item:selected {
    background-color: #10b981;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: #272e40;
    margin: 4px 6px;
}

/* Tooltips */
QToolTip {
    background-color: #1a1e2b;
    color: #f8fafc;
    border: 1px solid #2d3345;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
}
"""
