"""Application entry point for Music Player Pro."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from .ui.main_window import MainWindow


def main():
    # High DPI scaling is handled automatically in Qt6
    app = QApplication(sys.argv)
    app.setApplicationName("Music Player Pro")
    app.setApplicationDisplayName("Music Player Pro")
    app.setOrganizationName("MusicPlayerDev")
    app.setQuitOnLastWindowClosed(False)

    icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.ico"
    if not icon_path.exists():
        icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    # Force window visible via Windows User32 API in case started from a hidden parent process
    try:
        import ctypes
        hwnd = int(window.winId())
        ctypes.windll.user32.ShowWindow(hwnd, 1)  # 1 = SW_SHOWNORMAL
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
