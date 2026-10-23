"""Test Settings Dialog and Window Minimize / Close Tray behaviors."""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QCloseEvent

from music_player_pro.core.db import Database
from music_player_pro.ui.widgets.settings_dialog import SettingsDialog
from music_player_pro.ui.main_window import MainWindow


def test_settings_and_tray():
    app = QApplication.instance() or QApplication([])
    db = Database(":memory:")

    # 1. Test Settings Dialog defaults
    dlg = SettingsDialog(db)
    assert dlg.chk_min_to_tray.isChecked() is True, "Default minimize_to_tray should be True"
    assert dlg.chk_close_to_tray.isChecked() is False, "Default close_to_tray should be False (quit on X)"
    assert dlg.chk_auto_resume.isChecked() is True, "Default auto_resume should be True"
    print("✓ Settings dialog defaults verified.")

    # 2. Test saving modified settings
    dlg.chk_close_to_tray.setChecked(True)
    dlg._save_settings()
    assert db.get_setting("close_to_tray") == "1"
    dlg.chk_close_to_tray.setChecked(False)
    dlg._save_settings()
    assert db.get_setting("close_to_tray") == "0"
    print("✓ Settings persistence to DB verified.")

    # 3. Test MainWindow with close_to_tray = 0 (X quits completely)
    win = MainWindow(db)
    win.show()
    
    # Test closeEvent with close_to_tray = 0
    evt = QCloseEvent()
    win.closeEvent(evt)
    assert evt.isAccepted() is True, "When close_to_tray is False, closeEvent should accept and quit"
    print("✓ Close button (X) quits completely when close_to_tray is 0.")

    # 4. Test MainWindow with close_to_tray = 1 (X hides to tray)
    db.set_setting("close_to_tray", "1")
    win2 = MainWindow(db)
    win2.show()
    evt2 = QCloseEvent()
    win2.closeEvent(evt2)
    assert evt2.isAccepted() is False, "When close_to_tray is True, closeEvent should ignore and hide"
    assert not win2.isVisible(), "Window should be hidden to tray"
    print("✓ Close button (X) hides to tray when close_to_tray is 1.")

    # 5. Clean up
    win._force_quit()
    win2._force_quit()
    db.close()
    print("\nALL SETTINGS & TRAY TESTS PASSED! 🎉")


if __name__ == "__main__":
    test_settings_and_tray()
