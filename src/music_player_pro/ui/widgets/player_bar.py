"""Bottom player control bar with cover art, playback buttons, seeker, and volume."""
from typing import Optional
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage

from ...core.models import Track, RepeatMode
from ...utils.formatters import format_time_ms
from ..icons import (
    SVG_PLAY, SVG_PAUSE, SVG_PREV, SVG_NEXT,
    SVG_SHUFFLE, SVG_REPEAT, SVG_REPEAT_ONE, SVG_DISC,
    render_svg_icon, render_svg_pixmap
)
from .seek_slider import SeekSlider
from .volume_slider import VolumeWidget


class PlayerBar(QFrame):
    play_pause_clicked = Signal()
    next_clicked = Signal()
    previous_clicked = Signal()
    shuffle_clicked = Signal()
    repeat_clicked = Signal()
    seek_requested = Signal(int)     # ms
    volume_changed = Signal(float)   # 0.0 to 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("player_bar")
        self.setFixedHeight(84)

        self._is_seeking = False
        self._current_duration_ms = 0

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(16)

        # 1. Left Section: Cover Art & Track Metadata
        left_widget = QWidget(self)
        left_widget.setFixedWidth(280)
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Cover Art Label
        self.lbl_cover = QLabel(left_widget)
        self.lbl_cover.setFixedSize(54, 54)
        self.lbl_cover.setStyleSheet("background-color: #1a1e2b; border-radius: 8px; border: 1px solid #272e40;")
        self.lbl_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_default_cover()
        left_layout.addWidget(self.lbl_cover)

        # Metadata Texts
        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)
        meta_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_title = QLabel("Chưa phát bài hát nào", left_widget)
        self.lbl_title.setObjectName("track_title")
        meta_layout.addWidget(self.lbl_title)

        self.lbl_artist = QLabel("Chọn thư mục hoặc playlist để bắt đầu", left_widget)
        self.lbl_artist.setObjectName("track_artist")
        meta_layout.addWidget(self.lbl_artist)

        left_layout.addLayout(meta_layout)
        main_layout.addWidget(left_widget)

        # 2. Center Section: Playback Controls & Progress Bar
        center_widget = QWidget(self)
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(4)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top Controls Row
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(14)
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shuffle
        self.btn_shuffle = QPushButton(center_widget)
        self.btn_shuffle.setObjectName("btn_icon_ghost")
        self.btn_shuffle.setFixedSize(32, 32)
        self.btn_shuffle.setIconSize(QSize(16, 16))
        self.btn_shuffle.setIcon(render_svg_icon(SVG_SHUFFLE, normal_color="#64748b", active_color="#10b981", size=16))
        self.btn_shuffle.clicked.connect(self.shuffle_clicked.emit)
        ctrl_layout.addWidget(self.btn_shuffle)

        # Previous
        self.btn_prev = QPushButton(center_widget)
        self.btn_prev.setObjectName("btn_icon_ghost")
        self.btn_prev.setFixedSize(32, 32)
        self.btn_prev.setIconSize(QSize(20, 20))
        self.btn_prev.setIcon(render_svg_icon(SVG_PREV, normal_color="#cbd5e1", active_color="#ffffff", size=20))
        self.btn_prev.clicked.connect(self.previous_clicked.emit)
        ctrl_layout.addWidget(self.btn_prev)

        # Play / Pause (Big Circular)
        self.btn_play = QPushButton(center_widget)
        self.btn_play.setObjectName("btn_circle_play")
        self.btn_play.setFixedSize(44, 44)
        self.btn_play.setIconSize(QSize(22, 22))
        self.btn_play.setIcon(render_svg_icon(SVG_PLAY, normal_color="#ffffff", active_color="#ffffff", size=22))
        self.btn_play.clicked.connect(self.play_pause_clicked.emit)
        ctrl_layout.addWidget(self.btn_play)

        # Next
        self.btn_next = QPushButton(center_widget)
        self.btn_next.setObjectName("btn_icon_ghost")
        self.btn_next.setFixedSize(32, 32)
        self.btn_next.setIconSize(QSize(20, 20))
        self.btn_next.setIcon(render_svg_icon(SVG_NEXT, normal_color="#cbd5e1", active_color="#ffffff", size=20))
        self.btn_next.clicked.connect(self.next_clicked.emit)
        ctrl_layout.addWidget(self.btn_next)

        # Repeat
        self.btn_repeat = QPushButton(center_widget)
        self.btn_repeat.setObjectName("btn_icon_ghost")
        self.btn_repeat.setFixedSize(32, 32)
        self.btn_repeat.setIconSize(QSize(16, 16))
        self.btn_repeat.setIcon(render_svg_icon(SVG_REPEAT, normal_color="#64748b", active_color="#10b981", size=16))
        self.btn_repeat.clicked.connect(self.repeat_clicked.emit)
        ctrl_layout.addWidget(self.btn_repeat)

        center_layout.addLayout(ctrl_layout)

        # Bottom Progress Bar Row
        prog_layout = QHBoxLayout()
        prog_layout.setSpacing(8)

        self.lbl_cur_time = QLabel("00:00", center_widget)
        self.lbl_cur_time.setObjectName("time_label")
        self.lbl_cur_time.setFixedWidth(44)
        self.lbl_cur_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prog_layout.addWidget(self.lbl_cur_time)

        self.seek_slider = SeekSlider(Qt.Orientation.Horizontal, center_widget)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.setValue(0)
        self.seek_slider.seeking_started.connect(self._on_seek_started)
        self.seek_slider.user_seeked.connect(self._on_user_seeked)
        self.seek_slider.seeking_finished.connect(self._on_seek_finished)
        prog_layout.addWidget(self.seek_slider)

        self.lbl_tot_time = QLabel("00:00", center_widget)
        self.lbl_tot_time.setObjectName("time_label")
        self.lbl_tot_time.setFixedWidth(44)
        self.lbl_tot_time.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        prog_layout.addWidget(self.lbl_tot_time)

        center_layout.addLayout(prog_layout)
        main_layout.addWidget(center_widget, 1)

        # 3. Right Section: Memory Badge & Volume Widget
        right_widget = QWidget(self)
        right_widget.setFixedWidth(280)
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Memory save indicator
        self.lbl_saved_status = QLabel("● Ghi nhớ tự động", right_widget)
        self.lbl_saved_status.setStyleSheet("color: #10b981; font-size: 11px; font-weight: 500;")
        self.lbl_saved_status.setToolTip("Vị trí và bài hát đang nghe được lưu tự động cho từng folder & playlist")
        right_layout.addWidget(self.lbl_saved_status)

        # Volume
        self.volume_widget = VolumeWidget(right_widget)
        self.volume_widget.volume_changed.connect(self.volume_changed.emit)
        right_layout.addWidget(self.volume_widget)

        main_layout.addWidget(right_widget)

    def _set_default_cover(self):
        pix = render_svg_pixmap(SVG_DISC, color="#64748b", size=32)
        self.lbl_cover.setPixmap(pix)

    def update_track(self, track: Optional[Track]):
        if track is None:
            self.lbl_title.setText("Chưa phát bài hát nào")
            self.lbl_artist.setText("Chọn thư mục hoặc playlist")
            self._set_default_cover()
            self.lbl_cur_time.setText("00:00")
            self.lbl_tot_time.setText("00:00")
            self.seek_slider.setRange(0, 0)
            self.seek_slider.setValue(0)
            return

        self.lbl_title.setText(track.filename)
        if track.artist and track.artist != "Unknown Artist":
            self.lbl_artist.setText(f"{track.artist} • {track.title}")
        elif track.title and track.title != track.filename_stem:
            self.lbl_artist.setText(f"{track.title} • {track.album}")
        else:
            self.lbl_artist.setText(track.album if track.album != "Unknown Album" else track.duration_str)

        # Cover art
        if track.cover_art:
            img = QImage.fromData(track.cover_art)
            if not img.isNull():
                pix = QPixmap.fromImage(img).scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.lbl_cover.setPixmap(pix)
            else:
                self._set_default_cover()
        else:
            self._set_default_cover()

    def set_playing_state(self, is_playing: bool):
        if is_playing:
            self.btn_play.setIcon(render_svg_icon(SVG_PAUSE, normal_color="#ffffff", active_color="#ffffff", size=22))
        else:
            self.btn_play.setIcon(render_svg_icon(SVG_PLAY, normal_color="#ffffff", active_color="#ffffff", size=22))

    def update_position(self, pos_ms: int, dur_ms: int):
        self._current_duration_ms = dur_ms
        if not self._is_seeking:
            self.seek_slider.blockSignals(True)
            max_range = dur_ms if dur_ms > 0 else max(pos_ms, 1000)
            self.seek_slider.setRange(0, max_range)
            self.seek_slider.setValue(pos_ms)
            self.seek_slider.blockSignals(False)
            self.lbl_cur_time.setText(format_time_ms(pos_ms))

    def update_duration(self, dur_ms: int):
        self._current_duration_ms = dur_ms
        self.seek_slider.setRange(0, dur_ms if dur_ms > 0 else 1000)
        self.lbl_tot_time.setText(format_time_ms(dur_ms))

    def update_modes(self, repeat_mode: str, is_shuffle: bool):
        # Shuffle button styling
        if is_shuffle:
            self.btn_shuffle.setObjectName("btn_icon_active")
            self.btn_shuffle.setIcon(render_svg_icon(SVG_SHUFFLE, normal_color="#10b981", active_color="#10b981", size=16))
        else:
            self.btn_shuffle.setObjectName("btn_icon_ghost")
            self.btn_shuffle.setIcon(render_svg_icon(SVG_SHUFFLE, normal_color="#64748b", active_color="#10b981", size=16))
        self.btn_shuffle.style().unpolish(self.btn_shuffle)
        self.btn_shuffle.style().polish(self.btn_shuffle)

        # Repeat button styling
        if repeat_mode == "one":
            self.btn_repeat.setObjectName("btn_icon_active")
            self.btn_repeat.setIcon(render_svg_icon(SVG_REPEAT_ONE, normal_color="#10b981", active_color="#10b981", size=16))
        elif repeat_mode == "all":
            self.btn_repeat.setObjectName("btn_icon_active")
            self.btn_repeat.setIcon(render_svg_icon(SVG_REPEAT, normal_color="#10b981", active_color="#10b981", size=16))
        else:
            self.btn_repeat.setObjectName("btn_icon_ghost")
            self.btn_repeat.setIcon(render_svg_icon(SVG_REPEAT, normal_color="#64748b", active_color="#10b981", size=16))
        self.btn_repeat.style().unpolish(self.btn_repeat)
        self.btn_repeat.style().polish(self.btn_repeat)

    def set_volume(self, vol: float):
        self.volume_widget.set_volume(vol)

    def _on_seek_started(self):
        self._is_seeking = True

    def _on_user_seeked(self, val: int):
        self.lbl_cur_time.setText(format_time_ms(val))

    def _on_seek_finished(self):
        self._is_seeking = False
        self.seek_requested.emit(self.seek_slider.value())
