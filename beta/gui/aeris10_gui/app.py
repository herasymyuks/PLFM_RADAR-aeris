"""Command-line entry point: ``aeris10-gui [--demo] [--selftest] [--port PORT]``."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional, Sequence

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aeris10-gui", description="AERIS-10 radar host GUI (BETA)")
    p.add_argument("--demo", action="store_true", help="run with the built-in simulator (no hardware)")
    p.add_argument("--selftest", action="store_true",
                   help="create the window hidden, run --frames simulator frames through the full pipeline, exit 0")
    p.add_argument("--frames", type=int, default=3, help="frames for --selftest (default 3)")
    p.add_argument("--port", help="STM32 CDC serial port (hardware mode)")
    p.add_argument("--update-ms", type=int, default=100, help="UI poll interval in ms")
    p.add_argument("--log-level", default="INFO")
    p.add_argument("--version", action="version", version=f"aeris10-gui {__version__}")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    import tkinter as tk
    from .model import RadarSettings
    from .sim.simulator import DEMO_SETTINGS
    from .ui.main_window import MainWindow

    demo = args.demo or args.selftest
    settings = DEMO_SETTINGS if demo else RadarSettings()
    root = tk.Tk()
    if args.selftest:
        root.withdraw()
        win = MainWindow(root, demo=True, settings=settings, update_ms=args.update_ms)
        win.start()
        if win._after_id is not None:     # drive step() ourselves, deterministically
            root.after_cancel(win._after_id)
            win._after_id = None
        completed = 0
        for _ in range(args.frames * 2 + 2):
            completed += win.step()
            root.update()
            if completed >= args.frames:
                break
        stats = dict(win.fpga_parser.stats)
        win.stop()
        root.destroy()
        ok = completed >= args.frames and stats["packets"] > 0
        print(f"selftest: frames={completed} packets={stats['packets']} "
              f"resync_dropped={stats['resync_bytes_dropped']} status_msgs={win.cdc_parser.stats['status']} "
              f"-> {'OK' if ok else 'FAIL'}")
        return 0 if ok else 1
    win = MainWindow(root, demo=demo, settings=settings, port=args.port, update_ms=args.update_ms)
    if not demo:
        win.refresh_ports()
    root.mainloop()
    return 0


if __name__ == "__main__":          # pragma: no cover
    sys.exit(main())
