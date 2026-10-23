"""Data models for tracks, playlists, and playback states."""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from ..utils.formatters import format_time_ms, format_file_size


class RepeatMode(Enum):
    OFF = "off"
    ALL = "all"
    ONE = "one"


class SourceType(Enum):
    FOLDER = "folder"
    PLAYLIST = "playlist"


@dataclass
class Track:
    path: str
    title: str = ""
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    duration_ms: int = 0
    file_size: int = 0
    file_format: str = ""
    cover_art: Optional[bytes] = None
    year: Optional[str] = None
    genre: Optional[str] = None

    def __post_init__(self):
        if not self.title:
            self.title = Path(self.path).stem
        if not self.file_format:
            self.file_format = Path(self.path).suffix.lower()

    @property
    def duration_str(self) -> str:
        return format_time_ms(self.duration_ms)

    @property
    def file_size_str(self) -> str:
        return format_file_size(self.file_size)

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def filename_stem(self) -> str:
        return Path(self.path).stem


@dataclass
class Playlist:
    id: int
    name: str
    created_at: str
    track_count: int = 0


@dataclass
class SavedFolder:
    id: int
    path: str
    name: str
    added_at: str
    track_count: int = 0


@dataclass
class PlaybackMemory:
    source_type: str  # "folder" or "playlist"
    source_id: str    # folder path or playlist id (as str)
    last_track_path: str
    last_position_ms: int = 0
    updated_at: str = ""
