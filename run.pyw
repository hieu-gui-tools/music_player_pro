"""Silent GUI Launcher for Music Player Pro."""
import sys
import os
import ctypes
from pathlib import Path

# Add src directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Ensure working directory is ROOT_DIR
os.chdir(str(ROOT_DIR))

try:
    from music_player_pro.main import main
    main()
except Exception:
    import traceback
    err = traceback.format_exc()
    try:
        with open(ROOT_DIR / "crash.log", "a", encoding="utf-8") as f:
            f.write(err + "\n")
    except Exception:
        pass

    ctypes.windll.user32.MessageBoxW(
        0,
        f"Đã xảy ra lỗi khi khởi động Music Player Pro:\n\n{err}",
        "Music Player Pro - Lỗi Khởi Động",
        0x10  # MB_ICONERROR
    )
    sys.exit(1)
