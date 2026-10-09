#!/usr/bin/env python3
"""Shared PROPOSED head/pedestal layout for the AERIS-10 design generators (D-08, D-09, D-11, D-12, D-13).

Coordinate system of the HEAD (all mm): X = width (0 at the inner left wall, looking at the antenna),
Y = depth (0 = inner face of the front wall; antenna side), Z = height (0 = top of the base plate).
Boards are VERTICAL, parallel to the antenna, in depth order:
  radome gap → antenna panel → PA heat-spreader plate → 16 PA boards → Main Board → Synth → Power Board → rear wall.
Connector positions come from the KiCad pick-and-place files generated from the EAGLE boards
(engineering/PCB/<BOARD>/assembly/<BOARD>_pick_and_place.csv, mm, Y up).
Importing this module has no side effects; `python3 tools/design_layout.py` prints the layout.
"""
from __future__ import annotations

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSN = os.path.join(ROOT, "engineering", "DESIGN")
P = json.load(open(os.path.join(DSN, "design_parameters.json")))
TH = json.load(open(os.path.join(DSN, "THERMAL", "thermal_summary.json"))) if os.path.isfile(os.path.join(DSN, "THERMAL", "thermal_summary.json")) else {"fins": {"n": 26, "h": 25, "t": 2, "pitch": 4, "len": 280, "strip_w": 55}}
B = P["boards_mm"]
WALL = P["enclosure"]["wall_mm"]["value"]

# --- heat-spreader plate (D-11) ---
PLATE = {"w": 300.0, "h": 300.0, "t": P["thermal"]["heat_spreader_thickness_mm"]["value"]}
FIN = dict(TH["fins"])          # fins on the REAR face of the plate, two side strips, vertical airflow
# --- antenna panel (from design_antenna_array.py result; keep in sync) ---
ANT = {"w": 165.0, "h": 248.0, "t": 0.6, "gap_to_plate": 2.4, "radome_gap": 8.0}
# --- depth stations (Y) ---
Y_ANT = ANT["radome_gap"]                                  # antenna PCB front face
Y_PLATE = Y_ANT + ANT["t"] + ANT["gap_to_plate"]            # plate front face
Y_PLATE_REAR = Y_PLATE + PLATE["t"]
PA_TIER = 30.0                                              # PA boards + components + fins (fins 25 mm)
Y_PA = Y_PLATE_REAR                                         # PA board plane (on the plate rear face, thermal pad)
Y_MAIN = Y_PLATE_REAR + PA_TIER + 5.0                       # Main Board plane (components toward the rear)
PITCH = B["board_pitch_mm"]["value"]
Y_SYNTH = Y_MAIN + PITCH
Y_POWER = Y_SYNTH + PITCH
Y_REAR_IN = Y_POWER + B["pcb_thickness_mm"]["value"] + B["component_height_top_mm"]["value"] + 5.0
# --- width/height ---
W_IN = PLATE["w"] + 2 * 5.0
H_IN = PLATE["h"] + 2 * 5.0
D_IN = Y_REAR_IN
OUTER = {"w": W_IN + 2 * WALL, "h": H_IN + 2 * WALL, "d": D_IN + 2 * WALL}
# --- board placements: (x0, z0) of the board's lower-left corner in head coordinates; boards vertical ---
PLATE_POS = {"x": 5.0, "z": 5.0}
ANT_POS = {"x": PLATE_POS["x"] + (PLATE["w"] - ANT["w"]) / 2, "z": PLATE_POS["z"] + (PLATE["h"] - ANT["h"]) / 2}
PA_GRID = {"cols": 4, "rows": 4, "pitch_x": 40.0, "pitch_z": 68.0}
_pa_field_w = PA_GRID["cols"] * PA_GRID["pitch_x"] - (PA_GRID["pitch_x"] - B["RF_PA"]["w"])
_pa_field_h = PA_GRID["rows"] * PA_GRID["pitch_z"] - (PA_GRID["pitch_z"] - B["RF_PA"]["h"])
PA_FIELD = {"x": PLATE_POS["x"] + (PLATE["w"] - _pa_field_w) / 2, "z": PLATE_POS["z"] + (PLATE["h"] - _pa_field_h) / 2, "w": _pa_field_w, "h": _pa_field_h}
MAIN_POS = {"x": (W_IN - B["MAIN_BOARD"]["w"]) / 2, "z": 5.0}
POWER_POS = {"x": (W_IN - B["POWER_SUPPLY"]["w"]) / 2, "z": 5.0}


def pa_positions():
    """Lower-left (x, z) of each of the 16 PA boards, numbered row-major from bottom-left (PA1..PA16)."""
    out = []
    for r in range(PA_GRID["rows"]):
        for c in range(PA_GRID["cols"]):
            out.append((PA_FIELD["x"] + c * PA_GRID["pitch_x"], PA_FIELD["z"] + r * PA_GRID["pitch_z"]))
    return out


def load_pnp(board: str) -> dict:
    """Ref → (x, y, side) from the KiCad position file (board coordinates, mm, Y up)."""
    p = os.path.join(ROOT, "engineering", "PCB", board, "assembly", f"{board}_pick_and_place.csv")
    out = {}
    if not os.path.isfile(p):
        return out
    with open(p, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for r in rd:
            try:
                out[r["Ref"]] = (float(r["PosX"]), float(r["PosY"]), r.get("Side", "top"))
            except (KeyError, ValueError):
                continue
    return out


def board_to_head(board: str, bx: float, by: float) -> tuple[float, float, float]:
    """Map a connector position on a vertical board to head (x, y, z)."""
    if board == "MAIN_BOARD":
        return (MAIN_POS["x"] + bx, Y_MAIN, MAIN_POS["z"] + by)
    if board == "POWER_SUPPLY":
        return (POWER_POS["x"] + bx, Y_POWER, POWER_POS["z"] + by)
    if board == "FREQUENCY_SYNTHESIZER":
        sp = synth_pos()
        return (sp["x"] + bx, Y_SYNTH, sp["z"] + by)
    raise ValueError(board)


_SYNTH = None


def synth_pos() -> dict:
    """Place the Synth board on its tier as close as possible to the Main Board clock/LO SMAs (J1, J18, J20, J21, J22, J23)."""
    global _SYNTH
    if _SYNTH is not None:
        return _SYNTH
    pnp = load_pnp("MAIN_BOARD")
    refs = [r for r in ("J1", "J18", "J20", "J21", "J22", "J23") if r in pnp]
    if refs:
        cx = sum(pnp[r][0] for r in refs) / len(refs) + MAIN_POS["x"]
        cz = sum(pnp[r][1] for r in refs) / len(refs) + MAIN_POS["z"]
    else:
        cx, cz = W_IN / 2, H_IN / 2
    w = B["FREQUENCY_SYNTHESIZER"]["w"]
    x = min(max(cx - w / 2, 5.0), W_IN - w - 5.0)
    z = min(max(cz - w / 2, 5.0), H_IN - w - 5.0)
    _SYNTH = {"x": x, "z": z, "basis": f"centred on Main Board {','.join(refs)} (P&P)"}
    return _SYNTH


# --- pedestal (D-12, D-13) ---
PEDESTAL = {
    "turntable_d": 340.0, "turntable_t": 8.0,
    "bearing_od": 190.0, "bearing_id": 100.0, "bearing_t": 20.0,
    "ring_pulley_d": 172.0, "ring_pulley_t": 12.0, "ring_teeth": 180,
    "motor": "NEMA 23 (56.4 mm square, 76 mm long, 6.35 mm shaft), 200 steps/rev, ≥ 1.9 N·m",
    "motor_pulley_d": 57.3, "motor_teeth": 60, "belt": "GT3 9 mm", "ratio": 3,
    "firmware_change": "Stepper_steps = 600 (main.cpp:195) so that 4×3 = 12 pulses give 7.2° at the table; TB6600 at full step",
    "slip_ring": "through-bore slip ring, bore ≥ 60 mm, 12 circuits (4 × 10 A VIN, 4 × 10 A 22 V, 4 × signal USB 2.0)",
    "slip_ring_od": 99.0, "slip_ring_len": 60.0,
    "base_w": 360.0, "base_d": 360.0, "base_h": 130.0,
    "mast_flange": "Ø 150 mm, 4 × M10 on PCD 110 mm (ASSUMPTION — mast interface not defined)",
}


def summary() -> dict:
    return {"outer_mm": OUTER, "inner_mm": {"w": W_IN, "h": H_IN, "d": D_IN},
            "stations_y": {"antenna": Y_ANT, "plate_front": Y_PLATE, "plate_rear": Y_PLATE_REAR, "main": Y_MAIN, "synth": Y_SYNTH, "power": Y_POWER, "rear_inner": Y_REAR_IN},
            "plate": PLATE, "fins": FIN, "antenna": {**ANT, **ANT_POS}, "pa_field": PA_FIELD, "pa_grid": PA_GRID,
            "main_pos": MAIN_POS, "synth_pos": synth_pos(), "power_pos": POWER_POS, "pedestal": PEDESTAL}


if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
