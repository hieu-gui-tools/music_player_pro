"""Generate high quality icon (.ico and .png) for Music Player Pro."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import (
    QImage, QPainter, QColor, QLinearGradient, QRadialGradient,
    QPen, QBrush, QPainterPath
)
from PySide6.QtCore import Qt, QRectF, QPointF


def generate_icon(output_dir: Path):
    app = QApplication.instance() or QApplication([])
    output_dir.mkdir(parents=True, exist_ok=True)

    size = 256
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # 1. Background Rounded Rect with Gradient
    bg_path = QPainterPath()
    bg_rect = QRectF(12, 12, size - 24, size - 24)
    bg_path.addRoundedRect(bg_rect, 52, 52)

    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#10b981"))   # Vibrant Emerald
    grad.setColorAt(0.6, QColor("#059669"))   # Deep Emerald
    grad.setColorAt(1.0, QColor("#0f172a"))   # Dark Slate
    painter.fillPath(bg_path, grad)

    # 2. Glowing inner border
    pen = QPen(QColor(255, 255, 255, 60), 3)
    painter.setPen(pen)
    painter.drawPath(bg_path)

    # 3. Outer Disc / Vinyl ring
    center = QPointF(size / 2, size / 2)
    disc_pen = QPen(QColor(255, 255, 255, 40), 4)
    painter.setPen(disc_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, 74, 74)
    
    disc_pen2 = QPen(QColor(255, 255, 255, 25), 2)
    painter.setPen(disc_pen2)
    painter.drawEllipse(center, 60, 60)

    # 4. Center Glowing Disc Core
    core_grad = QRadialGradient(center, 38)
    core_grad.setColorAt(0.0, QColor("#34d399"))
    core_grad.setColorAt(0.8, QColor("#059669"))
    core_grad.setColorAt(1.0, QColor("#047857"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(core_grad)
    painter.drawEllipse(center, 38, 38)

    # 5. Play / Music Note Glyphs in the Center
    # Stylized Play Triangle
    triangle_path = QPainterPath()
    cx, cy = size / 2, size / 2
    triangle_path.moveTo(cx - 10, cy - 18)
    triangle_path.lineTo(cx + 16, cy)
    triangle_path.lineTo(cx - 10, cy + 18)
    triangle_path.closeSubpath()

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#ffffff"))
    painter.drawPath(triangle_path)

    # 6. Equalizer accent waves at bottom
    painter.setBrush(QColor("#ffffff"))
    bar_w, bar_r = 6, 3
    bars = [
        (cx - 26, cy + 46, 12),
        (cx - 13, cy + 42, 20),
        (cx,      cy + 38, 28),
        (cx + 13, cy + 44, 16),
        (cx + 26, cy + 48, 8),
    ]
    for bx, by, bh in bars:
        bar_path = QPainterPath()
        bar_path.addRoundedRect(QRectF(bx - bar_w/2, by - bh/2, bar_w, bh), bar_r, bar_r)
        painter.fillPath(bar_path, QColor(255, 255, 255, 200))

    painter.end()

    # Save PNG
    png_path = output_dir / "icon.png"
    img.save(str(png_path), "PNG")
    print(f"Saved {png_path}")

    # Save multi-size ICO
    ico_path = output_dir / "icon.ico"
    # QImage save as ICO writes standard Windows icon
    img.save(str(ico_path), "ICO")
    print(f"Saved {ico_path}")


if __name__ == "__main__":
    generate_icon(Path("assets"))
