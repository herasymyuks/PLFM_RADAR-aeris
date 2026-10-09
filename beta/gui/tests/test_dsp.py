import numpy as np
import pytest

from aeris10_gui.dsp.cfar import ca_cfar_1d, ca_cfar_2d, cfar_detections, cfar_scale_factor, local_maxima
from aeris10_gui.dsp.clustering import cluster_points
from aeris10_gui.dsp.tracking import Tracker


def test_scale_factor_textbook_value():
    # N=16, Pfa=1e-3 -> 16*(1000^(1/16)-1) ~= 8.69
    assert cfar_scale_factor(16, 1e-3) == pytest.approx(16 * (1000 ** (1 / 16) - 1))


def test_cfar_1d_detects_targets_in_noise():
    rng = np.random.default_rng(0)
    n = 512
    power = rng.exponential(1.0, n)              # square-law noise, unit mean
    for idx, amp in [(100, 40.0), (300, 60.0)]:
        power[idx] += amp
    mask, thr = ca_cfar_1d(power, guard=2, train=8, pfa=1e-4)
    assert mask[100] and mask[300]
    false_alarms = mask.sum() - 2
    assert false_alarms <= 3                     # expected 512*1e-4 ~ 0.05, allow slack
    assert thr.shape == power.shape and np.all(thr > 0)


def test_cfar_2d_synthetic_scene():
    rng = np.random.default_rng(1)
    power = rng.exponential(1.0, (64, 32))
    truth = [(10, 5), (40, 20), (62, 30)]        # includes an edge cell
    for r, d in truth:
        power[r, d] += 80.0
        power[r, (d + 1) % 32] += 20.0          # sidelobe next to the peak
    dets = cfar_detections(power, pfa=1e-5, guard=(1, 1), train=(4, 2))
    found = {(d.range_bin, d.doppler_bin) for d in dets}
    for cell in truth:
        assert cell in found
    assert len(found) <= len(truth) + 2          # peaks_only suppresses the sidelobes
    assert all(d.snr_db > 0 for d in dets)


def test_cfar_2d_no_detections_on_pure_noise_with_tiny_pfa():
    rng = np.random.default_rng(2)
    power = rng.exponential(1.0, (64, 32))
    mask, _ = ca_cfar_2d(power, pfa=1e-9)
    assert mask.sum() == 0


def test_local_maxima():
    p = np.zeros((5, 5)); p[2, 2] = 5; p[2, 3] = 4
    m = np.ones_like(p, bool)
    out = local_maxima(p, m)
    assert out[2, 2] and not out[2, 3]


def test_clustering_dbscan_groups_neighbours():
    pts = [(100, 1), (101, 1.2), (500, -3), (900, 2), (901, 2)]
    clusters = cluster_points(pts, eps=5, min_samples=1)
    sizes = sorted(c.size for c in clusters)
    assert sizes == [1, 2, 2]
    assert cluster_points([], eps=5) == []


def test_tracker_follows_constant_velocity_target():
    tr = Tracker(gate=100.0, stale_after=5.0, dt=1.0)
    r, v = 1000.0, 10.0
    for k in range(10):
        tracks = tr.update([(r + v * k + np.random.default_rng(k).normal(0, 2), v)], now=float(k))
    assert len(tracks) == 1
    t = tracks[0]
    assert t.hits == 10
    assert abs(t.range_m - (r + v * 9)) < 15
    assert abs(t.velocity_mps - v) < 2


def test_tracker_creates_and_expires_tracks():
    tr = Tracker(gate=50.0, stale_after=2.0)
    tr.update([(100, 0), (5000, 20)], now=0.0)
    assert len(tr.tracks) == 2
    tr.update([(102, 0)], now=1.0)
    tr.update([(104, 0)], now=3.5)               # second track stale (> 2 s)
    assert len(tr.tracks) == 1
    assert tr.confirmed()[0].hits == 3
