"""REG command codec against the firmware's literal behaviour (host_bridge_proto.c, USBHandler.cpp, main.cpp)."""
import pytest

from aeris10_gui.protocol import register_cmd as rc
from aeris10_gui.protocol import register_map as rm
from aeris10_gui.protocol.status_text import StatusStreamParser
from aeris10_gui.sim.register_file import DemoRegisterFile

# --- firmware-literal vectors ----------------------------------------------------------------
FW_REPLY_READ = b"REG 0x0009 0x000001FF\r\n"       # snprintf("REG 0x%04X 0x%08lX\r\n")
FW_REPLY_WRITE = b"REG 0x0001 0x00000FA0\r\n"      # write echoes the written value
FW_REPLY_ERR = b"REG ERR\r\n"


def test_parse_firmware_literal_replies():
    r = rc.parse_reply(FW_REPLY_READ.decode())
    assert (r.addr, r.value, r.ok, r.raw) == (9, 0x1FF, True, "REG 0x0009 0x000001FF")
    w = rc.parse_reply(FW_REPLY_WRITE.decode())
    assert (w.addr, w.value) == (1, 4000)
    e = rc.parse_reply(FW_REPLY_ERR.decode())
    assert e.error and not e.ok and e.raw == "REG ERR"
    assert rc.format_reply(9, 0x1FF) == FW_REPLY_READ and rc.format_error() == FW_REPLY_ERR
    assert rc.is_reply_line("REG 0x0009 0x000001FF\r\n") and rc.is_reply_line("REG ERR\r\n")
    for bad in ("REG 1", "REG 0x1 0x2 0x3", "reg 0x1 0x2", "REG 0x123456789 0x1"):
        assert not rc.is_reply_line(bad)
        with pytest.raises(rc.RegisterCommandError):
            rc.parse_reply(bad)


def test_device_side_parse_matches_hb_cmd_parse():
    assert rc.parse_command("REG W 0x1 0x7D0\r\n") == ("W", 1, 2000)
    assert rc.parse_command("REG w 0X1 4000") == ("W", 1, 4000)          # op either case, 0X allowed
    assert rc.parse_command("REG r 15") == ("R", 15, None)
    assert rc.parse_command("REG R 0xFFFF\n") == ("R", 0xFFFF, None)
    assert rc.parse_command("REG R 0x1\nREG R 0x2\n") == ("R", 1, None)  # line cut at first \n: 2nd command discarded
    assert rc.parse_command("REGR 1") == ("R", 1, None)   # firmware quirk: no space required after "REG" (skip_ws(p+3))
    for bad in ("reg R 1", "REG X 1", "REG W 1", "REG R", "REG R 0x10000", "REG W 1 -3", "REG R zz",
                "REG R 0x123456789", "REG R 1 junk", "REG WR 1 2"):
        with pytest.raises(rc.RegisterCommandError):
            rc.parse_command(bad)
    assert rc.is_text_command(b"REG R 1") and not rc.is_text_command(b" REG R 1") and not rc.is_text_command(b"RE")


def test_host_formats_accepted_by_device_parser():
    assert rc.format_write(0x1, 2000) == b"REG W 0x1 0x7D0\n"
    assert rc.format_read(0xF) == b"REG R 0xF\n"
    assert rc.parse_command(rc.format_write(0x1, 2000).decode()) == ("W", 1, 2000)
    with pytest.raises(rc.RegisterCommandError):
        rc.format_write(0x10000, 0)


def test_bridge_status_bytes():
    rx = bytes([0x00, 0x09, 0x00, 0x02, 0x01, 0x34, 0x12, 0x00, 0x00])
    st = rc.parse_bridge_status(rx)
    assert (st.status, st.version, st.frames, st.reserved) == (9, 0x0102, 0x1234, 0)
    assert st.frame_ready and st.calibration_lock and not st.fifo_overflow and not st.adar_cs_conflict
    with pytest.raises(rc.RegisterCommandError):
        rc.parse_bridge_status(rx[:5])


def test_register_map_matches_rtl_resets_and_fields():
    assert rm.REGISTERS[0x0].reset == 0b101
    assert rm.REGISTERS[0x1].reset == 10000
    assert rm.REGISTERS[0x6].reset == 16 and rm.REGISTERS[0x8].reset == 0x55AA
    assert rm.decode(0x9, 0x86FF) == {"lock": 0xFF, "done": 0, "busy": 1, "align_fail": 1, "fifo_ovf": 1}
    assert rm.decode(0xA, (22 << 10) | (10 << 5) | 16) == {"tap": 16, "win_lo": 10, "win_hi": 22}
    assert rm.register(0x4).encode(auto_start=1, check_en=1) == 0b1001
    assert set(rm.UNMAPPED_ADDRESSES) == {0xD, 0xE}
    with pytest.raises(ValueError):
        rm.register(0x6).encode(tap=32)


def test_demo_register_file_rtl_semantics_and_firmware_replies():
    rf = DemoRegisterFile()
    assert rf.handle_transfer(b"REG W 0x0 0xFFFF\n") == b"REG 0x0000 0x0000FFFF\r\n"   # echo of the written value
    assert rf.read(0x0) == 0x7                                                          # only bits [2:0] stored
    rf.write(0x4, 0b1111)
    assert rf.read(0x4) == 0b1000                      # toggles read as 0
    assert rf.read(0x9) & 0xFF == 0xFF                 # simulated auto calibration locked all lanes
    rf.write(0x9, 0)
    assert rf.read(0x9) & 0xFF == 0xFF                 # read-only
    assert rf.read(0xD) == 0 and rf.read(0xF) == 0xBE7A
    assert rf.handle_transfer(b"REG R 0xF\r\n") == b"REG 0x000F 0x0000BE7A\r\n"
    assert rf.handle_transfer(b"REG R 0xD\n") == FW_REPLY_ERR
    assert rf.handle_transfer(b"garbage") == b""       # not a text command at byte 0
    assert rf.handle_transfer(b"REG R 0x1\nREG R 0x2\n") == b"REG 0x0001 0x00002710\r\n"   # second line lost


class FakeFirmware:
    """USBHandler single slot + main loop: one transfer captured, executed on `main_loop()`, others dropped."""

    def __init__(self, regs: DemoRegisterFile):
        self.regs = regs
        self.slot = None
        self.dropped = 0
        self.out = bytearray()

    def usb_out(self, data: bytes):
        if not rc.is_text_command(data):
            return
        if self.slot is not None:
            self.dropped += 1
            return
        self.slot = bytes(data)

    def main_loop(self) -> bytes:
        if self.slot is None:
            return b""
        reply = self.regs.handle_transfer(self.slot)
        self.slot = None
        return reply


def test_client_single_slot_pacing_round_trip():
    fw = FakeFirmware(DemoRegisterFile())
    client = rc.RegisterClient(fw.usb_out, clock=lambda: 0.0)
    client.write(0x1, 2000)
    client.read(0x1)
    client.read(0xD)                                   # unmapped -> REG ERR
    client.read_all(rm.READ_ALL_ADDRESSES)
    assert client.sent == 1 and fw.slot == b"REG W 0x1 0x7D0\n"       # exactly one command in flight
    parser = StatusStreamParser()
    loops = 0
    while client.pending and loops < 100:
        loops += 1
        reply = fw.main_loop()
        for i in range(0, len(reply), 5):              # fragmented CDC delivery incl. split "\r\n"
            for msg in parser.feed(reply[i:i + 5]):
                client.on_reply(msg)
    assert fw.dropped == 0                             # pacing respected the single slot
    assert client.sent == loops == 3 + len(rm.READ_ALL_ADDRESSES) + 2 * 8 + 1
    assert client.values[0x1] == 2000 and client.values[0xF] == 0xBE7A
    assert [e[1] for e in client.errors] == [0xD]
    assert sorted(client.lane_info) == list(range(8))
    assert all(rm.decode(0xA, v)["tap"] == 16 for v in client.lane_info.values())
    assert client.unexpected == 0 and client.retransmits == 0


def test_unpaced_sender_loses_commands_on_the_firmware_slot():
    """Why the client paces: two transfers before the main loop runs -> the second is dropped."""
    fw = FakeFirmware(DemoRegisterFile())
    fw.usb_out(b"REG R 0xF\n")
    fw.usb_out(b"REG R 0x1\n")
    assert fw.dropped == 1
    assert fw.main_loop() == b"REG 0x000F 0x0000BE7A\r\n" and fw.main_loop() == b""


def test_client_timeout_retransmit_then_error():
    t = [0.0]
    sent = []
    client = rc.RegisterClient(sent.append, timeout=1.0, retries=2, clock=lambda: t[0])
    client.read(0x9)
    client.read(0xF)
    assert len(sent) == 1
    for k in range(1, 3):
        t[0] = 1.5 * k
        client.poll()
        assert len(sent) == 1 + k and client.retransmits == k
    t[0] = 10.0
    client.poll()                                      # third expiry: give up, move on to the next command
    assert client.errors == [("R", 0x9, None, "timeout")]
    assert sent[-1] == b"REG R 0xF\n" and client.in_flight is not None
    client.on_reply(rc.parse_reply("REG 0x000F 0x0000BE7A\r\n"))
    assert client.pending == [] and client.values[0xF] == 0xBE7A


def test_client_refuses_runaway_queue():
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
