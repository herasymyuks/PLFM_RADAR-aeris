"""Headless UI smoke test: hidden Tk root, demo source, three processed frames."""
import pytest

from conftest import tk_available

pytestmark = pytest.mark.skipif(not tk_available(), reason="no display / Tk unavailable")


def test_main_window_demo_three_frames():
    import tkinter as tk
    from aeris10_gui.sim.simulator import DEMO_SETTINGS
    from aeris10_gui.ui.main_window import MainWindow

    root = tk.Tk()
    root.withdraw()
    try:
        win = MainWindow(root, demo=True, settings=DEMO_SETTINGS)
        win.start()
        root.after_cancel(win._after_id)
        win._after_id = None
        completed = sum(win.step() for _ in range(3))
        root.update()
        assert completed == 3
        assert win.source.decoder.bridge_parser.frames == 3          # default link = SPI bridge frames
        assert win.source.decoder.status_parser.stats["status"] == 3
        assert win.last_status is not None
        assert "Azimuth" in win.beam_label.cget("text")
        assert len(win.tree.get_children()) >= 1          # confirmed tracks listed after 3 frames
        win.stop()
    finally:
        root.destroy()


def test_settings_form_validation_blocks_firmware_rejects():
    import tkinter as tk
    from aeris10_gui.ui.main_window import MainWindow

    root = tk.Tk()
    root.withdraw()
    try:
        win = MainWindow(root, demo=True)
        win.settings_vars["prf1"].set("50")          # below firmware minimum 100
        assert win.read_settings_from_form() is None
        assert "prf1" in win.settings_msg.cget("text")
        win.settings_vars["prf1"].set("1000")
        assert win.read_settings_from_form() is not None
    finally:
        root.destroy()


def test_cli_selftest_exit_code():
    from aeris10_gui.app import main
    assert main(["--selftest", "--frames", "2"]) == 0


def test_raw_ft601_demo_three_frames():
    import tkinter as tk
    from aeris10_gui.sim.simulator import DEMO_SETTINGS
    from aeris10_gui.ui.main_window import MainWindow
    from aeris10_gui.ui.sources import LINK_RAW_FT601

    root = tk.Tk()
    root.withdraw()
    try:
        win = MainWindow(root, demo=True, settings=DEMO_SETTINGS, link=LINK_RAW_FT601)
        win.start()
        root.after_cancel(win._after_id)
        win._after_id = None
        assert sum(win.step() for _ in range(3)) == 3
        assert win.source.decoder.fpga_parser.stats["packets"] == 3 * 64 * 32
    finally:
        root.destroy()


def test_register_panel_read_all_and_calibration():
    import tkinter as tk
    from aeris10_gui.sim.simulator import DEMO_SETTINGS
    from aeris10_gui.ui.main_window import MainWindow

    root = tk.Tk()
    root.withdraw()
    try:
        win = MainWindow(root, demo=True, settings=DEMO_SETTINGS)
        panel = win.register_panel
        panel.read_all()                                     # not started yet -> refused, no crash
        assert "Not connected" in panel.msg.cget("text")
        win.start()
        root.after_cancel(win._after_id)
        win._after_id = None
        panel.v_cfar.set("4096")
        panel._write_entry(0x1, panel.v_cfar)
        panel.auto_pattern()
        panel.v_lane.set("3"); panel.v_tap.set("9")
        panel.manual_tap()
        panel.v_slip.set("2")
        panel.manual_bitslip()
        panel.read_all()
        win.step()
        root.update()
        c = win.reg_client
        assert c.pending == [] and c.errors == []
        assert c.values[0x1] == 4096 and c.values[0xF] == 0xBE7A
        assert c.values[0x9] & 0xFF == 0xFF                  # simulated lock mask after auto calibration
        assert c.lane_info[3] & 0x1F == 9                    # manual tap loaded into lane 3
        text = panel.text.get("1.0", "end")
        assert "lock[7..0]=LLLLLLLL" in text and "lane 3: tap= 9" in text
        assert win.source.sim.regs.cfar_threshold == 4096    # the write reached the demo FPGA
        panel.v_tap.set("40")
        panel.manual_tap()
        assert "outside" in panel.msg.cget("text")
    finally:
        root.destroy()
