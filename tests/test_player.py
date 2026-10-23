"""Integration tests for Music Player Pro."""
import os
import wave
import struct
import math
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from music_player_pro.core.models import Track, SourceType
from music_player_pro.core.db import Database
from music_player_pro.core.scanner import scan_directory, extract_track_info
from music_player_pro.core.player import PlayerController


def create_sample_wav(file_path: Path, duration_sec: float = 3.0, freq: float = 440.0):
    """Generate a clean synthetic WAV file for testing."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration_sec)
    with wave.open(str(file_path), "w") as wav_file:
        wav_file.setnchannels(1)        # Mono
        wav_file.setsampwidth(2)       # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
            data = struct.pack("<h", value)
            wav_file.writeframes(data)


def test_full_workflow(tmp_path: Path):
    app = QApplication.instance() or QApplication([])

    # 1. Prepare sample audio directory
    music_dir = tmp_path / "TestMusicFolder"
    music_dir.mkdir(parents=True, exist_ok=True)
    
    song1 = music_dir / "Song_01.wav"
    song2 = music_dir / "Song_02.wav"
    create_sample_wav(song1, duration_sec=5.0, freq=440.0)
    create_sample_wav(song2, duration_sec=10.0, freq=880.0)

    # 2. Test Scanner (Sorted naturally by filename)
    tracks = scan_directory(str(music_dir))
    assert len(tracks) == 2, f"Expected 2 tracks, got {len(tracks)}"
    assert tracks[0].filename == "Song_01.wav"
    assert tracks[1].filename == "Song_02.wav"
    print("✓ Audio scanner extracted and sorted tracks by filename successfully.")

    # 3. Test Database & Playback State for Folder
    db_file = tmp_path / "test_library.db"
    db = Database(db_file)
    db.add_folder(str(music_dir), "My Test Folder")
    
    # Save folder playback state (e.g. at song2, position 3500ms)
    db.save_playback_memory("folder", str(music_dir.resolve()), str(song2.resolve()), 3500)
    
    mem_folder = db.get_playback_memory("folder", str(music_dir.resolve()))
    assert mem_folder is not None
    assert mem_folder.last_track_path == str(song2.resolve())
    assert mem_folder.last_position_ms == 3500
    print("✓ Folder playback memory saved and verified.")

    # 4. Test Playlists & Playback State for Playlist
    pid = db.create_playlist("Chill Wave")
    db.add_tracks_to_playlist(pid, [str(song1), str(song2)])
    playlist_tracks = db.get_playlist_track_paths(pid)
    assert len(playlist_tracks) == 2
    
    # Save playlist playback state (e.g. at song1, position 1800ms)
    db.save_playback_memory("playlist", str(pid), str(song1.resolve()), 1800)
    
    mem_playlist = db.get_playback_memory("playlist", str(pid))
    assert mem_playlist is not None
    assert mem_playlist.last_track_path == str(song1.resolve())
    assert mem_playlist.last_position_ms == 1800
    print("✓ Playlist playback memory saved and verified.")

    # 5. Verify folder and playlist memories are independent
    mem_folder_check = db.get_playback_memory("folder", str(music_dir.resolve()))
    assert mem_folder_check.last_position_ms == 3500
    assert mem_playlist.last_position_ms == 1800
    print("✓ Per-folder and per-playlist playback positions remain independent and intact.")

    # 6. Test PlayerController loading with resume
    player = PlayerController(db)
    
    # Switch to folder
    player.set_source_and_queue("folder", str(music_dir.resolve()), tracks, auto_resume=True)
    assert player.current_track is not None
    assert Path(player.current_track.path).resolve() == song2.resolve()
    print("✓ PlayerController successfully auto-restored track for folder.")

    # Switch to playlist
    pl_track_objs = [extract_track_info(p) for p in playlist_tracks]
    player.set_source_and_queue("playlist", str(pid), pl_track_objs, auto_resume=True)
    assert player.current_track is not None
    assert Path(player.current_track.path).resolve() == song1.resolve()
    print("✓ PlayerController successfully auto-restored track for playlist.")

    player.stop()
    del player
    db.close()

    print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY! 🎉")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_full_workflow(Path(td))
