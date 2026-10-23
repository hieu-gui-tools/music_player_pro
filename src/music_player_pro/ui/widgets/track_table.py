"""Track Table widget showing audio tracks with rich metadata and actions."""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Callable
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QClipboard

from ...core.models import Track
from ..icons import SVG_PLAY, SVG_EQUALIZER, render_svg_pixmap, render_svg_icon


class TrackTable(QTableWidget):
    track_selected = Signal(int)                    # Row index double-clicked
    add_to_playlist_requested = Signal(str, int)    # track_path, playlist_id
    remove_from_playlist_requested = Signal(str)    # track_path
    new_playlist_with_track = Signal(str)           # track_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracks: List[Track] = []
        self.current_playing_path: Optional[str] = None
        self.is_playlist_view: bool = False
        self.get_playlists_callback: Optional[Callable[[], list]] = None

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["#", "Tên File", "Album", "Thời lượng", "Định dạng"])
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Column sizing
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(0, 48)
        self.setColumnWidth(2, 180)
        self.setColumnWidth(3, 85)
        self.setColumnWidth(4, 80)

        self.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def set_tracks(self, tracks: List[Track], is_playlist: bool = False):
        self.tracks = list(tracks)
        self.is_playlist_view = is_playlist
        self.setRowCount(len(self.tracks))

        font_bold = QFont()
        font_bold.setBold(True)

        for row, trk in enumerate(self.tracks):
            self.setRowHeight(row, 44)
            is_playing = (self.current_playing_path and Path(trk.path).resolve() == Path(self.current_playing_path).resolve())

            # Col 0: Index / Playing
            item_num = QTableWidgetItem()
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_playing:
                item_num.setIcon(render_svg_icon(SVG_EQUALIZER, normal_color="#10b981", active_color="#10b981", size=16))
            else:
                item_num.setText(str(row + 1))
                item_num.setForeground(QColor("#64748b"))
            self.setItem(row, 0, item_num)

            # Col 1: Display by Filename
            if trk.artist and trk.artist != "Unknown Artist":
                display_text = f"{trk.filename}\n{trk.artist} • {trk.title}"
            elif trk.title and trk.title != trk.filename_stem:
                display_text = f"{trk.filename}\n{trk.title}"
            else:
                display_text = trk.filename

            item_title = QTableWidgetItem(display_text)
            if is_playing:
                item_title.setForeground(QColor("#10b981"))
                item_title.setFont(font_bold)
            else:
                item_title.setForeground(QColor("#f8fafc"))
            self.setItem(row, 1, item_title)

            # Col 2: Album
            item_album = QTableWidgetItem(trk.album)
            item_album.setForeground(QColor("#94a3b8"))
            self.setItem(row, 2, item_album)

            # Col 3: Duration
            item_dur = QTableWidgetItem(trk.duration_str)
            item_dur.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_dur.setForeground(QColor("#94a3b8"))
            self.setItem(row, 3, item_dur)

            # Col 4: Format
            fmt_str = trk.file_format.upper().replace(".", "")
            item_fmt = QTableWidgetItem(fmt_str)
            item_fmt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_fmt.setForeground(QColor("#64748b"))
            self.setItem(row, 4, item_fmt)

    def set_current_playing_path(self, path: Optional[str]):
        self.current_playing_path = path
        # Re-render indicators
        for row, trk in enumerate(self.tracks):
            is_playing = (path is not None and Path(trk.path).resolve() == Path(path).resolve())
            item_num = self.item(row, 0)
            item_title = self.item(row, 1)

            if item_num:
                if is_playing:
                    item_num.setIcon(render_svg_icon(SVG_EQUALIZER, normal_color="#10b981", active_color="#10b981", size=16))
                    item_num.setText("")
                else:
                    item_num.setIcon(render_svg_icon(SVG_PLAY, normal_color="transparent", active_color="transparent", size=0))
                    item_num.setText(str(row + 1))
                    item_num.setForeground(QColor("#64748b"))

            if item_title:
                font = item_title.font()
                font.setBold(is_playing)
                item_title.setFont(font)
                item_title.setForeground(QColor("#10b981" if is_playing else "#f8fafc"))

    def filter_tracks(self, query: str):
        q = query.strip().lower()
        for row, trk in enumerate(self.tracks):
            if not q:
                self.setRowHidden(row, False)
                continue
            matched = (
                q in trk.filename.lower() or
                q in trk.title.lower() or
                q in trk.artist.lower() or
                q in trk.album.lower() or
                q in trk.path.lower()
            )
            self.setRowHidden(row, not matched)

    def _on_cell_double_clicked(self, row: int, column: int):
        self.track_selected.emit(row)

    def _show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return
        row = item.row()
        if not (0 <= row < len(self.tracks)):
            return

        track = self.tracks[row]
        menu = QMenu(self)

        act_play = menu.addAction("▶ Phát bài này")
        menu.addSeparator()

        # Playlist submenu
        submenu_playlist = menu.addMenu("➕ Thêm vào Playlist")
        if self.get_playlists_callback:
            playlists = self.get_playlists_callback()
            for p in playlists:
                submenu_playlist.addAction(p.name, lambda pid=p.id: self.add_to_playlist_requested.emit(track.path, pid))
            if playlists:
                submenu_playlist.addSeparator()
        submenu_playlist.addAction("✨ Tạo playlist mới...", lambda: self.new_playlist_with_track.emit(track.path))

        if self.is_playlist_view:
            act_remove = menu.addAction("🗑 Xoá khỏi playlist này")
            act_remove.triggered.connect(lambda: self.remove_from_playlist_requested.emit(track.path))

        menu.addSeparator()
        act_open_folder = menu.addAction("📁 Mở thư mục chứa file")
        act_copy_path = menu.addAction("📋 Sao chép đường dẫn")

        action = menu.exec(self.viewport().mapToGlobal(pos))
        if action == act_play:
            self.track_selected.emit(row)
        elif action == act_copy_path:
            QApplication.clipboard().setText(track.path)
        elif action == act_open_folder:
            self._reveal_in_explorer(track.path)

    def _reveal_in_explorer(self, file_path: str):
        p = Path(file_path)
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p.parent)], check=False)
