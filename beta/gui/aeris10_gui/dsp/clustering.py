"""DBSCAN clustering of detections in (range, velocity) space.

Lifted from ``GUI_V5.RadarProcessor.clustering`` (``GUI_V5.py:587-605``):
``DBSCAN(eps=100, min_samples=2)`` on ``[[range, velocity], ...]``; noise
label -1 discarded; cluster centre = mean of member points.  Change: returns a
dataclass with member indices (V5 returned dicts without indices) and
``min_samples=1`` is allowed so isolated detections are not lost.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np

try:
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:                 # pragma: no cover
    SKLEARN_AVAILABLE = False


@dataclass
class Cluster:
    center: np.ndarray
    members: List[int]
    size: int


def cluster_points(points: Sequence[Sequence[float]], *, eps: float = 100.0,
                   min_samples: int = 2) -> List[Cluster]:
    pts = np.asarray(points, dtype=float)
    if pts.size == 0:
        return []
    if pts.ndim != 2:
        raise ValueError("points must be an (n, k) array")
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required for clustering: pip install scikit-learn")
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit(pts).labels_
    out = []
    for label in sorted(set(labels.tolist())):
        if label == -1:
            continue
        idx = np.nonzero(labels == label)[0]
        out.append(Cluster(center=pts[idx].mean(axis=0), members=idx.tolist(), size=int(len(idx))))
    return out
