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
    p.add_argument("--raw-ft601", action="store_true",
                   help="option A: decode raw 35-byte RTL packets (FT601) instead of SPI-bridge frames over CDC")
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
    from .ui.sources import LINK_BRIDGE, LINK_RAW_FT601
    from .protocol.register_map import READ_ALL_ADDRESSES
    link = LINK_RAW_FT601 if args.raw_ft601 else LINK_BRIDGE

    demo = args.demo or args.selftest
    settings = DEMO_SETTINGS if demo else RadarSettings()
    root = tk.Tk()
    if args.selftest:
        root.withdraw()
        win = MainWindow(root, demo=True, settings=settings, update_ms=args.update_ms, link=link)
        win.start()
        if win._after_id is not None:     # drive step() ourselves, deterministically
            root.after_cancel(win._after_id)
            win._after_id = None
        win.reg_client.read_all(READ_ALL_ADDRESSES)       # demo register file answers via the CDC stream
        completed = 0
        # one REG command per poll (firmware single slot): keep stepping until the read-all is answered
        for _ in range(args.frames + 200):
            completed += win.step()
            root.update()
            if completed >= args.frames and not win.reg_client.pending:
                break
        dec = win.source.decoder
        rc_client = win.reg_client
        reg_ok = rc_client.values.get(0xF) == 0xBE7A and not rc_client.pending and not rc_client.errors
        status_msgs = dec.status_parser.stats["status"]
        win.stop()
        root.destroy()
        ok = completed >= args.frames and status_msgs > 0 and reg_ok and dec.error_count() == 0
        print(f"selftest: link={link} frames={completed} link_stats={dec.stats()} "
              f"reg_read_all={'OK' if reg_ok else 'FAIL'} (sent={rc_client.sent}, "
              f"dropped_by_slot={getattr(win.source, 'dropped_commands', 'n/a')}) -> {'OK' if ok else 'FAIL'}")
        return 0 if ok else 1
    win = MainWindow(root, demo=demo, settings=settings, port=args.port, update_ms=args.update_ms, link=link)
    if not demo:
        win.refresh_ports()
    root.mainloop()
    return 0


if __name__ == "__main__":          # pragma: no cover
    sys.exit(main())
