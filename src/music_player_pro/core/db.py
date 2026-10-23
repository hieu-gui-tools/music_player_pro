"""SQLite Database storage for folders, playlists, and playback resume memory."""
import sqlite3
from pathlib import Path
from typing import Optional, List
from .models import Playlist, SavedFolder, PlaybackMemory


class Database:
    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            data_dir = Path.home() / ".music_player_pro"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path_str = str(data_dir / "library.db")
        elif str(db_path) == ":memory:":
            self.db_path_str = ":memory:"
        else:
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self.db_path_str = str(p)
            
        self._conn = sqlite3.connect(self.db_path_str)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        if self.db_path_str != ":memory:":
            self._conn.execute("PRAGMA journal_mode = WAL")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return self._conn

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Folders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Playlists table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Playlist tracks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL,
                    track_path TEXT NOT NULL,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
                )
            """)

            # Playback state / resume memory
            # Remembers last playing track and position in ms for each folder and playlist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playback_states (
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    last_track_path TEXT,
                    last_position_ms INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(source_type, source_id)
                )
            """)

            # App settings (key-value)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    # --- Folder methods ---
    def add_folder(self, path: str, name: Optional[str] = None) -> int:
        norm_path = str(Path(path).resolve())
        folder_name = name or Path(norm_path).name or norm_path
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO folders (path, name) 
                VALUES (?, ?)
                ON CONFLICT(path) DO UPDATE SET name=excluded.name
            """, (norm_path, folder_name))
            conn.commit()
            return cursor.lastrowid

    def get_folders(self) -> List[SavedFolder]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, path, name, added_at FROM folders ORDER BY name ASC")
            rows = cursor.fetchall()
            return [
                SavedFolder(
                    id=row["id"],
                    path=row["path"],
                    name=row["name"],
                    added_at=str(row["added_at"])
                )
                for row in rows
            ]

    def remove_folder(self, folder_path: str):
        norm_path = str(Path(folder_path).resolve())
        with self._get_connection() as conn:
            conn.execute("DELETE FROM folders WHERE path = ?", (norm_path,))
            conn.execute("DELETE FROM playback_states WHERE source_type = 'folder' AND source_id = ?", (norm_path,))
            conn.commit()

    # --- Playlist methods ---
    def create_playlist(self, name: str) -> int:
        clean_name = name.strip()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO playlists (name) VALUES (?)", (clean_name,))
            conn.commit()
            return cursor.lastrowid

    def rename_playlist(self, playlist_id: int, new_name: str) -> bool:
        clean_name = new_name.strip()
        with self._get_connection() as conn:
            try:
                conn.execute("UPDATE playlists SET name = ? WHERE id = ?", (clean_name, playlist_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def delete_playlist(self, playlist_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
            conn.execute("DELETE FROM playback_states WHERE source_type = 'playlist' AND source_id = ?", (str(playlist_id),))
            conn.commit()

    def get_playlists(self) -> List[Playlist]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.created_at, COUNT(pt.id) as track_count
                FROM playlists p
                LEFT JOIN playlist_tracks pt ON p.id = pt.playlist_id
                GROUP BY p.id
                ORDER BY p.name ASC
            """)
            rows = cursor.fetchall()
            return [
                Playlist(
                    id=row["id"],
                    name=row["name"],
                    created_at=str(row["created_at"]),
                    track_count=row["track_count"]
                )
                for row in rows
            ]

    def add_tracks_to_playlist(self, playlist_id: int, track_paths: List[str]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Find current max sort_order
            cursor.execute("SELECT COALESCE(MAX(sort_order), 0) FROM playlist_tracks WHERE playlist_id = ?", (playlist_id,))
            max_order = cursor.fetchone()[0]
            
            for i, path in enumerate(track_paths, start=1):
                cursor.execute("""
                    INSERT INTO playlist_tracks (playlist_id, track_path, sort_order)
                    VALUES (?, ?, ?)
                """, (playlist_id, str(Path(path).resolve()), max_order + i))
            conn.commit()

    def remove_track_from_playlist(self, playlist_id: int, track_path: str):
        with self._get_connection() as conn:
            conn.execute("""
                DELETE FROM playlist_tracks 
                WHERE playlist_id = ? AND track_path = ?
            """, (playlist_id, str(Path(track_path).resolve())))
            conn.commit()

    def get_playlist_track_paths(self, playlist_id: int) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT track_path FROM playlist_tracks 
                WHERE playlist_id = ? 
                ORDER BY sort_order ASC, id ASC
            """, (playlist_id,))
            rows = cursor.fetchall()
            return [row["track_path"] for row in rows]

    # --- Playback memory methods ---
    def save_playback_memory(self, source_type: str, source_id: str, last_track_path: str, last_position_ms: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO playback_states (source_type, source_id, last_track_path, last_position_ms, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(source_type, source_id) DO UPDATE SET
                    last_track_path = excluded.last_track_path,
                    last_position_ms = excluded.last_position_ms,
                    updated_at = CURRENT_TIMESTAMP
            """, (source_type, str(source_id), str(last_track_path), int(last_position_ms)))
            conn.commit()

    def get_playback_memory(self, source_type: str, source_id: str) -> Optional[PlaybackMemory]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source_type, source_id, last_track_path, last_position_ms, updated_at
                FROM playback_states
                WHERE source_type = ? AND source_id = ?
            """, (source_type, str(source_id)))
            row = cursor.fetchone()
            if row:
                return PlaybackMemory(
                    source_type=row["source_type"],
                    source_id=row["source_id"],
                    last_track_path=row["last_track_path"],
                    last_position_ms=row["last_position_ms"],
                    updated_at=str(row["updated_at"])
                )
            return None

    # --- App settings ---
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return row["value"]
            return default

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO app_settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, str(value)))
            conn.commit()
