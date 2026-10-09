"""HardwareSource (bridge link) on a synthetic CDC stream: frames + status strings + REG replies interleaved."""
import numpy as np

from aeris10_gui.model import GPSData, RadarSettings, SystemStatus
from aeris10_gui.processing import RadarPipeline, bridge_frame_to_power
from aeris10_gui.protocol.bridge_frame import build_frame, parse_frame
from aeris10_gui.protocol.register_cmd import RegisterReply, format_error, format_reply
from aeris10_gui.protocol.settings_packet import START_FLAG, build_settings_packet
from aeris10_gui.protocol.status_text import encode_gpsb, format_status_line
from aeris10_gui.sim.simulator import RadarSimulator, bridge_frame_from_iq, logmag
from aeris10_gui.ui.sources import LINK_BRIDGE, LINK_RAW_FT601, DemoSource, HardwareSource, LinkDecoder


class FakeCdc:
    """Stands in for CdcSerialPort: records writes, returns scripted read chunks."""

    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.written = bytearray()
        self.is_open = False

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def write(self, data):
        self.written += data
        return len(data)

    def read(self, size=8192):
        return self.chunks.pop(0) if self.chunks else b""

    def send_start_and_settings(self, settings, *, pad_to_64=False):
        return self.write(START_FLAG) + self.write(build_settings_packet(settings))


def _synthetic_stream():
    sim = RadarSimulator(seed=11)
    frames = [build_frame(sim.next_bridge_frame()[1]) for _ in range(3)]
    status = [format_status_line(azimuth=k + 1, beam_pos=2, chirp_count=32 * k).encode() for k in range(3)]
    stream = (status[0] + frames[0] + format_reply(0xF, 0xBE7A) + b"GPS:1.5,2.5,3.5\r\n"
              + frames[1] + status[1] + format_error() + encode_gpsb(4.0, 5.0, 6.0, 7.0)
              + b"\xa5\x5a\x01junk" + frames[2] + status[2] + format_reply(0x9, 0x1FF))
    return stream, frames


def test_hardware_bridge_source_decodes_interleaved_stream():
    stream, frames = _synthetic_stream()
    chunks = [stream[i:i + 509] for i in range(0, len(stream), 509)]       # CDC-sized, unaligned
    cdc = FakeCdc(chunks)
    src = HardwareSource(link=LINK_BRIDGE, cdc=cdc)
    src.start(RadarSettings())
    assert bytes(cdc.written) == START_FLAG + build_settings_packet(RadarSettings())
    got_frames, msgs = [], []
    for _ in range(len(chunks) + 2):
        r = src.poll()
        got_frames += r.bridge_frames
        msgs += r.messages
    assert [build_frame(f) for f in got_frames] == frames
    kinds = [type(m).__name__ for m in msgs]
    assert kinds.count("SystemStatus") == 3 and kinds.count("RegisterReply") == 3 and kinds.count("GPSData") == 2
    regs = [m for m in msgs if isinstance(m, RegisterReply)]
    assert (regs[0].addr, regs[0].value) == (0xF, 0xBE7A) and regs[1].error and regs[2].value == 0x1FF
    assert [m.azimuth for m in msgs if isinstance(m, SystemStatus)] == [1, 2, 3]
    assert src.decoder.bridge_parser.crc_errors == 0
    assert src.decoder.bridge_parser.resyncs >= 1          # the fake sync + "junk" was skipped
    src.send_line(b"REG R 0x9\n")
    assert cdc.written.endswith(b"REG R 0x9\n")
    src.stop()
    assert not cdc.is_open


def test_raw_ft601_hardware_source_has_no_frames_and_reports_why():
    cdc = FakeCdc([format_status_line().encode()])
    src = HardwareSource(link=LINK_RAW_FT601, cdc=cdc)
    src.start(RadarSettings())
    assert "not wired" in src.fpga_error
    r = src.poll()
    assert r.bridge_frames == [] and r.raw_frames == [] and isinstance(r.messages[0], SystemStatus)


def test_simulator_bridge_frame_matches_rd_map_packer_semantics():
    sim = RadarSimulator(seed=12)
    frame, bf = sim.next_bridge_frame()
    assert parse_frame(build_frame(bf)).magnitude == bf.magnitude
    mag = (np.abs(frame.iq.real) + np.abs(frame.iq.imag)).astype(int).reshape(-1)
    assert list(bf.magnitude) == [logmag(int(m)) for m in mag]
    thr = sim.regs.cfar_threshold
    expected = [(int(c // 32), int(c % 32)) for c in np.nonzero(mag > thr)[0][:32]]
    assert [(r, d) for r, d, _ in bf.detections] == expected
    assert (bf.azimuth, bf.elevation, bf.long_chirp) == (frame.azimuth_index, frame.beam_pos, True)
    # register write changes what the "FPGA" emits: CFAR_THR lowered -> more detections, long_chirp cleared
    sim.regs.handle_line("REG W 0x1 0x1000")
    sim.regs.handle_line("REG W 0x0 0x4")
    _, bf2 = sim.next_bridge_frame()
    assert len(bf2.detections) >= len(bf.detections) and not bf2.long_chirp


def test_bridge_frames_generator_and_sequence():
    sim = RadarSimulator(seed=13)
    seqs = [parse_frame(b).seq for b in sim.bridge_frames(4)]
    assert seqs == [0, 1, 2, 3]


def test_pipeline_on_bridge_frames_finds_targets():
    sim = RadarSimulator(seed=14)
    pipe = RadarPipeline(sim.settings)
    hits = 0
    for k in range(5):
        frame, bf = sim.next_bridge_frame(float(k))
        res = pipe.process_bridge_frame(parse_frame(build_frame(bf)), now=float(k))
        det = {(t.range_bin, t.doppler_bin) for t in res.targets}
        hits += sum(1 for t in frame.truth if any(abs(t.range_bin - r) <= 1 and abs(t.doppler_bin - d) <= 1 for r, d in det))
    assert hits >= 0.6 * 5 * 5
    power, det_map = bridge_frame_to_power(bf)
    assert power.shape == (64, 32) and det_map.sum() == len(bf.detections)


def test_demo_source_emulates_firmware_single_slot():
    src = DemoSource(link=LINK_BRIDGE)
    src.start(RadarSettings(max_distance=5000, map_size=5000))
    src.send_line(b"REG R 0xF\n")
    src.send_line(b"REG W 0x4 0x1\n")                 # second transfer before the "main loop" ran: dropped
    assert src.dropped_commands == 1
    replies = []
    for cmd in (None, b"REG W 0x4 0x1\n", b"REG R 0x9\n"):
        if cmd:
            src.send_line(cmd)
        r = src.poll()                                 # one frame + status + the reply of the slot
        assert len(r.bridge_frames) == 1 and any(isinstance(m, SystemStatus) for m in r.messages)
        replies += [m for m in r.messages if isinstance(m, RegisterReply)]
    assert [(m.addr, m.value) for m in replies] == [(0xF, 0xBE7A), (0x4, 1), (0x9, 0x1FF)]   # write echoes value
    assert all(m.raw.startswith("REG 0x000") for m in replies)


def test_link_decoder_rejects_unknown_link():
    import pytest
    with pytest.raises(ValueError):
        LinkDecoder("usb4")
