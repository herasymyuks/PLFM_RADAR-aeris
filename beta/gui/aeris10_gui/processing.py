"""Host-side processing: frame assembly -> power map -> CFAR -> clustering -> tracking.

Scaling assumptions (marked UNVERIFIED in the README; nothing in the packet or
firmware defines them):

* Range axis: cell ``r`` of ``n_range`` -> ``r * settings.max_distance / n_range``
  metres.  The RTL's 64 "range bins" are decimated matched-filter outputs
  (``radar_receiver_final.v:233-238``); their physical spacing is not
  documented, so the GUI maps them linearly onto ``max_distance``.
* Velocity axis: FFT bin ``k`` of ``n_doppler`` -> ``((k + N/2) mod N - N/2) *
  prf1 * lambda / (2 N)`` (natural FFT order, bins >= N/2 negative; standard
  pulse-Doppler relation, using ``prf1`` and ``system_frequency``).
* Azimuth/elevation of a detection are taken from the latest STM32 status
  (``Azimuth``/``BeamPos`` indices, ``protocol.status_text``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import numpy as np

from .dsp.cfar import Detection, cfar_detections
from .dsp.clustering import cluster_points
from .dsp.tracking import Track, Tracker
from .model import RadarSettings, RadarTarget, SystemStatus
from .protocol import fpga_packet as fp
from .protocol.bridge_frame import BridgeFrame
from .protocol.status_text import azimuth_index_to_degrees


class FrameAssembler:
    """Collect ``n_range * n_doppler`` packets into one complex frame (range-major)."""

    def __init__(self, n_range: int = fp.N_RANGE_BINS, n_doppler: int = fp.N_DOPPLER_BINS):
        self.n_range, self.n_doppler = n_range, n_doppler
        self.cells_per_frame = n_range * n_doppler
        self._i = np.zeros(self.cells_per_frame, dtype=np.int32)
        self._q = np.zeros(self.cells_per_frame, dtype=np.int32)
        self._det = np.zeros(self.cells_per_frame, dtype=bool)
        self._n = 0
        self.frames_completed = 0

    @property
    def fill(self) -> int:
        return self._n

    def reset(self) -> None:
        self._n = 0

    def feed(self, packets: Sequence[fp.FpgaPacket]):
        """Return a list of ``(iq_map, detection_map)`` tuples completed by these packets."""
        done = []
        for p in packets:
            self._i[self._n] = p.doppler_real
            self._q[self._n] = p.doppler_imag
            self._det[self._n] = p.detection
            self._n += 1
            if self._n == self.cells_per_frame:
                iq = (self._i.astype(np.float64) + 1j * self._q.astype(np.float64)).reshape(self.n_range, self.n_doppler)
                det = self._det.reshape(self.n_range, self.n_doppler).copy()
                done.append((iq, det))
                self._n = 0
                self.frames_completed += 1
        return done


@dataclass
class FrameResult:
    power: np.ndarray                 # (n_range, n_doppler) linear power, natural FFT order
    power_db_shifted: np.ndarray      # fftshift along Doppler axis, dB, for display
    fpga_detection_map: np.ndarray
    cfar_detections: List[Detection]
    targets: List[RadarTarget]        # clustered detections, physical units
    tracks: List[Track]
    status: Optional[SystemStatus] = None


class RadarPipeline:
    def __init__(self, settings: RadarSettings, *, n_range: int = fp.N_RANGE_BINS,
                 n_doppler: int = fp.N_DOPPLER_BINS, cfar_pfa: float = 1e-4,
                 cfar_guard=(1, 1), cfar_train=(4, 2), cluster_eps_bins: float = 1.5,
                 tracker: Optional[Tracker] = None):
        self.settings = settings
        self.n_range, self.n_doppler = n_range, n_doppler
        self.cfar_kwargs = dict(pfa=cfar_pfa, guard=cfar_guard, train=cfar_train)
        self.cluster_eps_bins = cluster_eps_bins
        self.tracker = tracker if tracker is not None else Tracker(gate=self.range_resolution * 4 + 1e-9)
        self.latest_status: Optional[SystemStatus] = None
        self.frame_index = 0

    # --- axes -------------------------------------------------------------------------
    @property
    def range_resolution(self) -> float:
        return self.settings.max_distance / self.n_range

    @property
    def velocity_resolution(self) -> float:
        return self.settings.prf1 * self.settings.wavelength / (2.0 * self.n_doppler)

    def range_axis(self) -> np.ndarray:
        return np.arange(self.n_range) * self.range_resolution

    def velocity_axis_shifted(self) -> np.ndarray:
        k = np.arange(self.n_doppler) - self.n_doppler // 2
        return k * self.velocity_resolution

    def bin_to_velocity(self, k: int) -> float:
        n = self.n_doppler
        return (((k + n // 2) % n) - n // 2) * self.velocity_resolution

    def bin_to_range(self, r: int) -> float:
        return r * self.range_resolution

    # --- processing ---------------------------------------------------------------------
    def process_frame(self, iq: np.ndarray, det_map: Optional[np.ndarray] = None,
                      now: float = 0.0) -> FrameResult:
        """Raw-RTL path: complex I/Q cells (``FrameAssembler``)."""
        return self.process_power(np.abs(iq) ** 2, det_map, now)

    def process_bridge_frame(self, frame: BridgeFrame, now: float = 0.0) -> FrameResult:
        """Option-B path: uint8 log-magnitude map + FPGA detection list; az/el come from the frame header."""
        power, det_map = bridge_frame_to_power(frame)
        return self.process_power(power, det_map, now, azimuth_index=frame.azimuth, elevation_index=frame.elevation)

    def process_power(self, power: np.ndarray, det_map: Optional[np.ndarray] = None, now: float = 0.0, *,
                      azimuth_index: Optional[int] = None, elevation_index: Optional[int] = None) -> FrameResult:
        self.frame_index += 1
        power = np.asarray(power, dtype=np.float64)
        if power.shape != (self.n_range, self.n_doppler):
            raise ValueError(f"power map shape {power.shape} != ({self.n_range}, {self.n_doppler})")
        dets = cfar_detections(power, **self.cfar_kwargs)
        # exclude the zero-Doppler clutter notch (bins 0, 1, N-1) from target reports
        dets = [d for d in dets if d.doppler_bin not in (0, 1, self.n_doppler - 1)]
        az = el = 0.0
        if azimuth_index is None and self.latest_status is not None:
            azimuth_index = self.latest_status.azimuth
        if elevation_index is None and self.latest_status is not None:
            elevation_index = self.latest_status.beam_pos
        if azimuth_index:
            az = azimuth_index_to_degrees(azimuth_index)
        if elevation_index:
            el = float(elevation_index)                        # index, no angle table in firmware
        targets: List[RadarTarget] = []
        if dets:
            pts = [(d.range_bin, (d.doppler_bin + self.n_doppler // 2) % self.n_doppler) for d in dets]
            for ci, c in enumerate(cluster_points(pts, eps=self.cluster_eps_bins, min_samples=1)):
                best = max(c.members, key=lambda m: dets[m].power)
                d = dets[best]
                targets.append(RadarTarget(ci, self.bin_to_range(d.range_bin), self.bin_to_velocity(d.doppler_bin),
                                           az, el, d.snr_db, now, range_bin=d.range_bin, doppler_bin=d.doppler_bin))
        tracks = self.tracker.update([(t.range_m, t.velocity_mps) for t in targets], now)
        for t in targets:
            best = min(tracks, key=lambda tr: np.hypot(tr.range_m - t.range_m, tr.velocity_mps - t.velocity_mps), default=None)
            if best is not None:
                t.track_id = best.id
        shifted = np.fft.fftshift(power, axes=1)
        power_db = 10.0 * np.log10(shifted + 1.0)
        if det_map is None:
            det_map = np.zeros_like(power, dtype=bool)
        return FrameResult(power, power_db, det_map, dets, targets, tracks, self.latest_status)


LOGMAG_DB_PER_LSB = 20.0 * np.log10(2.0) / 8.0        # 0.7526 dB of |I|+|Q| per uint8 step


def bridge_frame_to_power(frame: BridgeFrame):
    """uint8 8*log2(|I|+|Q|) -> linear power proxy (|I|+|Q|)^2 = 2**(u8/4), plus the FPGA detection map."""
    lm = np.frombuffer(bytes(frame.magnitude), dtype=np.uint8).astype(np.float64)
    if lm.size != frame.n_range * frame.n_doppler:
        raise ValueError("bridge frame magnitude length does not match n_range*n_doppler")
    power = np.exp2(lm / 4.0).reshape(frame.n_range, frame.n_doppler)
    power[lm.reshape(frame.n_range, frame.n_doppler) == 0] = 0.0
    det = np.zeros((frame.n_range, frame.n_doppler), dtype=bool)
    for r, d, _m in frame.detections:
        if r < frame.n_range and d < frame.n_doppler:
            det[r, d] = True
    return power, det
