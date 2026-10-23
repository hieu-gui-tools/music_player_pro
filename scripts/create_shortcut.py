"""Create Windows Desktop shortcut for Music Player Pro."""
import os
import sys
from pathlib import Path


def create_desktop_shortcut():
    try:
        import win32com.client  # In case pywin32 is present
        shell = win32com.client.Dispatch("WScript.Shell")
    except ImportError:
        # Fallback to subprocess with powershell
        project_dir = Path(__file__).resolve().parent.parent
        ps_script = project_dir / "scripts" / "create_shortcut.ps1"
        import subprocess
        res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)], capture_output=True, text=True)
        print(res.stdout)
        if res.stderr:
            print(res.stderr)
        return

    project_dir = Path(__file__).resolve().parent.parent
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
    shortcut_path = desktop / "Music Player Pro.lnk"
    
    vbs_path = project_dir / "run.vbs"
    icon_path = project_dir / "assets" / "icon.ico"

    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = "wscript.exe"
    shortcut.Arguments = f'"{vbs_path}"'
    shortcut.WorkingDirectory = str(project_dir)
    shortcut.IconLocation = f"{icon_path}, 0"
    shortcut.Description = "Music Player Pro - Trình phát nhạc chuyên nghiệp"
    shortcut.Save()
    print(f"Desktop shortcut created at: {shortcut_path}")


if __name__ == "__main__":
    create_desktop_shortcut()
