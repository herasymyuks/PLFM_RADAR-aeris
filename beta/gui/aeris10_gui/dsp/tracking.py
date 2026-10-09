"""Nearest-neighbour association + Kalman tracking.

Lifted from ``GUI_V5.RadarProcessor.association`` / ``tracking``
(``GUI_V5.py:607-670``): state ``[range, range_rate, velocity, velocity_rate]``,
constant-velocity ``F``, ``H`` selecting range and velocity, ``P *= 1000``,
``R = diag(10, 1)``, ``Q = 0.1 I``, association gate 500, stale after 5 s.
Changes: time is injected (``now``) for deterministic tests; the predict step
runs once per update for every track (V5 only predicted on association); the
gate and timeouts are constructor parameters; ``dt`` scales the velocity terms
of ``F``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np

try:
    from filterpy.kalman import KalmanFilter
    FILTERPY_AVAILABLE = True
except ImportError:                 # pragma: no cover
    FILTERPY_AVAILABLE = False


@dataclass
class Track:
    id: int
    kf: "KalmanFilter"
    last_update: float
    hits: int = 1
    misses: int = 0
    history: List[Tuple[float, float]] = field(default_factory=list)

    @property
    def range_m(self) -> float:
        return float(self.kf.x[0])

    @property
    def velocity_mps(self) -> float:
        return float(self.kf.x[2])

    @property
    def state(self) -> np.ndarray:
        return np.asarray(self.kf.x, dtype=float).reshape(-1)


def _make_filter(range_m: float, velocity: float, dt: float) -> "KalmanFilter":
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.x = np.array([range_m, 0.0, velocity, 0.0])
    kf.F = np.array([[1, dt, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, dt],
                     [0, 0, 0, 1]], dtype=float)
    kf.H = np.array([[1, 0, 0, 0],
                     [0, 0, 1, 0]], dtype=float)
    kf.P *= 1000.0
    kf.R = np.diag([10.0, 1.0])
    kf.Q = np.eye(4) * 0.1
    return kf


class Tracker:
    def __init__(self, *, gate: float = 500.0, stale_after: float = 5.0, dt: float = 1.0,
                 confirm_hits: int = 2):
        if not FILTERPY_AVAILABLE:
            raise ImportError("filterpy is required for tracking: pip install filterpy")
        self.gate = gate
        self.stale_after = stale_after
        self.dt = dt
        self.confirm_hits = confirm_hits
        self.tracks: dict[int, Track] = {}
        self._next_id = 0

    def update(self, detections: Sequence[Tuple[float, float]], now: float) -> List[Track]:
        """``detections`` = [(range_m, velocity_mps), ...].  Returns live tracks."""
        for t in self.tracks.values():
            t.kf.predict()
        unassigned = set(range(len(detections)))
        # greedy nearest-neighbour association (V5 logic, one detection per track)
        pairs = []
        for i, (r, v) in enumerate(detections):
            for tid, t in self.tracks.items():
                d = float(np.hypot(r - t.kf.x[0], v - t.kf.x[2]))
                if d < self.gate:
                    pairs.append((d, i, tid))
        pairs.sort()
        used_tracks = set()
        for d, i, tid in pairs:
            if i in unassigned and tid not in used_tracks:
                t = self.tracks[tid]
                t.kf.update(np.array(detections[i], dtype=float))
                t.last_update = now
                t.hits += 1
                t.misses = 0
                t.history.append((t.range_m, t.velocity_mps))
                unassigned.discard(i)
                used_tracks.add(tid)
        for tid, t in self.tracks.items():
            if tid not in used_tracks:
                t.misses += 1
        for i in sorted(unassigned):
            r, v = detections[i]
            tid = self._next_id
            self._next_id += 1
            self.tracks[tid] = Track(tid, _make_filter(r, v, self.dt), now, history=[(r, v)])
        stale = [tid for tid, t in self.tracks.items() if now - t.last_update > self.stale_after]
        for tid in stale:
            del self.tracks[tid]
        return list(self.tracks.values())

    def confirmed(self) -> List[Track]:
        return [t for t in self.tracks.values() if t.hits >= self.confirm_hits]
