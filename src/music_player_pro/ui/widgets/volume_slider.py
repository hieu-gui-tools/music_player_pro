"""Volume controller widget with mute button and slider."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QToolTip
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QMouseEvent

from ..icons import SVG_VOLUME_HIGH, SVG_VOLUME_MUTE, render_svg_icon
from .seek_slider import SeekSlider


class VolumeWidget(QWidget):
    volume_changed = Signal(float)  # 0.0 to 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._prev_volume = 0.75
        self._is_muted = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.btn_mute = QPushButton(self)
        self.btn_mute.setObjectName("btn_icon_ghost")
        self.btn_mute.setFixedSize(30, 30)
        self.btn_mute.setIconSize(QSize(18, 18))
        self.btn_mute.clicked.connect(self._toggle_mute)
        layout.addWidget(self.btn_mute)

        self.slider = SeekSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(75)
        self.slider.setFixedWidth(90)
        self.slider.user_seeked.connect(self._on_slider_moved)
        self.slider.valueChanged.connect(self._on_slider_moved)
        layout.addWidget(self.slider)

        self._update_icon(0.75)

    def _toggle_mute(self):
        if self._is_muted:
            self._is_muted = False
            self.set_volume(self._prev_volume if self._prev_volume > 0.05 else 0.5)
        else:
            self._prev_volume = self.slider.value() / 100.0
            self._is_muted = True
            self.slider.setValue(0)
            self.volume_changed.emit(0.0)
            self._update_icon(0.0)

    def _on_slider_moved(self, val: int):
        vol = val / 100.0
        self._is_muted = (vol == 0.0)
        self._update_icon(vol)
        self.volume_changed.emit(vol)

    def set_volume(self, vol: float):
        self.slider.blockSignals(True)
        val = int(vol * 100)
        self.slider.setValue(val)
        self.slider.blockSignals(False)
        self._is_muted = (val == 0)
        self._update_icon(vol)

    def _update_icon(self, vol: float):
        if vol <= 0.001 or self._is_muted:
            icon = render_svg_icon(SVG_VOLUME_MUTE, normal_color="#ef4444", active_color="#f87171", size=18)
        else:
            icon = render_svg_icon(SVG_VOLUME_HIGH, normal_color="#94a3b8", active_color="#10b981", size=18)
        self.btn_mute.setIcon(icon)
