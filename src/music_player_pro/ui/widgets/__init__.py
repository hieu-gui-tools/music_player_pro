"""Widgets package."""
from .seek_slider import SeekSlider
from .volume_slider import VolumeWidget
from .track_table import TrackTable
from .sidebar import Sidebar
from .header_banner import HeaderBanner
from .player_bar import PlayerBar
from .settings_dialog import SettingsDialog

__all__ = [
    "SeekSlider",
    "VolumeWidget",
    "TrackTable",
    "Sidebar",
    "HeaderBanner",
    "PlayerBar",
    "SettingsDialog",
]
