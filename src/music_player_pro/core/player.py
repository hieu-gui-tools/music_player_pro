"""Audio player controller managing QMediaPlayer, queue, shuffle/repeat, and resume memory."""
import random
from pathlib import Path
from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from .models import Track, RepeatMode, SourceType, PlaybackMemory
from .db import Database


class PlayerController(QObject):
    # Signals for UI updates
    track_changed = Signal(object)             # Track or None
    playback_state_changed = Signal(bool)      # True if playing, False if paused/stopped
    position_changed = Signal(int, int)        # position_ms, duration_ms
    duration_changed = Signal(int)             # duration_ms
    volume_changed = Signal(float)             # 0.0 to 1.0
    queue_updated = Signal()                   # Queue changed
    mode_changed = Signal(str, bool)           # repeat_mode ("off","all","one"), shuffle (bool)
    playback_resumed = Signal(str, int)        # track_title, position_ms

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        
        # Audio Player setup
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)

        # Queue and state
        self.tracks: List[Track] = []
        self.current_index: int = -1
        self.shuffle_history: List[int] = []
        self.repeat_mode: RepeatMode = RepeatMode.OFF
        self.is_shuffle: bool = False
        
        # Current active source (folder or playlist)
        self.active_source_type: Optional[str] = None
        self.active_source_id: Optional[str] = None
        
        # Target resume position after loading media
        self._target_seek_ms: Optional[int] = None
        self._seek_applied: bool = True
        self._last_saved_position_ms: int = 0

        # Periodic timer to save playback position to DB every 1.5s
        self.save_timer = QTimer(self)
        self.save_timer.setInterval(1500)
        self.save_timer.timeout.connect(self._auto_save_state)

        # Wire QtMultimedia signals
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)

        # Restore volume from DB or default 0.75
        saved_vol = self.db.get_setting("volume", "0.75")
        try:
            vol = float(saved_vol)
        except ValueError:
            vol = 0.75
        self.set_volume(vol)

    @property
    def _pending_seek_ms(self) -> Optional[int]:
        return self._target_seek_ms if not self._seek_applied else None

    @_pending_seek_ms.setter
    def _pending_seek_ms(self, val: Optional[int]):
        self._target_seek_ms = val
        self._seek_applied = (val is None or val <= 0)

    # --- Source & Queue Management ---
    def set_source_and_queue(self, source_type: str, source_id: str, tracks: List[Track], auto_resume: bool = True, auto_play: bool = False):
        """Set the current active folder/playlist and its track list.
        If auto_resume is True, checks DB for saved track & position and restores it.
        """
        # Save previous state if any
        self.save_current_state()

        self.active_source_type = source_type
        self.active_source_id = str(source_id)
        self.tracks = list(tracks)
        self.shuffle_history.clear()
        self.queue_updated.emit()

        if not self.tracks:
            self.stop()
            self.current_index = -1
            self.track_changed.emit(None)
            return

        # Check saved playback memory for this source
        memory = self.db.get_playback_memory(source_type, str(source_id))
        target_index = -1
        target_pos_ms = 0

        if memory and memory.last_track_path:
            norm_saved = Path(memory.last_track_path).resolve()
            for idx, trk in enumerate(self.tracks):
                if Path(trk.path).resolve() == norm_saved:
                    target_index = idx
                    target_pos_ms = memory.last_position_ms
                    break

        if target_index >= 0:
            # We found the saved track!
            self.current_index = target_index
            self._last_saved_position_ms = target_pos_ms
            self._load_track_at_index(self.current_index, seek_pos_ms=target_pos_ms, auto_play=auto_play)
            if target_pos_ms > 0:
                self.position_changed.emit(target_pos_ms, self.tracks[target_index].duration_ms)
            self.playback_resumed.emit(self.tracks[target_index].filename, target_pos_ms)
        else:
            # Default to first track if not found
            self.current_index = 0
            self._last_saved_position_ms = 0
            self._load_track_at_index(0, seek_pos_ms=0, auto_play=auto_play)

    def _load_track_at_index(self, index: int, seek_pos_ms: int = 0, auto_play: bool = False):
        if not (0 <= index < len(self.tracks)):
            return

        self.current_index = index
        track = self.tracks[index]
        self._target_seek_ms = seek_pos_ms if seek_pos_ms > 0 else None
        self._seek_applied = (seek_pos_ms <= 0)

        file_url = QUrl.fromLocalFile(track.path)
        self.player.setSource(file_url)
        self.track_changed.emit(track)

        if auto_play:
            self.play()

    # --- Playback Controls ---
    def play(self):
        if self.current_index == -1 and self.tracks:
            self._load_track_at_index(0, auto_play=True)
            return

        if self._target_seek_ms is not None and not self._seek_applied and self.player.isSeekable():
            dur = self.player.duration()
            target = min(self._target_seek_ms, dur) if dur > 0 else self._target_seek_ms
            self.player.setPosition(target)

        self.player.play()

    def pause(self):
        self.player.pause()
        self.save_current_state()

    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def stop(self):
        self.save_current_state()
        self.player.stop()

    def play_track_at_index(self, index: int, seek_pos_ms: int = 0):
        if 0 <= index < len(self.tracks):
            self.save_current_state()
            self._load_track_at_index(index, seek_pos_ms=seek_pos_ms, auto_play=True)

    def play_track_by_path(self, track_path: str):
        norm = Path(track_path).resolve()
        for idx, trk in enumerate(self.tracks):
            if Path(trk.path).resolve() == norm:
                self.play_track_at_index(idx)
                break

    def next_track(self):
        if not self.tracks:
            return
        
        self.save_current_state()

        if self.is_shuffle and len(self.tracks) > 1:
            next_idx = self._get_random_next_index()
        else:
            next_idx = self.current_index + 1
            if next_idx >= len(self.tracks):
                if self.repeat_mode == RepeatMode.ALL:
                    next_idx = 0
                else:
                    self.stop()
                    return

        self._load_track_at_index(next_idx, seek_pos_ms=0, auto_play=True)

    def previous_track(self):
        if not self.tracks:
            return
        
        # If current track has played for more than 3 seconds, restart it first
        if self.player.position() > 3000:
            self.seek(0)
            return

        self.save_current_state()

        if self.is_shuffle and len(self.shuffle_history) > 1:
            # Pop current and get previous
            self.shuffle_history.pop()
            prev_idx = self.shuffle_history[-1]
            self._load_track_at_index(prev_idx, seek_pos_ms=0, auto_play=True)
            return

        prev_idx = self.current_index - 1
        if prev_idx < 0:
            prev_idx = len(self.tracks) - 1 if self.repeat_mode == RepeatMode.ALL else 0

        self._load_track_at_index(prev_idx, seek_pos_ms=0, auto_play=True)

    def seek(self, position_ms: int):
        self._target_seek_ms = None
        self._seek_applied = True
        self.player.setPosition(position_ms)
        self._last_saved_position_ms = position_ms
        self.save_current_state()

    def set_volume(self, volume: float):
        """Volume between 0.0 and 1.0"""
        vol = max(0.0, min(1.0, volume))
        self.audio_output.setVolume(vol)
        self.volume_changed.emit(vol)
        self.db.set_setting("volume", str(vol))

    def get_volume(self) -> float:
        return self.audio_output.volume()

    def set_muted(self, muted: bool):
        self.audio_output.setMuted(muted)

    def is_muted(self) -> bool:
        return self.audio_output.isMuted()

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.mode_changed.emit(self.repeat_mode.value, self.is_shuffle)

    def cycle_repeat_mode(self):
        if self.repeat_mode == RepeatMode.OFF:
            self.repeat_mode = RepeatMode.ALL
        elif self.repeat_mode == RepeatMode.ALL:
            self.repeat_mode = RepeatMode.ONE
        else:
            self.repeat_mode = RepeatMode.OFF
        self.mode_changed.emit(self.repeat_mode.value, self.is_shuffle)

    def _get_random_next_index(self) -> int:
        indices = [i for i in range(len(self.tracks)) if i != self.current_index]
        if not indices:
            return 0
        pick = random.choice(indices)
        self.shuffle_history.append(pick)
        return pick

    def _apply_pending_seek(self):
        if self._target_seek_ms is not None and not self._seek_applied:
            if self.player.isSeekable():
                target = self._target_seek_ms
                dur = self.player.duration()
                if dur > 0:
                    target = min(target, dur)
                self.player.setPosition(target)

    # --- Signal Handlers ---
    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState):
        is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.playback_state_changed.emit(is_playing)
        if is_playing:
            self.save_timer.start()
        else:
            self.save_timer.stop()

    def _on_position_changed(self, pos_ms: int):
        duration = self.player.duration()

        if self._target_seek_ms is not None and not self._seek_applied:
            if pos_ms < (self._target_seek_ms - 500):
                if self.player.isSeekable():
                    self.player.setPosition(self._target_seek_ms)
                return
            else:
                self._seek_applied = True
                self._last_saved_position_ms = pos_ms
                self._target_seek_ms = None

        self.position_changed.emit(pos_ms, duration)

    def _on_duration_changed(self, dur_ms: int):
        self.duration_changed.emit(dur_ms)
        if dur_ms > 0:
            self._apply_pending_seek()

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            self._apply_pending_seek()
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._handle_end_of_media()

    def _handle_end_of_media(self):
        if self.repeat_mode == RepeatMode.ONE:
            self.seek(0)
            self.play()
        else:
            self.next_track()

    # --- State Saving & Memory ---
    def _auto_save_state(self):
        if self.is_playing() and self.current_track:
            # Don't overwrite if seek has not yet been applied
            if self._target_seek_ms is not None and not self._seek_applied:
                return

            pos = self.player.position()
            # Only save to DB if position changed meaningfully
            if abs(pos - self._last_saved_position_ms) >= 1000:
                self._last_saved_position_ms = pos
                if self.active_source_type and self.active_source_id:
                    self.db.save_playback_memory(
                        source_type=self.active_source_type,
                        source_id=self.active_source_id,
                        last_track_path=self.current_track.path,
                        last_position_ms=pos
                    )

    def save_current_state(self):
        if self.active_source_type and self.active_source_id and self.current_track:
            # If seek hasn't completed yet, preserve target seek
            if self._target_seek_ms is not None and not self._seek_applied:
                pos = self._target_seek_ms
            else:
                pos = self.player.position()
                if pos <= 0 and self._last_saved_position_ms > 0 and self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                    pos = self._last_saved_position_ms

            if pos > 0:
                self._last_saved_position_ms = pos
                self.db.save_playback_memory(
                    source_type=self.active_source_type,
                    source_id=self.active_source_id,
                    last_track_path=self.current_track.path,
                    last_position_ms=pos
                )

    @property
    def current_track(self) -> Optional[Track]:
        if 0 <= self.current_index < len(self.tracks):
            return self.tracks[self.current_index]
        return None

    def is_playing(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def is_paused_or_stopped(self) -> bool:
        return self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState
