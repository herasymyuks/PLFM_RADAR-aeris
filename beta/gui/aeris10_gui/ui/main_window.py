"""Main window: controls, range-Doppler map, PPI, track list, settings, status bar.

Layout and widget set follow ``GUI_V5.RadarGUI`` (``GUI_V5.py:867-1300``):
control row (device selection, Refresh, Start, Stop, status/GPS/pitch labels),
``ttk.Notebook`` with a radar tab (matplotlib ``imshow`` range-Doppler map +
targets ``Treeview``) and a settings tab with the ten firmware fields.  Added:
PPI polar plot (``GUI_V5`` only had the Google-Maps HTML export, dropped),
status tab, ``pad_to_64`` checkbox, simulator-based demo mode, and a
``step()`` method used by ``--selftest``.  No background threads: a Tk timer
polls the data source (``GUI_V6_Demo`` style) so the UI is deterministic.
"""
from __future__ import annotations

import logging
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg   # noqa: E402
from matplotlib.figure import Figure                              # noqa: E402
import numpy as np                                                # noqa: E402

from .. import __version__
from ..model import GPSData, RadarSettings, SystemStatus
from ..processing import RadarPipeline
from ..protocol.register_cmd import RegisterClient, RegisterReply
from ..protocol.settings_packet import validate_settings
from ..protocol.status_text import azimuth_index_to_degrees
from .register_panel import RegisterPanel
from .sources import LINK_BRIDGE, LINK_RAW_FT601, DataSource, DemoSource, HardwareSource
from .theme import DARK_BG, DARK_FG, PLOT_BG, apply_dark_theme

log = logging.getLogger(__name__)

SETTINGS_FIELDS = [
    ("system_frequency", "System frequency (Hz)"),
    ("chirp_duration_1", "Long chirp duration (s)"),
    ("chirp_duration_2", "Short chirp duration (s)"),
    ("chirps_per_position", "Chirps per position"),
    ("freq_min", "IF min (Hz)"),
    ("freq_max", "IF max (Hz)"),
    ("prf1", "PRF 1 (Hz)"),
    ("prf2", "PRF 2 (Hz)"),
    ("max_distance", "Max distance (m)"),
    ("map_size", "Map size (m)"),
]


class MainWindow:
    def __init__(self, root: tk.Tk, *, demo: bool = False, settings: Optional[RadarSettings] = None,
                 port: Optional[str] = None, update_ms: int = 100, source: Optional[DataSource] = None,
                 link: str = LINK_BRIDGE):
        self.root = root
        self.demo = demo
        self.settings = settings if settings is not None else RadarSettings()
        self.update_ms = update_ms
        self.link = source.link if source is not None else link
        self.source: DataSource = source if source is not None else (DemoSource(link=link) if demo else DataSource(link))
        self.reg_client: Optional[RegisterClient] = None
        self.port = port
        self.running = False
        self.pad_to_64 = tk.BooleanVar(value=False)
        self.frames = 0
        self.fps = 0.0
        self._last_t = time.time()
        self._after_id = None
        self.last_status: Optional[SystemStatus] = None
        self.last_gps: Optional[GPSData] = None

        self.pipeline = RadarPipeline(self.settings)

        root.title(f"AERIS-10 Radar GUI {__version__} BETA -- {'DEMO' if demo else 'HARDWARE (unverified)'}")
        root.geometry("1400x900")
        root.minsize(1100, 700)
        self.style = ttk.Style(root)
        apply_dark_theme(root, self.style)
        self._build()
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------ layout
    def _build(self) -> None:
        ctrl = ttk.Frame(self.root, padding=5)
        ctrl.pack(fill="x")
        ttk.Label(ctrl, text="STM32 CDC port:").grid(row=0, column=0, padx=4)
        self.port_var = tk.StringVar(value=self.port or "")
        self.port_combo = ttk.Combobox(ctrl, textvariable=self.port_var, width=28, state="readonly" if not self.demo else "disabled")
        self.port_combo.grid(row=0, column=1, padx=4)
        ttk.Button(ctrl, text="Refresh ports", command=self.refresh_ports).grid(row=0, column=2, padx=4)
        self.start_btn = ttk.Button(ctrl, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=3, padx=4)
        self.stop_btn = ttk.Button(ctrl, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=4, padx=4)
        ttk.Label(ctrl, text=f"Source: {self.source.name}").grid(row=0, column=5, padx=12)
        link_text = ("FPGA link: SPI bridge via STM32 CDC (option B, unverified)" if self.link == LINK_BRIDGE
                     else "FPGA link: raw FT601 (option A) -- FT601 not wired on Main Board")
        ttk.Label(ctrl, text=link_text, foreground="#f0a050").grid(row=0, column=6, padx=12)
        self.gps_label = ttk.Label(ctrl, text="GPS: --")
        self.gps_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=4)
        self.pitch_label = ttk.Label(ctrl, text="IMU pitch: --")
        self.pitch_label.grid(row=1, column=4, columnspan=2, sticky="w", padx=4)
        self.beam_label = ttk.Label(ctrl, text="Beam: -- / Azimuth: --")
        self.beam_label.grid(row=1, column=6, sticky="w", padx=4)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self._build_radar_tab()
        self._build_settings_tab()
        self._build_status_tab()
        self.register_panel = RegisterPanel(self.notebook, lambda: self.reg_client)

        bar = ttk.Frame(self.root, padding=3)
        bar.pack(fill="x", side="bottom")
        self.status_label = ttk.Label(bar, text="Status: Ready")
        self.status_label.pack(side="left", padx=6)
        self.packets_label = ttk.Label(bar, text="Packets: 0")
        self.packets_label.pack(side="left", padx=6)
        self.frames_label = ttk.Label(bar, text="Frames: 0")
        self.frames_label.pack(side="left", padx=6)
        self.fps_label = ttk.Label(bar, text="FPS: 0.0")
        self.fps_label.pack(side="left", padx=6)
        self.errors_label = ttk.Label(bar, text="Parser errors: 0")
        self.errors_label.pack(side="left", padx=6)
        ttk.Label(bar, text="BETA -- not validated with hardware").pack(side="right", padx=6)

    def _build_radar_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Radar")
        plots = ttk.Frame(tab)
        plots.pack(side="left", fill="both", expand=True)
        self.fig = Figure(figsize=(10, 6), facecolor=DARK_BG)
        self.rd_ax = self.fig.add_subplot(1, 2, 1)
        self.ppi_ax = self.fig.add_subplot(1, 2, 2, projection="polar")
        for ax in (self.rd_ax, self.ppi_ax):
            ax.set_facecolor(PLOT_BG)
            ax.tick_params(colors=DARK_FG)
            for s in ax.spines.values():
                s.set_color(DARK_FG)
        n_r, n_d = self.pipeline.n_range, self.pipeline.n_doppler
        v = self.pipeline.velocity_axis_shifted()
        self.rd_img = self.rd_ax.imshow(np.zeros((n_r, n_d)), aspect="auto", cmap="viridis", origin="lower",
                                        extent=[v[0], v[-1], 0, self.settings.max_distance], interpolation="nearest")
        self.rd_ax.set_xlabel("Velocity (m/s)", color=DARK_FG)
        self.rd_ax.set_ylabel("Range (m)", color=DARK_FG)
        self.rd_ax.set_title("Range-Doppler (dB)", color=DARK_FG)
        self.det_scatter = self.rd_ax.scatter([], [], s=60, facecolors="none", edgecolors="red")
        self.ppi_ax.set_theta_zero_location("N")
        self.ppi_ax.set_theta_direction(-1)
        self.ppi_ax.set_ylim(0, self.settings.max_distance)
        self.ppi_ax.set_title("PPI (tracks)", color=DARK_FG)
        self.ppi_scatter = self.ppi_ax.scatter([], [], c="cyan", s=30)
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, plots)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        tf = ttk.LabelFrame(tab, text="Tracks", padding=4)
        tf.pack(side="right", fill="y", padx=(5, 0))
        cols = ("ID", "Range (m)", "Vel (m/s)", "Az (deg)", "Hits", "Misses")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=25)
        for c, w in zip(cols, (40, 90, 80, 70, 50, 55)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def _build_settings_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Settings")
        self.settings_vars = {}
        for i, (name, label) in enumerate(SETTINGS_FIELDS):
            ttk.Label(tab, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            var = tk.StringVar(value=str(getattr(self.settings, name)))
            self.settings_vars[name] = var
            ttk.Entry(tab, textvariable=var, width=24).grid(row=i, column=1, padx=5, pady=3)
        r = len(SETTINGS_FIELDS)
        ttk.Checkbutton(tab, text="Zero-pad CDC writes to 64 bytes (GUI_V5 legacy; current firmware rejects it)",
                        variable=self.pad_to_64).grid(row=r, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Button(tab, text="Apply settings", command=self.apply_settings).grid(row=r + 1, column=0, columnspan=2, pady=8)
        self.settings_msg = ttk.Label(tab, text="")
        self.settings_msg.grid(row=r + 2, column=0, columnspan=2, sticky="w")

    def _build_status_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="STM32 status")
        self.status_text = tk.Text(tab, height=20, bg=PLOT_BG, fg=DARK_FG, insertbackground=DARK_FG)
        self.status_text.pack(fill="both", expand=True)
        self.status_text.insert("end", "No status message received yet.\n")
        self.status_text.configure(state="disabled")

    # ------------------------------------------------------------------ actions
    def refresh_ports(self) -> None:
        if self.demo:
            return
        try:
            from ..io.usb_cdc import list_ports
            ports = list_ports()
        except ImportError as e:
            messagebox.showerror("pyserial missing", str(e))
            return
        self.port_combo["values"] = [p.device for p in ports]
        stm = [p.device for p in ports if p.is_stm32]
        if stm:
            self.port_var.set(stm[0])
        elif ports and not self.port_var.get():
            self.port_var.set(ports[0].device)

    def read_settings_from_form(self) -> Optional[RadarSettings]:
        try:
            kwargs = {}
            for name, _ in SETTINGS_FIELDS:
                raw = self.settings_vars[name].get()
                kwargs[name] = int(float(raw)) if name == "chirps_per_position" else float(raw)
            s = RadarSettings(**kwargs)
        except ValueError as e:
            self.settings_msg.config(text=f"Invalid value: {e}")
            return None
        problems = validate_settings(s)
        if problems:
            self.settings_msg.config(text="Firmware would reject: " + "; ".join(problems))
            return None
        return s

    def apply_settings(self) -> None:
        s = self.read_settings_from_form()
        if s is None:
            return
        self.settings = s
        self.pipeline = RadarPipeline(s, n_range=self.pipeline.n_range, n_doppler=self.pipeline.n_doppler)
        v = self.pipeline.velocity_axis_shifted()
        self.rd_img.set_extent([v[0], v[-1], 0, s.max_distance])
        self.ppi_ax.set_ylim(0, s.max_distance)
        if self.running and isinstance(self.source, HardwareSource) and self.source.cdc is not None:
            n = self.source.cdc.send_start_and_settings(s, pad_to_64=self.pad_to_64.get())
            self.settings_msg.config(text=f"Settings sent ({n} bytes). Firmware acceptance cannot be confirmed (no ACK in protocol).")
        else:
            self.settings_msg.config(text="Settings applied locally (sent on Start).")
        self.canvas.draw_idle()

    def start(self) -> None:
        s = self.read_settings_from_form()
        if s is None:
            return
        self.settings = s
        self.pipeline = RadarPipeline(s, n_range=self.pipeline.n_range, n_doppler=self.pipeline.n_doppler)
        if not self.demo and not isinstance(self.source, HardwareSource):
            port = self.port_var.get()
            if not port:
                messagebox.showerror("No port", "Select the STM32 CDC serial port first.")
                return
            self.source = HardwareSource(port, link=self.link)
        try:
            self.source.start(s, pad_to_64=self.pad_to_64.get())
        except Exception as e:                           # noqa: BLE001 -- surfaced to the user
            log.exception("start failed")
            messagebox.showerror("Start failed", str(e))
            return
        self.running = True
        self.reg_client = RegisterClient(self.source.send_line)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Status: Running")
        self._schedule()

    def stop(self) -> None:
        self.running = False
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.source.stop()
        self.reg_client = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped")

    def on_close(self) -> None:
        self.stop()
        self.root.destroy()

    # ------------------------------------------------------------------ loop
    def _schedule(self) -> None:
        if self.running:
            self._after_id = self.root.after(self.update_ms, self._tick)

    def _tick(self) -> None:
        try:
            self.step()
        except Exception:                                  # noqa: BLE001
            log.exception("update failed")
        self._schedule()

    def step(self) -> int:
        """Poll the source once, process, redraw.  Returns frames completed in this step."""
        res = self.source.poll()
        reg_replies = 0
        for msg in res.messages:
            if isinstance(msg, SystemStatus):
                self.last_status = msg
                self.pipeline.latest_status = msg
                self._show_status(msg)
            elif isinstance(msg, GPSData):
                self.last_gps = msg
            elif isinstance(msg, RegisterReply):
                if self.reg_client is not None:
                    self.reg_client.on_reply(msg)
                reg_replies += 1
        if reg_replies:
            self.register_panel.render()
        completed = 0
        now = time.time()
        for bf in res.bridge_frames:
            self._draw(self.pipeline.process_bridge_frame(bf, now))
            completed += 1
        for iq, det in res.raw_frames:
            self._draw(self.pipeline.process_frame(iq, det, now))
            completed += 1
        self.frames += completed
        if completed:
            dt = now - self._last_t
            if dt > 0:
                self.fps = 0.8 * self.fps + 0.2 * (completed / dt)
            self._last_t = now
        dec = self.source.decoder
        unit = "frames" if self.link == LINK_BRIDGE else "packets"
        count = dec.bridge_parser.frames if self.link == LINK_BRIDGE else dec.fpga_parser.stats["packets"]
        self.packets_label.config(text=f"Link {unit}: {count}")
        self.frames_label.config(text=f"Frames: {self.frames}")
        self.fps_label.config(text=f"FPS: {self.fps:.1f}")
        self.errors_label.config(text=f"Parser errors: {dec.error_count()}")
        return completed

    def _show_status(self, s: SystemStatus) -> None:
        gps = f"GPS: {s.gps_latitude:.6f}, {s.gps_longitude:.6f}  ALT {s.altitude:.1f} m" if s.gps_latitude is not None else "GPS: --"
        self.gps_label.config(text=gps)
        self.pitch_label.config(text=f"IMU pitch: {s.imu_pitch:+.1f} deg" if s.imu_pitch is not None else "IMU pitch: --")
        az = f"{azimuth_index_to_degrees(s.azimuth):.1f} deg (idx {s.azimuth})" if s.azimuth is not None else "--"
        self.beam_label.config(text=f"Beam: {s.beam_pos} / Azimuth: {az}")
        lines = [f"mode: {s.mode}", f"last_error: {s.last_error}  error_count: {s.error_count}",
                 f"IMU pitch/roll/yaw: {s.imu_pitch} / {s.imu_roll} / {s.imu_yaw}",
                 f"LO_TX locked: {s.lo_tx_locked}  LO_RX locked: {s.lo_rx_locked}",
                 f"temperatures: {s.temperatures}", f"PA: current={s.pa_avg_current} enabled={s.pa_enabled}",
                 f"BeamPos={s.beam_pos} Azimuth={s.azimuth} ChirpCount={s.chirp_count}",
                 f"unknown fields: {s.unknown_fields}", "", "raw:", s.raw]
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.insert("end", "\n".join(lines) + "\n")
        self.status_text.configure(state="disabled")

    def _draw(self, result) -> None:
        img = result.power_db_shifted
        self.rd_img.set_data(img)
        lo, hi = np.percentile(img, 5), np.percentile(img, 99.5)
        self.rd_img.set_clim(lo, max(hi, lo + 1))
        if result.targets:
            self.det_scatter.set_offsets([[t.velocity_mps, t.range_m] for t in result.targets])
        else:
            self.det_scatter.set_offsets(np.empty((0, 2)))
        tracks = [t for t in result.tracks if t.hits >= self.pipeline.tracker.confirm_hits]
        az_rad = np.deg2rad(result.targets[0].azimuth_deg) if result.targets else 0.0
        if tracks:
            self.ppi_scatter.set_offsets([[az_rad, t.range_m] for t in tracks])
        else:
            self.ppi_scatter.set_offsets(np.empty((0, 2)))
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in sorted(tracks, key=lambda t: t.id):
            self.tree.insert("", "end", values=(t.id, f"{t.range_m:.0f}", f"{t.velocity_mps:+.1f}",
                                                f"{np.rad2deg(az_rad):.1f}", t.hits, t.misses))
        self.canvas.draw_idle()
