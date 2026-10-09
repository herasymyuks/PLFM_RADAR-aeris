"""Radar scene simulator emitting FPGA packets and STM32 status strings.

Refactored from ``GUI_V6_Demo.SimulatedRadarProcessor`` (``GUI_V6_Demo.py:61-231``).
Kept: the five-target scene with drift/reflection, noise floor, zero-Doppler
clutter, gaussian target blobs, range-dependent gain.  Changed:

* Output is a complex (I/Q) map of **64 x 32** cells (RTL geometry,
  ``radar_receiver_final.v:291-293``) instead of a 1024 x 32 power map, and it
  is serialised into 2048 FPGA packets per frame (``protocol.fpga_packet``),
  range-major (``doppler_processor.v:244-266``), so the GUI consumes the same
  parser path it would use for hardware.
* The detection bit per cell is ``|I| + |Q| > 10000`` -- the placeholder
  threshold in ``radar_system_top.v:318``.
* Detections are **not** drawn from the truth list (V6 did
  ``random.random() < snr/35``); the host CFAR finds them.
* A status string in the firmware format (``protocol.status_text``) is emitted
  per frame with advancing ``Azimuth``/``BeamPos``/``ChirpCount`` indices.
* Target velocities are scaled to fit the unambiguous Doppler span implied by
  ``DEMO_SETTINGS`` (prf1 = 10 kHz, 10 GHz -> +-75 m/s); V6 used +-100 m/s
  with no PRF link.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional

import numpy as np

from ..model import RadarSettings, RadarTarget
from ..protocol import fpga_packet as fp
from ..protocol.status_text import format_status_line, FIRMWARE_Y_MAX

# Demo settings: firmware defaults except prf1 (10 kHz, within the firmware's
# 100..10000 Hz validation range) and max_distance/map_size (5 km, V6 scene).
DEMO_SETTINGS = RadarSettings(prf1=10000.0, prf2=10000.0, max_distance=5000.0, map_size=5000.0)

TOP_LEVEL_DETECTION_THRESHOLD = 10000     # radar_system_top.v:318, |I|+|Q|


@dataclass
class SimTarget:
    id: int
    range_m: float
    velocity_mps: float
    azimuth_deg: float
    elevation_deg: float
    snr_db: float
    range_drift: float
    azimuth_drift: float
    velocity_drift: float


def v6_targets() -> List[SimTarget]:
    """GUI_V6_Demo.py:71-129, velocities scaled x0.75 to stay inside +-75 m/s."""
    raw = [
        (1, 2500, -80, 45, 5, 25, -0.8, 0.15, 0.1),
        (2, 800, 15, -30, 0, 18, 0.3, -0.1, -0.05),
        (3, 1500, 0, 10, 2, 22, 0, 0.05, 0),
        (4, 3500, 50, -15, 3, 15, 0.5, -0.2, -0.3),
        (5, 500, -20, 60, 1, 30, -0.2, 0.3, 0.2),
    ]
    return [SimTarget(i, r, v * 0.75, az, el, snr, rd, ad, vd * 0.75) for (i, r, v, az, el, snr, rd, ad, vd) in raw]


@dataclass
class SimFrame:
    index: int
    iq: np.ndarray                    # complex128 (n_range, n_doppler), int16-quantised values
    truth: List[RadarTarget]
    fpga_bytes: bytes                 # n_range*n_doppler packets of 35 bytes
    status_bytes: bytes               # firmware-format status string
    beam_pos: int
    azimuth_index: int


class RadarSimulator:
    def __init__(self, settings: Optional[RadarSettings] = None, *, n_range: int = fp.N_RANGE_BINS,
                 n_doppler: int = fp.N_DOPPLER_BINS, seed: Optional[int] = 1,
                 noise_sigma: float = 400.0, clutter_db: float = 12.0, max_range_m: Optional[float] = None):
        self.settings = replace(settings) if settings else replace(DEMO_SETTINGS)
        self.n_range, self.n_doppler = n_range, n_doppler
        self.rng = np.random.default_rng(seed)
        self.noise_sigma = noise_sigma
        self.clutter_db = clutter_db
        self.max_range_m = max_range_m if max_range_m is not None else self.settings.max_distance
        self.targets = v6_targets()
        self.frame_count = 0
        self.azimuth_index = 1          # firmware y, 1..y_max
        self.beam_pos = 1               # firmware n
        self.chirp_count = 0            # firmware m
        self.y_max = FIRMWARE_Y_MAX
        self.gps = (41.9028, 12.4964, 50.0)   # GUI_V5.py:905 default position
        self.imu = (1.5, -0.5, 0.0)

    # --- scaling shared with processing.RadarPipeline -------------------------------------
    @property
    def velocity_resolution(self) -> float:
        """m/s per Doppler bin: prf * lambda / (2 N)."""
        return self.settings.prf1 * self.settings.wavelength / (2.0 * self.n_doppler)

    @property
    def unambiguous_velocity(self) -> float:
        return self.settings.prf1 * self.settings.wavelength / 2.0

    @property
    def range_resolution(self) -> float:
        return self.max_range_m / self.n_range

    def velocity_to_bin(self, v: float) -> int:
        return int(round(v / self.velocity_resolution)) % self.n_doppler

    def range_to_bin(self, r: float) -> int:
        return int(min(max(round(r / self.range_resolution), 0), self.n_range - 1))

    # --- scene -------------------------------------------------------------------------
    def _advance_targets(self) -> None:
        vmax = 0.95 * self.unambiguous_velocity / 2.0
        for t in self.targets:
            t.range_m += t.range_drift
            t.azimuth_deg += t.azimuth_drift
            t.velocity_mps += t.velocity_drift
            if t.range_m < 0.02 * self.max_range_m:
                t.range_m = 0.02 * self.max_range_m
                t.range_drift *= -1
            elif t.range_m > 0.96 * self.max_range_m:
                t.range_m = 0.96 * self.max_range_m
                t.range_drift *= -1
            if t.azimuth_deg < -90:
                t.azimuth_deg, t.azimuth_drift = -90, -t.azimuth_drift
            elif t.azimuth_deg > 90:
                t.azimuth_deg, t.azimuth_drift = 90, -t.azimuth_drift
            if t.velocity_mps < -vmax:
                t.velocity_mps, t.velocity_drift = -vmax, -t.velocity_drift
            elif t.velocity_mps > vmax:
                t.velocity_mps, t.velocity_drift = vmax, -t.velocity_drift

    def _scene_iq(self) -> np.ndarray:
        n_r, n_d = self.n_range, self.n_doppler
        sig = self.noise_sigma
        iq = (self.rng.normal(0, sig, (n_r, n_d)) + 1j * self.rng.normal(0, sig, (n_r, n_d))) / np.sqrt(2)
        # clutter at zero Doppler (bins 0, 1, N-1)
        clutter_amp = sig * 10 ** (self.clutter_db / 20)
        for d in (0, 1, n_d - 1):
            iq[:, d] += clutter_amp * (0.8 + 0.4 * self.rng.random(n_r)) * np.exp(1j * self.rng.uniform(0, 2 * np.pi, n_r))
        for t in self.targets:
            rb, db = self.range_to_bin(t.range_m), self.velocity_to_bin(t.velocity_mps)
            amp = sig * 10 ** (t.snr_db / 20)
            phase = self.rng.uniform(0, 2 * np.pi)
            for dr in (-1, 0, 1):
                for dd in (-1, 0, 1):
                    rr, ddd = rb + dr, (db + dd) % n_d
                    if 0 <= rr < n_r:
                        dist = np.hypot(dr, dd)
                        iq[rr, ddd] += amp * np.exp(-dist / 0.8) * np.exp(1j * phase)
        # range-dependent gain (V6: linspace(1, 0.3))
        iq *= np.linspace(1.0, 0.3, n_r)[:, None]
        re = np.clip(np.round(iq.real), -32768, 32767)
        im = np.clip(np.round(iq.imag), -32768, 32767)
        return re + 1j * im

    def _truth(self, ts: float) -> List[RadarTarget]:
        return [RadarTarget(t.id, t.range_m, t.velocity_mps, t.azimuth_deg, t.elevation_deg, t.snr_db, ts,
                            range_bin=self.range_to_bin(t.range_m), doppler_bin=self.velocity_to_bin(t.velocity_mps))
                for t in self.targets]

    def encode_frame(self, iq: np.ndarray) -> bytes:
        """Serialise a complex map range-major into 35-byte RTL packets."""
        out = bytearray()
        for r in range(iq.shape[0]):
            for d in range(iq.shape[1]):
                i, q = int(iq[r, d].real), int(iq[r, d].imag)
                det = (abs(i) + abs(q)) > TOP_LEVEL_DETECTION_THRESHOLD
                out += fp.encode_cell(i, q, det)
        return bytes(out)

    def status_string(self) -> str:
        return format_status_line(imu=self.imu, gps=self.gps[:2], altitude=self.gps[2],
                                  temperatures=tuple(35.0 + i for i in range(8)),
                                  beam_pos=self.beam_pos, azimuth=self.azimuth_index,
                                  chirp_count=self.chirp_count)

    def next_frame(self, timestamp: float = 0.0) -> SimFrame:
        self.frame_count += 1
        self._advance_targets()
        iq = self._scene_iq()
        frame = SimFrame(self.frame_count, iq, self._truth(timestamp), self.encode_frame(iq),
                         self.status_string().encode("ascii"), self.beam_pos, self.azimuth_index)
        # advance firmware-style counters: one azimuth step per frame
        self.chirp_count = (self.chirp_count + self.settings.chirps_per_position) % 1_000_000
        self.azimuth_index = self.azimuth_index % self.y_max + 1
        return frame
