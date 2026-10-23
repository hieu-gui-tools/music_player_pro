"""Main Window for Music Player Pro."""
from pathlib import Path
from typing import List, Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFileDialog, QInputDialog, QMessageBox, QStatusBar, QLabel,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QSize, QEvent, QTimer
from PySide6.QtGui import QIcon

from ..core.models import Track, SavedFolder, Playlist, SourceType
from ..core.db import Database
from ..core.player import PlayerController
from ..core.scanner import ScannerThread, extract_track_info, scan_directory
from .theme import DARK_STYLESHEET
from .icons import SVG_MUSIC, render_svg_icon
from .widgets import Sidebar, HeaderBanner, TrackTable, PlayerBar, SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, db: Optional[Database] = None):
        super().__init__()
        self.setWindowTitle("Music Player Pro")
        self.resize(1100, 720)
        self.setMinimumSize(850, 550)

        # Apply dark theme
        self.setStyleSheet(DARK_STYLESHEET)
        
        # Application Icon
        icon_path = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icon.ico"
        if not icon_path.exists():
            icon_path = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            self.setWindowIcon(render_svg_icon(SVG_MUSIC, normal_color="#10b981", active_color="#10b981", size=32))

        # Core logic
        self.db = db or Database()
        self.player = PlayerController(self.db, self)
        
        # State
        self.current_source_type: Optional[str] = None     # "folder" or "playlist"
        self.current_source_id: Optional[str] = None       # folder path or playlist id (str)
        self.current_tracks: List[Track] = []
        self._scanner_thread: Optional[ScannerThread] = None
        self._is_quitting: bool = False
        self._tray_message_shown: bool = False

        # Build UI
        self._setup_ui()
        self._setup_tray_icon()
        self._connect_signals()

        # Load initial data
        self._load_sidebar_data()
        self._restore_last_session()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Upper Area: Sidebar + Main Content
        upper_widget = QWidget(self)
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = Sidebar(self)
        upper_layout.addWidget(self.sidebar)

        # 2. Main Content Area
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header Banner
        self.header_banner = HeaderBanner(self)
        content_layout.addWidget(self.header_banner)

        # Track Table
        self.track_table = TrackTable(self)
        self.track_table.get_playlists_callback = self.db.get_playlists
        content_layout.addWidget(self.track_table, 1)

        upper_layout.addWidget(content_widget, 1)
        root_layout.addWidget(upper_widget, 1)

        # 3. Bottom Player Bar
        self.player_bar = PlayerBar(self)
        root_layout.addWidget(self.player_bar)

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.status_bar.setFixedHeight(22)
        self.status_bar.setStyleSheet("background-color: #0b0d13; color: #64748b; font-size: 11px; border-top: 1px solid #161922;")
        self.setStatusBar(self.status_bar)
        self.status_msg = QLabel("Sẵn sàng", self)
        self.status_bar.addWidget(self.status_msg)

    def _connect_signals(self):
        # Sidebar signals
        self.sidebar.folder_selected.connect(self._on_folder_selected)
        self.sidebar.playlist_selected.connect(self._on_playlist_selected)
        self.sidebar.add_folder_clicked.connect(self._on_add_folder)
        self.sidebar.create_playlist_clicked.connect(self._on_create_playlist)
        self.sidebar.remove_folder_requested.connect(self._on_remove_folder)
        self.sidebar.delete_playlist_requested.connect(self._on_delete_playlist)
        self.sidebar.rename_playlist_requested.connect(self._on_rename_playlist)

        # Header banner signals
        self.header_banner.play_all_clicked.connect(self._on_play_all)
        self.header_banner.shuffle_all_clicked.connect(self._on_shuffle_all)
        self.header_banner.add_files_clicked.connect(self._on_add_files)
        self.header_banner.hide_tray_clicked.connect(self._hide_to_tray)
        self.header_banner.settings_clicked.connect(self._open_settings_dialog)
        self.header_banner.resume_clicked.connect(self._on_resume_clicked)
        self.header_banner.search_changed.connect(self.track_table.filter_tracks)

        # Track table signals
        self.track_table.track_selected.connect(self._on_track_double_clicked)
        self.track_table.add_to_playlist_requested.connect(self._on_add_track_to_playlist)
        self.track_table.remove_from_playlist_requested.connect(self._on_remove_track_from_playlist)
        self.track_table.new_playlist_with_track.connect(self._on_new_playlist_with_track)

        # Player controller signals
        self.player.track_changed.connect(self._on_player_track_changed)
        self.player.playback_state_changed.connect(self._on_player_playback_state_changed)
        self.player.position_changed.connect(self.player_bar.update_position)
        self.player.duration_changed.connect(self.player_bar.update_duration)
        self.player.volume_changed.connect(self.player_bar.set_volume)
        self.player.mode_changed.connect(self.player_bar.update_modes)
        self.player.playback_resumed.connect(self._on_playback_resumed)

        # Player bar signals
        self.player_bar.play_pause_clicked.connect(self.player.toggle_play_pause)
        self.player_bar.next_clicked.connect(self.player.next_track)
        self.player_bar.previous_clicked.connect(self.player.previous_track)
        self.player_bar.shuffle_clicked.connect(self.player.toggle_shuffle)
        self.player_bar.repeat_clicked.connect(self.player.cycle_repeat_mode)
        self.player_bar.seek_requested.connect(self.player.seek)
        self.player_bar.volume_changed.connect(self.player.set_volume)

    # --- Sidebar & Data Loading ---
    def _load_sidebar_data(self):
        folders = self.db.get_folders()
        playlists = self.db.get_playlists()
        self.sidebar.set_folders(folders, self.current_source_id if self.current_source_type == "folder" else None)
        self.sidebar.set_playlists(playlists, int(self.current_source_id) if self.current_source_type == "playlist" and self.current_source_id else None)

    def _restore_last_session(self):
        last_source_type = self.db.get_setting("last_source_type")
        last_source_id = self.db.get_setting("last_source_id")
        auto_play = self.db.get_setting("auto_resume_play", "1") == "1"

        if last_source_type == "folder" and last_source_id and Path(last_source_id).exists():
            self._load_folder(last_source_id, auto_play=auto_play)
            self.sidebar.select_folder_by_path(last_source_id)
        elif last_source_type == "playlist" and last_source_id:
            try:
                pid = int(last_source_id)
                self._load_playlist(pid, auto_play=auto_play)
                self.sidebar.select_playlist_by_id(pid)
            except ValueError:
                self._load_first_available_source(auto_play=auto_play)
        else:
            self._load_first_available_source(auto_play=auto_play)

    def _load_first_available_source(self, auto_play: bool = False):
        folders = self.db.get_folders()
        if folders and Path(folders[0].path).exists():
            self._load_folder(folders[0].path, auto_play=auto_play)
            self.sidebar.select_folder_by_path(folders[0].path)
        else:
            playlists = self.db.get_playlists()
            if playlists:
                self._load_playlist(playlists[0].id, auto_play=auto_play)
                self.sidebar.select_playlist_by_id(playlists[0].id)
            else:
                self.header_banner.set_source_info(
                    source_type="folder",
                    title="Chào mừng bạn đến với Music Player Pro",
                    track_count=0,
                    total_duration_ms=0
                )
                self.status_msg.setText("Chưa có bài hát. Nhấn 'Thêm Thư Mục' hoặc 'Tạo Playlist Mới' để bắt đầu.")

    # --- Folder Actions ---
    def _on_folder_selected(self, folder: SavedFolder):
        if not Path(folder.path).exists():
            QMessageBox.warning(self, "Không tìm thấy thư mục", f"Thư mục không tồn tại trên ổ đĩa:\n{folder.path}")
            return
        self._load_folder(folder.path, auto_play=False)

    def _load_folder(self, folder_path: str, auto_play: bool = False):
        self.current_source_type = "folder"
        self.current_source_id = str(Path(folder_path).resolve())
        self.db.set_setting("last_source_type", "folder")
        self.db.set_setting("last_source_id", self.current_source_id)

        # Cancel any previous scan
        if self._scanner_thread and self._scanner_thread.isRunning():
            self._scanner_thread.cancel()
            self._scanner_thread.wait()

        self.status_msg.setText(f"Đang quét nhạc từ {folder_path}...")

        # Run scanner thread
        self._scanner_thread = ScannerThread(self.current_source_id, recursive=False, parent=self)
        self._scanner_thread.scan_complete.connect(lambda tracks: self._on_folder_scan_finished(tracks, folder_path, auto_play))
        self._scanner_thread.start()

    def _on_folder_scan_finished(self, tracks: List[Track], folder_path: str, auto_play: bool):
        self.current_tracks = tracks
        self.track_table.set_tracks(self.current_tracks, is_playlist=False)

        # Calculate totals
        total_duration = sum(t.duration_ms for t in self.current_tracks)
        folder_name = Path(folder_path).name or folder_path

        # Check resume state
        memory = self.db.get_playback_memory("folder", self.current_source_id)
        resume_name = None
        resume_pos = 0
        if memory and memory.last_track_path:
            norm_saved = Path(memory.last_track_path).resolve()
            for t in self.current_tracks:
                if Path(t.path).resolve() == norm_saved:
                    resume_name = t.filename
                    resume_pos = memory.last_position_ms
                    break

        self.header_banner.set_source_info(
            source_type="folder",
            title=folder_name,
            track_count=len(self.current_tracks),
            total_duration_ms=total_duration,
            resume_track=resume_name,
            resume_pos_ms=resume_pos
        )

        # Set player source and queue (auto-resume to saved song & position)
        self.player.set_source_and_queue(
            source_type="folder",
            source_id=self.current_source_id,
            tracks=self.current_tracks,
            auto_resume=True,
            auto_play=auto_play
        )

        self.status_msg.setText(f"Đã tải {len(self.current_tracks)} bài hát từ thư mục '{folder_name}'")

    def _on_add_folder(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa nhạc")
        if selected_dir:
            self.db.add_folder(selected_dir)
            self._load_sidebar_data()
            self._load_folder(selected_dir, auto_play=False)
            self.sidebar.select_folder_by_path(selected_dir)

    def _on_remove_folder(self, folder_path: str):
        self.db.remove_folder(folder_path)
        self._load_sidebar_data()
        if self.current_source_type == "folder" and self.current_source_id == str(Path(folder_path).resolve()):
            self.player.stop()
            self._load_first_available_source()

    # --- Playlist Actions ---
    def _on_playlist_selected(self, playlist: Playlist):
        self._load_playlist(playlist.id, auto_play=False)

    def _load_playlist(self, playlist_id: int, auto_play: bool = False):
        self.current_source_type = "playlist"
        self.current_source_id = str(playlist_id)
        self.db.set_setting("last_source_type", "playlist")
        self.db.set_setting("last_source_id", str(playlist_id))

        playlists = self.db.get_playlists()
        target_playlist = next((p for p in playlists if p.id == playlist_id), None)
        playlist_name = target_playlist.name if target_playlist else f"Playlist #{playlist_id}"

        track_paths = self.db.get_playlist_track_paths(playlist_id)
        tracks: List[Track] = []
        for p in track_paths:
            if Path(p).exists():
                tracks.append(extract_track_info(p))

        self.current_tracks = tracks
        self.track_table.set_tracks(self.current_tracks, is_playlist=True)

        total_duration = sum(t.duration_ms for t in self.current_tracks)

        # Check resume state
        memory = self.db.get_playback_memory("playlist", str(playlist_id))
        resume_name = None
        resume_pos = 0
        if memory and memory.last_track_path:
            norm_saved = Path(memory.last_track_path).resolve()
            for t in self.current_tracks:
                if Path(t.path).resolve() == norm_saved:
                    resume_name = t.filename
                    resume_pos = memory.last_position_ms
                    break

        self.header_banner.set_source_info(
            source_type="playlist",
            title=playlist_name,
            track_count=len(self.current_tracks),
            total_duration_ms=total_duration,
            resume_track=resume_name,
            resume_pos_ms=resume_pos
        )

        self.player.set_source_and_queue(
            source_type="playlist",
            source_id=str(playlist_id),
            tracks=self.current_tracks,
            auto_resume=True,
            auto_play=auto_play
        )

        self.status_msg.setText(f"Đã mở playlist '{playlist_name}' ({len(self.current_tracks)} bài hát)")

    def _on_create_playlist(self):
        name, ok = QInputDialog.getText(self, "Tạo Playlist Mới", "Nhập tên cho Playlist:")
        if ok and name.strip():
            pid = self.db.create_playlist(name.strip())
            self._load_sidebar_data()
            self._load_playlist(pid, auto_play=False)
            self.sidebar.select_playlist_by_id(pid)

    def _on_delete_playlist(self, playlist_id: int):
        self.db.delete_playlist(playlist_id)
        self._load_sidebar_data()
        if self.current_source_type == "playlist" and self.current_source_id == str(playlist_id):
            self.player.stop()
            self._load_first_available_source()

    def _on_rename_playlist(self, playlist_id: int, new_name: str):
        if self.db.rename_playlist(playlist_id, new_name):
            self._load_sidebar_data()
            if self.current_source_type == "playlist" and self.current_source_id == str(playlist_id):
                self._load_playlist(playlist_id, auto_play=False)
        else:
            QMessageBox.warning(self, "Lỗi", "Tên playlist đã tồn tại!")

    def _on_add_track_to_playlist(self, track_path: str, playlist_id: int):
        self.db.add_tracks_to_playlist(playlist_id, [track_path])
        self._load_sidebar_data()
        if self.current_source_type == "playlist" and self.current_source_id == str(playlist_id):
            self._load_playlist(playlist_id, auto_play=False)
        self.status_msg.setText("Đã thêm bài hát vào playlist thành công")

    def _on_remove_track_from_playlist(self, track_path: str):
        if self.current_source_type == "playlist" and self.current_source_id:
            pid = int(self.current_source_id)
            self.db.remove_track_from_playlist(pid, track_path)
            self._load_sidebar_data()
            self._load_playlist(pid, auto_play=False)
            self.status_msg.setText("Đã xoá bài hát khỏi playlist")

    def _on_new_playlist_with_track(self, track_path: str):
        track_name = Path(track_path).stem
        name, ok = QInputDialog.getText(self, "Tạo Playlist Mới", "Tên Playlist mới:", text=f"Tuyển tập {track_name}")
        if ok and name.strip():
            pid = self.db.create_playlist(name.strip())
            self.db.add_tracks_to_playlist(pid, [track_path])
            self._load_sidebar_data()
            self._load_playlist(pid, auto_play=False)
            self.sidebar.select_playlist_by_id(pid)

    def _on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Chọn các file nhạc", "",
            "Audio Files (*.mp3 *.flac *.wav *.ogg *.m4a *.aac *.wma *.opus)"
        )
        if not files:
            return

        if self.current_source_type == "playlist" and self.current_source_id:
            pid = int(self.current_source_id)
            self.db.add_tracks_to_playlist(pid, files)
            self._load_sidebar_data()
            self._load_playlist(pid, auto_play=False)
            self.status_msg.setText(f"Đã thêm {len(files)} bài hát vào playlist.")
        elif self.current_source_type == "folder" and self.current_source_id:
            # Inform user
            QMessageBox.information(
                self, "Thêm file vào Playlist",
                "Để tạo bộ sưu tập bài hát tùy chỉnh từ nhiều thư mục khác nhau, hãy tạo một Playlist!"
            )
        else:
            self._on_create_playlist()

    # --- Playback Coordination ---
    def _on_track_double_clicked(self, row: int):
        if row == self.player.current_index and self.player.is_paused_or_stopped():
            # If user double-clicks the currently loaded/restored track while paused, continue from saved position!
            self.player.play()
        else:
            self.player.play_track_at_index(row)

    def _on_play_all(self):
        if self.current_tracks:
            self.player.play_track_at_index(0)

    def _on_shuffle_all(self):
        if self.current_tracks:
            if not self.player.is_shuffle:
                self.player.toggle_shuffle()
            self.player.next_track()

    def _on_resume_clicked(self):
        self.player.play()

    # --- System Tray Implementation ---
    def _setup_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setToolTip("Music Player Pro")

        # Tray Context Menu
        self.tray_menu = QMenu(self)

        self.tray_act_toggle = self.tray_menu.addAction("👁 Hiện / Ẩn cửa sổ")
        self.tray_act_toggle.triggered.connect(self._toggle_window_visibility)
        self.tray_menu.addSeparator()

        self.tray_act_play_pause = self.tray_menu.addAction("▶ Phát nhạc")
        self.tray_act_play_pause.triggered.connect(self.player.toggle_play_pause)

        self.tray_act_prev = self.tray_menu.addAction("⏮ Bài trước")
        self.tray_act_prev.triggered.connect(self.player.previous_track)

        self.tray_act_next = self.tray_menu.addAction("⏭ Bài kế tiếp")
        self.tray_act_next.triggered.connect(self.player.next_track)

        self.tray_menu.addSeparator()

        self.tray_act_settings = self.tray_menu.addAction("⚙️ Cài đặt...")
        self.tray_act_settings.triggered.connect(self._open_settings_dialog)

        self.tray_act_quit = self.tray_menu.addAction("❌ Thoát ứng dụng")
        self.tray_act_quit.triggered.connect(self._force_quit)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        self.tray_icon.show()

    def _open_settings_dialog(self):
        dlg = SettingsDialog(self.db, self)
        dlg.exec()

    def _toggle_window_visibility(self):
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def _on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self._toggle_window_visibility()

    def _hide_to_tray(self):
        self.hide()
        if hasattr(self, "tray_icon") and self.tray_icon and not self._tray_message_shown:
            self.tray_icon.showMessage(
                "Music Player Pro",
                "Ứng dụng đã thu nhỏ xuống khay hệ thống (System Tray).\nNhấp vào biểu tượng ở góc phải để mở lại.",
                QSystemTrayIcon.MessageIcon.Information,
                2500
            )
            self._tray_message_shown = True

    def _force_quit(self):
        self._is_quitting = True
        self.player.save_current_state()
        self.close()
        QApplication.quit()

    def _on_player_playback_state_changed(self, is_playing: bool):
        self.player_bar.set_playing_state(is_playing)
        if hasattr(self, "tray_act_play_pause") and self.tray_act_play_pause:
            self.tray_act_play_pause.setText("⏸ Tạm dừng" if is_playing else "▶ Phát nhạc")

    def _on_player_track_changed(self, track: Optional[Track]):
        self.player_bar.update_track(track)
        if track:
            self.track_table.set_current_playing_path(track.path)
            self.status_msg.setText(f"Đang phát: {track.filename}")
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.setToolTip(f"Music Player Pro\nĐang phát: {track.filename}")
                if self.isHidden():
                    self.tray_icon.showMessage("Music Player Pro", f"Đang phát: {track.filename}", QSystemTrayIcon.MessageIcon.Information, 1500)
        else:
            self.track_table.set_current_playing_path(None)
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.setToolTip("Music Player Pro")

    def _on_playback_resumed(self, track_title: str, pos_ms: int):
        from ..utils.formatters import format_time_ms
        time_str = format_time_ms(pos_ms)
        self.status_msg.setText(f"🔄 Đã khôi phục quá trình nghe: '{track_title}' tại {time_str}")

    # --- Window Events: Minimize to Tray & Close ---
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                min_to_tray = self.db.get_setting("minimize_to_tray", "1") == "1"
                if min_to_tray and hasattr(self, "tray_icon") and self.tray_icon:
                    QTimer.singleShot(0, self._hide_to_tray)
                    event.accept()
                    return
        super().changeEvent(event)

    def closeEvent(self, event):
        close_to_tray = self.db.get_setting("close_to_tray", "0") == "1"
        if not self._is_quitting and close_to_tray:
            event.ignore()
            self._hide_to_tray()
        else:
            # Quit application completely
            self._is_quitting = True
            self.player.save_current_state()
            if self._scanner_thread and self._scanner_thread.isRunning():
                self._scanner_thread.cancel()
                self._scanner_thread.wait()
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.hide()
            event.accept()
            QApplication.quit()
