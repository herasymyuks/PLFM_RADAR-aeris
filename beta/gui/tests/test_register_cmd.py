"""REG command codec, register map (from radar_control_regs.v), client <-> demo register file round trip."""
import pytest

from aeris10_gui.protocol import register_cmd as rc
from aeris10_gui.protocol import register_map as rm
from aeris10_gui.protocol.status_text import StatusStreamParser
from aeris10_gui.sim.register_file import DemoRegisterFile


def test_format_and_parse_commands():
    assert rc.format_write(0x1, 2000) == b"REG W 0x1 0x7D0\n"
    assert rc.format_read(0xF) == b"REG R 0xF\n"
    assert rc.parse_command("REG W 0x1 0x7D0\r\n") == ("W", 1, 2000)
    assert rc.parse_command("reg  r  15") == ("R", 15, None)
    for bad in ("REG X 1", "REG W 1", "REG R", "FOO R 1", "REG W 1 -3", "REG R zz"):
        with pytest.raises(rc.RegisterCommandError):
            rc.parse_command(bad)
    with pytest.raises(rc.RegisterCommandError):
        rc.format_write(0x10000, 0)


def test_parse_replies():
    r = rc.parse_reply("REG 0x9 0x1FF\r\n")
    assert (r.addr, r.value, r.ok) == (9, 0x1FF, True)
    e = rc.parse_reply("REG ERR")
    assert e.error and not e.ok
    with pytest.raises(rc.RegisterCommandError):
        rc.parse_reply("REG 1")


def test_register_map_matches_rtl_resets_and_fields():
    assert rm.REGISTERS[0x0].reset == 0b101            # {usb_enable=1, adc_pwdn=0, use_long_chirp=1}
    assert rm.REGISTERS[0x1].reset == 10000
    assert rm.REGISTERS[0x6].reset == 16 and rm.REGISTERS[0x8].reset == 0x55AA
    assert rm.decode(0x9, 0x86FF) == {"lock": 0xFF, "done": 0, "busy": 1, "align_fail": 1, "fifo_ovf": 1}
    assert rm.decode(0xA, (22 << 10) | (10 << 5) | 16) == {"tap": 16, "win_lo": 10, "win_hi": 22}
    assert rm.register(0x4).encode(auto_start=1, check_en=1) == 0b1001
    assert set(rm.UNMAPPED_ADDRESSES) == {0xD, 0xE}
    with pytest.raises(ValueError):
        rm.register(0x6).encode(tap=32)


def test_demo_register_file_rtl_semantics():
    rf = DemoRegisterFile()
    rf.write(0x0, 0xFFFF)
    assert rf.read(0x0) == 0x7                         # only bits [2:0] stored
    rf.write(0x4, 0b1111)                              # toggles + check_en
    assert rf.read(0x4) == 0b1000                      # toggles read as 0
    assert rf.read(0x9) & 0xFF == 0xFF                 # simulated auto calibration locked all lanes
    rf.write(0x9, 0)                                   # read-only: ignored
    assert rf.read(0x9) & 0xFF == 0xFF
    assert rf.read(0xD) == 0 and rf.read(0xF) == 0xBE7A
    assert rf.handle_line("REG R 0xD") == b"REG ERR\n"  # unmapped address -> error reply
    assert rf.handle_line("garbage") == b"REG ERR\n"


def test_client_round_trip_through_status_stream():
    rf = DemoRegisterFile()
    wire = bytearray()
    client = rc.RegisterClient(wire.extend)
    client.write(0x1, 2000)
    client.read(0x1)
    client.read(0xD)                                   # unmapped -> REG ERR
    client.read_all(rm.READ_ALL_ADDRESSES)
    assert bytes(wire).startswith(b"REG W 0x1 0x7D0\nREG R 0x1\nREG R 0xD\n")
    replies = rf.handle_stream(bytes(wire))
    parser = StatusStreamParser()
    for i in range(0, len(replies), 7):               # fragmented delivery
        for msg in parser.feed(replies[i:i + 7]):
            client.on_reply(msg)
    assert client.pending == []
    assert client.values[0x1] == 2000 and client.values[0xF] == 0xBE7A
    assert [e[1] for e in client.errors] == [0xD]
    assert sorted(client.lane_info) == list(range(8))
    assert all(rm.decode(0xA, v)["tap"] == 16 for v in client.lane_info.values())   # DEFAULT_TAP before calibration
    assert client.unexpected == 0


def test_client_refuses_runaway_pending():
    client = rc.RegisterClient(lambda b: None, max_pending=2)
    client.read(1); client.read(2)
    with pytest.raises(rc.RegisterCommandError):
        client.read(3)


def test_cdc_port_register_methods_write_ascii():
    from aeris10_gui.io.usb_cdc import CdcSerialPort

    class FakeSerial:
        is_open = True
        def __init__(self): self.out = bytearray()
        def write(self, d): self.out += d; return len(d)

    port = CdcSerialPort.__new__(CdcSerialPort)
    port._ser = FakeSerial()
    port.send_register_write(0x6, 20)
    port.send_register_read(0xA)
    assert bytes(port._ser.out) == b"REG W 0x6 0x14\nREG R 0xA\n"
