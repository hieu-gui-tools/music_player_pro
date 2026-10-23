"""Audio scanner and metadata extractor using Mutagen."""
import os
from pathlib import Path
from typing import List, Optional, Set
from PySide6.QtCore import QThread, Signal
import mutagen
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4

from .models import Track
from ..utils.formatters import natural_sort_key

SUPPORTED_EXTENSIONS: Set[str] = {
    ".mp3", ".flac", ".wav", ".ogg", ".m4a", 
    ".aac", ".wma", ".opus", ".aiff", ".alac"
}


def extract_track_info(file_path: str) -> Track:
    """Extract metadata and cover art from an audio file."""
    path_obj = Path(file_path)
    if not path_obj.exists() or not path_obj.is_file():
        return Track(
            path=file_path,
            title=path_obj.stem,
            artist="Unknown Artist",
            album="Unknown Album",
            duration_ms=0,
            file_size=0,
            file_format=path_obj.suffix.lower()
        )

    file_size = path_obj.stat().st_size
    file_format = path_obj.suffix.lower()
    title = path_obj.stem
    artist = "Unknown Artist"
    album = "Unknown Album"
    duration_ms = 0
    year = None
    genre = None
    cover_art: Optional[bytes] = None

    try:
        audio = mutagen.File(file_path)
        if audio is not None:
            # Duration
            if hasattr(audio, "info") and hasattr(audio.info, "length"):
                duration_ms = int(audio.info.length * 1000)

            # Tags extraction
            tags = getattr(audio, "tags", None)
            if tags:
                # 1. ID3 tags (MP3, etc.)
                if isinstance(tags, ID3) or hasattr(tags, "getall"):
                    if "TIT2" in tags:
                        title = str(tags["TIT2"].text[0])
                    if "TPE1" in tags:
                        artist = str(tags["TPE1"].text[0])
                    if "TALB" in tags:
                        album = str(tags["TALB"].text[0])
                    if "TDRC" in tags:
                        year = str(tags["TDRC"].text[0])
                    if "TCON" in tags:
                        genre = str(tags["TCON"].text[0])

                    # Cover art
                    apic_frames = tags.getall("APIC")
                    if apic_frames:
                        cover_art = apic_frames[0].data

                # 2. FLAC tags
                elif isinstance(audio, FLAC):
                    title = tags.get("title", [title])[0]
                    artist = tags.get("artist", [artist])[0]
                    album = tags.get("album", [album])[0]
                    year = tags.get("date", [None])[0]
                    genre = tags.get("genre", [None])[0]
                    if audio.pictures:
                        cover_art = audio.pictures[0].data

                # 3. MP4 / M4A tags
                elif isinstance(audio, MP4):
                    title = tags.get("\xa9nam", [title])[0]
                    artist = tags.get("\xa9ART", [artist])[0]
                    album = tags.get("\xa9alb", [album])[0]
                    year = str(tags.get("\xa9day", [None])[0]) if tags.get("\xa9day") else None
                    genre = tags.get("\xa9gen", [None])[0]
                    covr = tags.get("covr")
                    if covr and len(covr) > 0:
                        cover_art = bytes(covr[0])

                # 4. Generic dictionary-like tags (Ogg, Opus, etc.)
                elif hasattr(tags, "get"):
                    def _get_val(k):
                        v = tags.get(k)
                        if isinstance(v, list) and len(v) > 0:
                            return str(v[0])
                        return str(v) if v else None

                    t = _get_val("title")
                    if t:
                        title = t
                    ar = _get_val("artist")
                    if ar:
                        artist = ar
                    al = _get_val("album")
                    if al:
                        album = al
                    year = _get_val("date")
                    genre = _get_val("genre")

    except Exception:
        # Fallback to defaults on corrupt tags
        pass

    return Track(
        path=str(path_obj.resolve()),
        title=str(title).strip() or path_obj.stem,
        artist=str(artist).strip() or "Unknown Artist",
        album=str(album).strip() or "Unknown Album",
        duration_ms=duration_ms,
        file_size=file_size,
        file_format=file_format,
        cover_art=cover_art,
        year=year,
        genre=genre
    )


def scan_directory(dir_path: str, recursive: bool = False) -> List[Track]:
    """Synchronously scan a directory for audio tracks."""
    tracks: List[Track] = []
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        return tracks

    pattern = "**/*" if recursive else "*"
    for item in path.glob(pattern):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            tracks.append(extract_track_info(str(item)))

    # Sort tracks by filename using natural alphanumeric sorting
    tracks.sort(key=lambda t: natural_sort_key(t.filename))
    return tracks


class ScannerThread(QThread):
    """Background worker for scanning directories without freezing the GUI."""
    progress = Signal(int, int)        # current, total
    track_loaded = Signal(object)      # Track
    scan_complete = Signal(list)       # List[Track]

    def __init__(self, dir_path: str, recursive: bool = False, parent=None):
        super().__init__(parent)
        self.dir_path = dir_path
        self.recursive = recursive
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        root = Path(self.dir_path)
        if not root.exists() or not root.is_dir():
            self.scan_complete.emit([])
            return

        pattern = "**/*" if self.recursive else "*"
        matched_files = [
            f for f in root.glob(pattern) 
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        
        total = len(matched_files)
        tracks: List[Track] = []

        for i, f in enumerate(matched_files, start=1):
            if self._is_cancelled:
                break
            track = extract_track_info(str(f))
            tracks.append(track)
            self.track_loaded.emit(track)
            self.progress.emit(i, total)

        # Sort tracks by filename using natural alphanumeric sorting
        tracks.sort(key=lambda t: natural_sort_key(t.filename))
        self.scan_complete.emit(tracks)
