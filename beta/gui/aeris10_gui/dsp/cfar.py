"""Cell-averaging CFAR (CA-CFAR) for 1-D range profiles and 2-D range-Doppler maps.

Square-law detector assumption: the input is power (|x|^2).  For N training
cells and a desired false-alarm probability P_fa the threshold multiplier is
``alpha = N * (P_fa**(-1/N) - 1)`` (Richards, *Fundamentals of Radar Signal
Processing*, eq. for CA-CFAR with exponential noise).  Implemented with
cumulative sums / integral images so the cost is independent of window size.
Edges are handled by edge-padding the input (the window is always full).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


def cfar_scale_factor(num_train: int, pfa: float) -> float:
    if num_train <= 0:
        raise ValueError("num_train must be > 0")
    if not 0 < pfa < 1:
        raise ValueError("pfa must be in (0, 1)")
    return num_train * (pfa ** (-1.0 / num_train) - 1.0)


def _window_sum_1d(x: np.ndarray, half: int) -> np.ndarray:
    """Sum over [i-half, i+half] with edge padding."""
    if half == 0:
        return x.copy()
    xp = np.pad(x, half, mode="edge")
    cs = np.concatenate(([0.0], np.cumsum(xp)))
    n = len(x)
    return cs[2 * half + 1:2 * half + 1 + n] - cs[0:n]


def ca_cfar_1d(power: np.ndarray, *, guard: int = 2, train: int = 8,
               pfa: float = 1e-3, scale: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Return ``(mask, threshold)`` for a 1-D power vector."""
    x = np.asarray(power, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("ca_cfar_1d expects a 1-D array")
    if train <= 0 or guard < 0:
        raise ValueError("train must be > 0 and guard >= 0")
    n_train = 2 * train
    alpha = cfar_scale_factor(n_train, pfa) if scale is None else scale
    outer = _window_sum_1d(x, guard + train)
    inner = _window_sum_1d(x, guard)
    noise = (outer - inner) / n_train
    threshold = alpha * noise
    return x > threshold, threshold


def _window_sum_2d(x: np.ndarray, hr: int, hd: int) -> np.ndarray:
    xp = np.pad(x, ((hr, hr), (hd, hd)), mode="edge")
    ii = np.zeros((xp.shape[0] + 1, xp.shape[1] + 1))
    ii[1:, 1:] = xp.cumsum(0).cumsum(1)
    n0, n1 = x.shape
    a = 2 * hr + 1
    b = 2 * hd + 1
    return ii[a:a + n0, b:b + n1] - ii[0:n0, b:b + n1] - ii[a:a + n0, 0:n1] + ii[0:n0, 0:n1]


def ca_cfar_2d(power: np.ndarray, *, guard: Tuple[int, int] = (1, 1),
               train: Tuple[int, int] = (4, 2), pfa: float = 1e-4,
               scale: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
    """2-D CA-CFAR on a (range, Doppler) power map.  Returns ``(mask, threshold)``.

    ``guard``/``train`` are half-widths per axis.  Training cells are the
    rectangular ring between the guard window and the outer window.
    """
    x = np.asarray(power, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("ca_cfar_2d expects a 2-D array")
    gr, gd = guard
    tr, td = train
    if tr <= 0 or td <= 0 or gr < 0 or gd < 0:
        raise ValueError("train half-widths must be > 0 and guard >= 0")
    n_outer = (2 * (gr + tr) + 1) * (2 * (gd + td) + 1)
    n_inner = (2 * gr + 1) * (2 * gd + 1)
    n_train = n_outer - n_inner
    alpha = cfar_scale_factor(n_train, pfa) if scale is None else scale
    noise = (_window_sum_2d(x, gr + tr, gd + td) - _window_sum_2d(x, gr, gd)) / n_train
    threshold = alpha * noise
    return x > threshold, threshold


@dataclass
class Detection:
    range_bin: int
    doppler_bin: int
    power: float
    threshold: float

    @property
    def snr_db(self) -> float:
        """Power over the local CFAR noise estimate (threshold/alpha is not stored; use threshold)."""
        return 10.0 * np.log10(max(self.power, 1e-30) / max(self.threshold, 1e-30))


def local_maxima(power: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Keep only mask cells that are >= all 8 neighbours (suppresses blobs)."""
    xp = np.pad(power, 1, mode="constant", constant_values=-np.inf)
    out = mask.copy()
    for dr in (-1, 0, 1):
        for dd in (-1, 0, 1):
            if dr == 0 and dd == 0:
                continue
            nb = xp[1 + dr:1 + dr + power.shape[0], 1 + dd:1 + dd + power.shape[1]]
            out &= power >= nb
    return out


def cfar_detections(power: np.ndarray, *, peaks_only: bool = True, **cfar_kwargs) -> List[Detection]:
    """Run :func:`ca_cfar_2d` and return a list of :class:`Detection`."""
    mask, thr = ca_cfar_2d(power, **cfar_kwargs)
    if peaks_only:
        mask = local_maxima(np.asarray(power, float), mask)
    rr, dd = np.nonzero(mask)
    return [Detection(int(r), int(d), float(power[r, d]), float(thr[r, d])) for r, d in zip(rr, dd)]
