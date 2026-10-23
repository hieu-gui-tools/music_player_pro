"""Header banner displaying source info, stats, search bar, and resume indicator."""
from typing import Optional
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap

from ..icons import (
    SVG_FOLDER, SVG_PLAYLIST, SVG_PLAY, SVG_SHUFFLE,
    SVG_SEARCH, SVG_HISTORY, SVG_TRAY, SVG_SETTINGS, render_svg_icon, render_svg_pixmap
)
from ...utils.formatters import format_time_ms


class HeaderBanner(QFrame):
    play_all_clicked = Signal()
    shuffle_all_clicked = Signal()
    add_files_clicked = Signal()
    resume_clicked = Signal()
    search_changed = Signal(str)
    hide_tray_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header_banner")
        self.setFixedHeight(120)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(18)

        # Icon box
        self.lbl_icon = QLabel(self)
        self.lbl_icon.setFixedSize(72, 72)
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icon.setStyleSheet("""
            background-color: #1e2330;
            border-radius: 12px;
            border: 1px solid #2d3345;
        """)
        main_layout.addWidget(self.lbl_icon)

        # Info & Details column
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Title
        self.lbl_title = QLabel("Thư viện nhạc", self)
        self.lbl_title.setObjectName("banner_title")
        info_layout.addWidget(self.lbl_title)

        # Subtitle / Stats & Resume pill
        row_sub = QHBoxLayout()
        row_sub.setSpacing(12)

        self.lbl_stats = QLabel("Chưa chọn nguồn phát", self)
        self.lbl_stats.setObjectName("banner_subtitle")
        row_sub.addWidget(self.lbl_stats)

        # Resume Memory Badge
        self.lbl_resume = QLabel(self)
        self.lbl_resume.setObjectName("banner_resume_badge")
        self.lbl_resume.setVisible(False)
        self.lbl_resume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_resume.mousePressEvent = lambda e: self.resume_clicked.emit()
        row_sub.addWidget(self.lbl_resume)
        row_sub.addStretch()

        info_layout.addLayout(row_sub)

        # Actions buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_play_all = QPushButton(" Phát tất cả", self)
        self.btn_play_all.setObjectName("btn_primary")
        self.btn_play_all.setIcon(render_svg_icon(SVG_PLAY, normal_color="#ffffff", active_color="#ffffff", size=14))
        self.btn_play_all.clicked.connect(self.play_all_clicked.emit)
        btn_layout.addWidget(self.btn_play_all)

        self.btn_shuffle_all = QPushButton(" Trộn bài", self)
        self.btn_shuffle_all.setIcon(render_svg_icon(SVG_SHUFFLE, normal_color="#cbd5e1", active_color="#10b981", size=14))
        self.btn_shuffle_all.clicked.connect(self.shuffle_all_clicked.emit)
        btn_layout.addWidget(self.btn_shuffle_all)

        self.btn_add_files = QPushButton(" Thêm file nhạc", self)
        self.btn_add_files.clicked.connect(self.add_files_clicked.emit)
        btn_layout.addWidget(self.btn_add_files)

        self.btn_hide_tray = QPushButton(" Ẩn Tray", self)
        self.btn_hide_tray.setToolTip("Thu nhỏ ứng dụng xuống khay hệ thống (System Tray)")
        self.btn_hide_tray.setIcon(render_svg_icon(SVG_TRAY, normal_color="#cbd5e1", active_color="#10b981", size=14))
        self.btn_hide_tray.clicked.connect(self.hide_tray_clicked.emit)
        btn_layout.addWidget(self.btn_hide_tray)

        self.btn_settings = QPushButton(" Cài đặt", self)
        self.btn_settings.setToolTip("Cài đặt thu nhỏ, đóng cửa sổ và tự động phát")
        self.btn_settings.setIcon(render_svg_icon(SVG_SETTINGS, normal_color="#cbd5e1", active_color="#10b981", size=14))
        self.btn_settings.clicked.connect(self.settings_clicked.emit)
        btn_layout.addWidget(self.btn_settings)

        btn_layout.addStretch()
        info_layout.addLayout(btn_layout)

        main_layout.addLayout(info_layout, 1)

        # Search Bar
        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        self.search_input = QLineEdit(self)
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("🔍 Tìm bài hát, nghệ sĩ...")
        self.search_input.setFixedWidth(240)
        self.search_input.textChanged.connect(self.search_changed.emit)
        search_layout.addWidget(self.search_input)

        main_layout.addLayout(search_layout)

    def set_source_info(
        self,
        source_type: str,
        title: str,
        track_count: int,
        total_duration_ms: int,
        resume_track: Optional[str] = None,
        resume_pos_ms: int = 0
    ):
        self.lbl_title.setText(title)
        
        # Icon
        if source_type == "folder":
            pix = render_svg_pixmap(SVG_FOLDER, color="#38bdf8", size=40)
        else:
            pix = render_svg_pixmap(SVG_PLAYLIST, color="#a855f7", size=40)
        self.lbl_icon.setPixmap(pix)

        # Stats
        dur_str = format_time_ms(total_duration_ms)
        self.lbl_stats.setText(f"{track_count} bài hát • Tổng thời lượng: {dur_str}")

        # Resume badge
        if resume_track and resume_pos_ms > 0:
            pos_str = format_time_ms(resume_pos_ms)
            self.lbl_resume.setText(f"🕒 Đang nghe dở: {resume_track} ({pos_str}) - Nhấn để nghe tiếp")
            self.lbl_resume.setVisible(True)
        else:
            self.lbl_resume.setVisible(False)
