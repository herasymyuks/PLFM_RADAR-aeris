"""Simulator -> FPGA byte stream -> parser -> frame assembler -> CFAR/tracker."""
import numpy as np

from aeris10_gui.processing import FrameAssembler, RadarPipeline
from aeris10_gui.protocol import fpga_packet as fp
from aeris10_gui.protocol.status_text import StatusStreamParser
from aeris10_gui.sim.replay import load_testbench_csv
from aeris10_gui.sim.simulator import DEMO_SETTINGS, RadarSimulator


def test_simulator_frame_shape_and_bytes():
    sim = RadarSimulator(seed=3)
    f = sim.next_frame()
    assert f.iq.shape == (fp.N_RANGE_BINS, fp.N_DOPPLER_BINS)
    assert len(f.fpga_bytes) == fp.N_RANGE_BINS * fp.N_DOPPLER_BINS * fp.PACKET_LENGTH
    assert f.status_bytes.startswith(b"System Status: NORMAL|")


def test_parser_reconstructs_simulator_map_exactly():
    sim = RadarSimulator(seed=4)
    f = sim.next_frame()
    parser = fp.FpgaPacketParser(check_top_level_consistency=True)
    asm = FrameAssembler()
    frames = []
    # feed in odd-sized chunks to exercise fragmentation
    data = f.fpga_bytes
    for i in range(0, len(data), 1000):
        frames += asm.feed(parser.feed(data[i:i + 1000]))
    assert parser.stats["packets"] == fp.N_RANGE_BINS * fp.N_DOPPLER_BINS
    assert parser.stats["resync_bytes_dropped"] == 0
    assert len(frames) == 1
    iq, det = frames[0]
    assert np.array_equal(iq, f.iq)
    assert np.array_equal(det, (np.abs(f.iq.real) + np.abs(f.iq.imag)) > 10000)


def test_pipeline_finds_simulated_targets():
    sim = RadarSimulator(seed=5)
    pipe = RadarPipeline(DEMO_SETTINGS)
    sp = StatusStreamParser()
    hits = 0
    for k in range(6):
        f = sim.next_frame(float(k))
        for msg in sp.feed(f.status_bytes):
            pipe.latest_status = msg
        res = pipe.process_frame(f.iq, None, now=float(k))
        truth_cells = {(t.range_bin, t.doppler_bin) for t in f.truth}
        det_cells = {(t.range_bin, t.doppler_bin) for t in res.targets}
        hits += sum(1 for c in truth_cells if any(abs(c[0] - d[0]) <= 1 and abs(c[1] - d[1]) <= 1 for d in det_cells))
    assert hits >= 0.6 * 5 * 6                   # most of the 5 targets found in most of the 6 frames
    assert len(res.tracks) >= 3
    assert res.status is not None and res.status.azimuth == 6
    assert res.power_db_shifted.shape == f.iq.shape


def test_velocity_axis_consistency_between_sim_and_pipeline():
    sim = RadarSimulator(seed=6)
    pipe = RadarPipeline(sim.settings)
    for v in (-50.0, -7.3, 0.0, 12.0, 60.0):
        k = sim.velocity_to_bin(v)
        assert abs(pipe.bin_to_velocity(k) - v) <= pipe.velocity_resolution / 2 + 1e-9


def test_testbench_csv_loads(test_csv_path):
    chirps = load_testbench_csv(test_csv_path)
    assert len(chirps) == 32                     # 16 LONG + 16 SHORT (docs/GUI/DEPENDENCIES.md section 5)
    assert all(len(v) == 512 for v in chirps.values())
    assert {k[0] for k in chirps} == {"LONG", "SHORT"}
