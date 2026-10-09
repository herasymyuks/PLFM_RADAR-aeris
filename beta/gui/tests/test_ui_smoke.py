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
        assert win.fpga_parser.stats["packets"] == 3 * 64 * 32
        assert win.cdc_parser.stats["status"] == 3
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
