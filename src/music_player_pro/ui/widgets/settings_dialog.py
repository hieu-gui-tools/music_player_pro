"""Settings dialog for Music Player Pro."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from ...core.db import Database


class SettingsDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Cài đặt - Music Player Pro")
        self.setFixedSize(480, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Title
        title = QLabel("Cài Đặt Ứng Dụng", self)
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)

        desc = QLabel("Tuỳ chỉnh hành vi thu nhỏ, đóng cửa sổ và phát nhạc tự động:", self)
        desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(desc)

        line = QFrame(self)
        line.setStyleSheet("border-top: 1px solid #1e2330; margin: 4px 0;")
        layout.addWidget(line)

        # Checkbox 1: Minimize to Tray
        self.chk_min_to_tray = QCheckBox("Thu nhỏ xuống khay hệ thống khi nhấn nút Minimize (_)", self)
        self.chk_min_to_tray.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.chk_min_to_tray)

        desc_min = QLabel("Khi nhấn nút thu nhỏ (_), ứng dụng sẽ ẩn xuống System Tray thay vì taskbar.", self)
        desc_min.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 20px;")
        desc_min.setWordWrap(True)
        layout.addWidget(desc_min)

        # Checkbox 2: Close to Tray
        self.chk_close_to_tray = QCheckBox("Ẩn xuống khay hệ thống khi nhấn nút Đóng (X)", self)
        self.chk_close_to_tray.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.chk_close_to_tray)

        desc_close = QLabel("Nếu tắt (mặc định): Nhấn nút (X) sẽ TẮT HẲN ứng dụng.\nNếu bật: Nhấn nút (X) sẽ tiếp tục phát nhạc ngầm dưới khay hệ thống.", self)
        desc_close.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 20px;")
        desc_close.setWordWrap(True)
        layout.addWidget(desc_close)

        # Checkbox 3: Auto-resume play
        self.chk_auto_resume = QCheckBox("Tự động phát tiếp tục vị trí cũ khi mở app", self)
        self.chk_auto_resume.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.chk_auto_resume)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Huỷ", self)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Lưu cài đặt", self)
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save_settings)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _load_settings(self):
        # minimize_to_tray defaults to 1 (True)
        min_tray = self.db.get_setting("minimize_to_tray", "1") == "1"
        self.chk_min_to_tray.setChecked(min_tray)

        # close_to_tray defaults to 0 (False - user wants X to completely quit)
        close_tray = self.db.get_setting("close_to_tray", "0") == "1"
        self.chk_close_to_tray.setChecked(close_tray)

        # auto_resume defaults to 1 (True)
        auto_res = self.db.get_setting("auto_resume_play", "1") == "1"
        self.chk_auto_resume.setChecked(auto_res)

    def _save_settings(self):
        self.db.set_setting("minimize_to_tray", "1" if self.chk_min_to_tray.isChecked() else "0")
        self.db.set_setting("close_to_tray", "1" if self.chk_close_to_tray.isChecked() else "0")
        self.db.set_setting("auto_resume_play", "1" if self.chk_auto_resume.isChecked() else "0")
        self.accept()
