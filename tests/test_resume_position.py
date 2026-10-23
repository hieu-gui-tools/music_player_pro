"""Test that playback resume correctly preserves and continues from the saved position."""
import os
import sys
import wave
import struct
import math
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from music_player_pro.core.models import Track
from music_player_pro.core.db import Database
from music_player_pro.core.player import PlayerController


def create_sample_wav(file_path: Path, duration_sec: float = 30.0):
    sample_rate = 8000
    with wave.open(str(file_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        # 1-second sine wave repeated
        cycle = [int(10000 * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(sample_rate)]
        one_sec_bytes = struct.pack(f"<{sample_rate}h", *cycle)
        wav_file.writeframes(one_sec_bytes * int(duration_sec))


def test_resume_not_reset_to_zero():
    app = QApplication.instance() or QApplication([])

    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td)
        song = tmp_dir / "Lesson 10.wav"
        create_sample_wav(song, duration_sec=30.0)

        track = Track(
            path=str(song.resolve()),
            title="Lesson 10",
            duration_ms=30000
        )

        db_path = tmp_dir / "test_resume.db"
        db = Database(db_path)
        
        # Save memory at 13,000 ms (13 seconds)
        folder_path = str(tmp_dir.resolve())
        db.save_playback_memory("folder", folder_path, track.path, 13000)

        # Create PlayerController
        player = PlayerController(db)
        
        # Load source with auto_resume=True, auto_play=False
        player.set_source_and_queue("folder", folder_path, [track], auto_resume=True, auto_play=False)

        assert player.current_track is not None
        assert player.current_track.path == track.path
        assert player._pending_seek_ms == 13000 or player.player.position() == 13000

        # Verify save_current_state does NOT overwrite 13,000 ms with 0 ms
        player.save_current_state()
        mem = db.get_playback_memory("folder", folder_path)
        assert mem.last_position_ms == 13000, f"Expected 13000 ms, but got {mem.last_position_ms} ms!"
        print("✓ save_current_state correctly protected position from being overwritten with 0.")

        player.stop()
        del player
        db.close()

    print("✓ All position resume tests passed!")


def test_resume_auto_play_advances_from_saved():
    app = QApplication.instance() or QApplication([])

    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td)
        song = tmp_dir / "Lesson 10.wav"
        create_sample_wav(song, duration_sec=30.0)

        track = Track(
            path=str(song.resolve()),
            title="Lesson 10",
            duration_ms=30000
        )

        db_path = tmp_dir / "test_resume_play.db"
        db = Database(db_path)
        
        target_ms = 13000
        folder_path = str(tmp_dir.resolve())
        db.save_playback_memory("folder", folder_path, track.path, target_ms)

        player = PlayerController(db)
        
        positions = []
        player.position_changed.connect(lambda pos, dur: positions.append(pos))

        player.set_source_and_queue("folder", folder_path, [track], auto_resume=True, auto_play=True)

        # Allow event loop to process playback and seeking
        timer = QTimer(player)
        timer.setInterval(100)
        ticks = 0

        def check_progress():
            nonlocal ticks
            ticks += 1
            if player.player.position() >= target_ms or ticks > 25:
                timer.stop()
                app.quit()

        timer.timeout.connect(check_progress)
        timer.start()
        app.exec()

        final_pos = player.player.position()
        print(f"✓ Playback resumed and advanced to position: {final_pos} ms (target was {target_ms} ms)")
        assert final_pos >= target_ms - 200, f"Expected position >= {target_ms - 200}, but got {final_pos}"
        
        # Verify positions emitted to UI did not contain any pre-seek 0 values
        for p in positions:
            assert p >= target_ms - 500, f"UI received unexpected early position: {p} ms"

        player.stop()
        del player
        db.close()

    print("✓ Auto-play resume test passed!")


if __name__ == "__main__":
    test_resume_not_reset_to_zero()
    test_resume_auto_play_advances_from_saved()
