"""Interactive Seek Slider with click-to-jump and hover tooltip."""
from PySide6.QtWidgets import QSlider, QToolTip
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent
from ...utils.formatters import format_time_ms


class SeekSlider(QSlider):
    user_seeked = Signal(int)       # Emits target position in milliseconds
    seeking_started = Signal()
    seeking_finished = Signal()

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self._is_user_dragging = False

    def is_user_dragging(self) -> bool:
        return self._is_user_dragging

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_user_dragging = True
            self.seeking_started.emit()
            pos = self._pixel_pos_to_value(event.position().x())
            self.setValue(pos)
            self.user_seeked.emit(pos)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self._pixel_pos_to_value(event.position().x())
        if self._is_user_dragging:
            self.setValue(pos)
            self.user_seeked.emit(pos)
        else:
            # Show hover time tooltip
            time_str = format_time_ms(pos)
            global_pos = self.mapToGlobal(QPoint(int(event.position().x()), -24))
            QToolTip.showText(global_pos, time_str, self)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_user_dragging = False
            pos = self._pixel_pos_to_value(event.position().x())
            self.setValue(pos)
            self.user_seeked.emit(pos)
            self.seeking_finished.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _pixel_pos_to_value(self, x: float) -> int:
        width = self.width()
        if width <= 0 or self.maximum() <= self.minimum():
            return 0
        ratio = max(0.0, min(1.0, x / width))
        val = int(self.minimum() + ratio * (self.maximum() - self.minimum()))
        return val
