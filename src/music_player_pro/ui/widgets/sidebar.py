"""Sidebar widget for navigation between folders and playlists."""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QMenu, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from ...core.models import SavedFolder, Playlist
from ..icons import (
    SVG_MUSIC, SVG_FOLDER, SVG_FOLDER_ADD,
    SVG_PLAYLIST, SVG_PLAYLIST_ADD, SVG_TRASH, render_svg_icon
)


class Sidebar(QFrame):
    folder_selected = Signal(object)             # SavedFolder
    playlist_selected = Signal(object)           # Playlist
    add_folder_clicked = Signal()
    create_playlist_clicked = Signal()
    remove_folder_requested = Signal(str)        # folder_path
    delete_playlist_requested = Signal(int)      # playlist_id
    rename_playlist_requested = Signal(int, str) # playlist_id, new_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar_frame")
        self.setFixedWidth(240)
        self.folders: List[SavedFolder] = []
        self.playlists: List[Playlist] = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Brand / App Header
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_icon = QLabel(self)
        brand_icon.setPixmap(render_svg_icon(SVG_MUSIC, normal_color="#10b981", active_color="#10b981", size=24).pixmap(24, 24))
        brand_title = QLabel("Music Player Pro", self)
        brand_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        brand_layout.addWidget(brand_icon)
        brand_layout.addWidget(brand_title)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)

        # Divider
        line = QFrame(self)
        line.setStyleSheet("border-top: 1px solid #1e2330; margin: 10px 0;")
        layout.addWidget(line)

        # Folders Section Header
        lbl_folders = QLabel("THƯ MỤC NHẠC", self)
        lbl_folders.setObjectName("sidebar_header")
        layout.addWidget(lbl_folders)

        # Add Folder Button
        self.btn_add_folder = QPushButton(" Thêm Thư Mục", self)
        self.btn_add_folder.setIcon(render_svg_icon(SVG_FOLDER_ADD, normal_color="#cbd5e1", active_color="#ffffff", size=16))
        self.btn_add_folder.clicked.connect(self.add_folder_clicked.emit)
        layout.addWidget(self.btn_add_folder)

        # Folder List
        self.list_folders = QListWidget(self)
        self.list_folders.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_folders.customContextMenuRequested.connect(self._show_folder_context_menu)
        self.list_folders.itemClicked.connect(self._on_folder_item_clicked)
        layout.addWidget(self.list_folders, 1)

        # Playlists Section Header
        lbl_playlists = QLabel("DANH SÁCH PHÁT", self)
        lbl_playlists.setObjectName("sidebar_header")
        layout.addWidget(lbl_playlists)

        # Add Playlist Button
        self.btn_add_playlist = QPushButton(" Tạo Playlist Mới", self)
        self.btn_add_playlist.setIcon(render_svg_icon(SVG_PLAYLIST_ADD, normal_color="#cbd5e1", active_color="#ffffff", size=16))
        self.btn_add_playlist.clicked.connect(self.create_playlist_clicked.emit)
        layout.addWidget(self.btn_add_playlist)

        # Playlist List
        self.list_playlists = QListWidget(self)
        self.list_playlists.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_playlists.customContextMenuRequested.connect(self._show_playlist_context_menu)
        self.list_playlists.itemClicked.connect(self._on_playlist_item_clicked)
        layout.addWidget(self.list_playlists, 1)

    def set_folders(self, folders: List[SavedFolder], current_path: Optional[str] = None):
        self.folders = list(folders)
        self.list_folders.clear()
        
        icon_folder = render_svg_icon(SVG_FOLDER, normal_color="#38bdf8", active_color="#38bdf8", size=16)
        selected_row = -1

        for idx, f in enumerate(self.folders):
            item = QListWidgetItem(f.name)
            item.setIcon(icon_folder)
            item.setToolTip(f.path)
            item.setData(Qt.ItemDataRole.UserRole, f)
            self.list_folders.addItem(item)
            if current_path and Path(f.path).resolve() == Path(current_path).resolve():
                selected_row = idx

        if selected_row >= 0:
            self.list_folders.setCurrentRow(selected_row)

    def set_playlists(self, playlists: List[Playlist], current_id: Optional[int] = None):
        self.playlists = list(playlists)
        self.list_playlists.clear()

        icon_playlist = render_svg_icon(SVG_PLAYLIST, normal_color="#a855f7", active_color="#a855f7", size=16)
        selected_row = -1

        for idx, p in enumerate(self.playlists):
            count_text = f" ({p.track_count})" if p.track_count > 0 else ""
            item = QListWidgetItem(f"{p.name}{count_text}")
            item.setIcon(icon_playlist)
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.list_playlists.addItem(item)
            if current_id is not None and p.id == current_id:
                selected_row = idx

        if selected_row >= 0:
            self.list_playlists.setCurrentRow(selected_row)

    def _on_folder_item_clicked(self, item: QListWidgetItem):
        self.list_playlists.clearSelection()
        folder = item.data(Qt.ItemDataRole.UserRole)
        if folder:
            self.folder_selected.emit(folder)

    def _on_playlist_item_clicked(self, item: QListWidgetItem):
        self.list_folders.clearSelection()
        playlist = item.data(Qt.ItemDataRole.UserRole)
        if playlist:
            self.playlist_selected.emit(playlist)

    def select_folder_by_path(self, folder_path: str):
        self.list_playlists.clearSelection()
        norm = Path(folder_path).resolve()
        for i in range(self.list_folders.count()):
            item = self.list_folders.item(i)
            folder = item.data(Qt.ItemDataRole.UserRole)
            if folder and Path(folder.path).resolve() == norm:
                self.list_folders.setCurrentRow(i)
                break

    def select_playlist_by_id(self, playlist_id: int):
        self.list_folders.clearSelection()
        for i in range(self.list_playlists.count()):
            item = self.list_playlists.item(i)
            playlist = item.data(Qt.ItemDataRole.UserRole)
            if playlist and playlist.id == playlist_id:
                self.list_playlists.setCurrentRow(i)
                break

    def _show_folder_context_menu(self, pos):
        item = self.list_folders.itemAt(pos)
        if not item:
            return
        folder: SavedFolder = item.data(Qt.ItemDataRole.UserRole)
        if not folder:
            return

        menu = QMenu(self)
        act_open_explorer = menu.addAction("📁 Mở trong File Explorer")
        act_remove = menu.addAction("🗑 Xoá khỏi thư viện")

        action = menu.exec(self.list_folders.viewport().mapToGlobal(pos))
        if action == act_open_explorer:
            if sys.platform == "win32":
                subprocess.run(["explorer", folder.path], check=False)
            else:
                subprocess.run(["xdg-open", folder.path], check=False)
        elif action == act_remove:
            self.remove_folder_requested.emit(folder.path)

    def _show_playlist_context_menu(self, pos):
        item = self.list_playlists.itemAt(pos)
        if not item:
            return
        playlist: Playlist = item.data(Qt.ItemDataRole.UserRole)
        if not playlist:
            return

        menu = QMenu(self)
        act_rename = menu.addAction("✏️ Đổi tên Playlist")
        act_delete = menu.addAction("🗑 Xoá Playlist")

        action = menu.exec(self.list_playlists.viewport().mapToGlobal(pos))
        if action == act_rename:
            new_name, ok = QInputDialog.getText(self, "Đổi tên Playlist", "Nhập tên mới cho playlist:", text=playlist.name)
            if ok and new_name.strip():
                self.rename_playlist_requested.emit(playlist.id, new_name.strip())
        elif action == act_delete:
            res = QMessageBox.question(
                self, "Xác nhận xoá",
                f"Bạn có chắc muốn xoá playlist '{playlist.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res == QMessageBox.StandardButton.Yes:
                self.delete_playlist_requested.emit(playlist.id)
