"""Shared data classes.

``RadarSettings`` mirrors the firmware class of the same name
(``9_1_1_C_Cpp_Libraries/RadarSettings.h``) and the dataclass in
``GUI_V5.py:69-80``.  Default values are the firmware defaults
(``RadarSettings.cpp:8-20``), which are identical to the GUI_V5 defaults.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class RadarSettings:
    system_frequency: float = 10.0e9     # Hz
    chirp_duration_1: float = 30.0e-6    # s, long chirp
    chirp_duration_2: float = 0.5e-6     # s, short chirp
    chirps_per_position: int = 32
    freq_min: float = 10.0e6             # Hz
    freq_max: float = 30.0e6             # Hz
    prf1: float = 1000.0                 # Hz
    prf2: float = 2000.0                 # Hz
    max_distance: float = 50000.0        # m
    map_size: float = 50000.0            # m

    def as_dict(self) -> dict:
        return asdict(self)

    @property
    def wavelength(self) -> float:
        """Free-space wavelength at ``system_frequency`` (m)."""
        return 299_792_458.0 / self.system_frequency


@dataclass
class RadarTarget:
    """A detection or a track as shown in the GUI (GUI_V5.py:56-67)."""
    id: int
    range_m: float
    velocity_mps: float
    azimuth_deg: float = 0.0
    elevation_deg: float = 0.0
    snr_db: float = 0.0
    timestamp: float = 0.0
    track_id: int = -1
    range_bin: Optional[int] = None
    doppler_bin: Optional[int] = None


@dataclass
class GPSData:
    """GUI_V5.py:82-88; ``pitch`` is only carried by the binary GPSB frame."""
    latitude: float
    longitude: float
    altitude: float
    pitch: float = 0.0
    timestamp: float = 0.0


@dataclass
class SystemStatus:
    """Parsed ``getSystemStatusForGUI`` string (main.cpp:807-877)."""
    mode: str                                   # "NORMAL" | "EMERGENCY_STOP"
    last_error: Optional[int] = None
    error_count: Optional[int] = None
    imu_pitch: Optional[float] = None
    imu_roll: Optional[float] = None
    imu_yaw: Optional[float] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    altitude: Optional[float] = None
    lo_tx_locked: Optional[bool] = None
    lo_rx_locked: Optional[bool] = None
    temperatures: list = field(default_factory=list)   # T1..T8
    pa_avg_current: Optional[float] = None
    pa_enabled: Optional[int] = None
    beam_pos: Optional[int] = None              # firmware variable n (elevation index)
    azimuth: Optional[int] = None               # firmware variable y (azimuth index)
    chirp_count: Optional[int] = None           # firmware variable m
    unknown_fields: dict = field(default_factory=dict)
    raw: str = ""
