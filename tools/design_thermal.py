#!/usr/bin/env python3
"""PROPOSED DESIGN — thermal budget of the 16 × QPA2962 PA set and sizing of the 22 V drain supply.

Reads engineering/DESIGN/design_parameters.json and writes
engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md (+ thermal_summary.json).
All formulas are first-order engineering estimates (stated in the document);
no measurement was made.  Usage: python3 tools/design_thermal.py
"""
import datetime as _dt
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSN = os.path.join(ROOT, "engineering", "DESIGN")
OUT = os.path.join(DSN, "THERMAL")


def main() -> int:
    P = json.load(open(os.path.join(DSN, "design_parameters.json")))
    rf, tm, th, ps = P["rf"], P["timing"], P["thermal"], P["pa_supply"]
    v = lambda d: d["value"]
    date = _dt.date.today().isoformat()
    # ---- duty cycle from the firmware timing ----
    tx = v(tm["chirps_long"]) * v(tm["T1_us"]) + v(tm["chirps_short"]) * v(tm["T2_us"])
    frame = v(tm["chirps_long"]) * v(tm["PRI1_us"]) + v(tm["guard_us"]) + v(tm["chirps_short"]) * v(tm["PRI2_us"])
    duty_rf = tx / frame
    gate_overhead_us = 5.0  # drain switch on 5 µs before / off after each chirp (assumption)
    n_pulses = v(tm["chirps_long"]) + v(tm["chirps_short"])
    duty_gate = (tx + n_pulses * gate_overhead_us) / frame
    # ---- per-PA power ----
    vd, idq, pae = v(rf["pa_vd_v"]), v(rf["pa_idq_a"]), v(rf["pa_pae_pct"]) / 100
    psat_w = 10 ** (v(rf["pa_psat_dbm"]) / 10) / 1000
    pin_w = 10 ** (27 / 10) / 1000  # datasheet drive 27 dBm
    p_q = vd * idq
    p_dc_rf = (psat_w - pin_w) / pae
    p_diss_rf = p_dc_rf + pin_w - psat_w
    p_diss_on = max(p_q, p_diss_rf)
    n = v(rf["n_elements"])
    cases = {
        "A continuous drain bias (firmware as coded: VD left on)": p_diss_on * n,
        "B drain gated per chirp (D-14), duty %.1f %%" % (duty_gate * 100): p_diss_on * duty_gate * n,
        "C drain gated per CPI frame only (on during the 5.6 ms frame, off while the stepper moves)": p_diss_on * n * 0.9,
    }
    # ---- heat path per PA (case B) ----
    p_pa = p_diss_on * duty_gate
    r_pcb_via = 1.5   # °C/W through the PA board thermal-via field (ASSUMPTION; verify with PA board stack-up)
    r_tim = v(th["tim_r_c_per_w"])
    r_spread_local = 0.2
    dT_local = p_pa * (r_pcb_via + r_tim + r_spread_local)
    t_amb = v(th["ambient_max_c"])
    t_base_max = v(rf["pa_tbase_max_c"])
    t_plate_max = t_base_max - dT_local
    p_total_b = cases[list(cases)[1]]
    r_sa_required = (t_plate_max - t_amb) / p_total_b
    # fin field (two side strips on the 300 x 300 x 10 plate)
    fin_h, fin_t, fin_pitch, fin_len, strip_w = 25.0, 2.0, 4.0, 280.0, 55.0
    n_fins = int(strip_w // fin_pitch) * 2
    a_fin = n_fins * 2 * fin_h * fin_len * 1e-6 + 2 * strip_w * fin_len * 1e-6
    h_forced = 25.0  # W/m²K at ~2 m/s between fins (ASSUMPTION)
    r_sa_fins = 1 / (h_forced * a_fin)
    # lateral spreading from the PA field (centre 160 mm wide) to the strips: 10 mm Al, path ~100 mm, section 10 x 280
    k_al = 200.0
    r_spread_lat = (0.1 / (k_al * 0.010 * 0.280)) / 2
    r_total = r_spread_lat + r_sa_fins
    dT_plate = p_total_b * r_total
    t_plate = t_amb + dT_plate
    t_base = t_plate + dT_local
    # airflow
    rho, cp, dT_air = 1.1, 1005, 12.0
    q_air = p_total_b / (rho * cp * dT_air)              # m³/s
    q_cfm = q_air * 2118.88 * v(th["fan_margin"])
    q_air_A = cases[list(cases)[0]] / (rho * cp * dT_air) * 2118.88 * v(th["fan_margin"])
    # ---- 22 V supply ----
    id_max = v(rf["pa_id_max_a"])
    i_peak = n * id_max
    t_pulse = v(tm["T1_us"]) * 1e-6
    dv = 0.5
    c_bulk_total = i_peak * t_pulse / dv
    i_avg = n * idq * duty_gate + n * (p_dc_rf / vd - idq) * duty_rf
    p_avg = i_avg * vd
    vin_min = ps["vin_range_v"]["value"][0]
    eff = 0.92
    i_in_max = p_avg / (vin_min * eff)
    i_avg_A = n * idq + n * (p_dc_rf / vd - idq) * duty_rf
    os.makedirs(OUT, exist_ok=True)
    md = f"""# Thermal budget and 22 V PA supply sizing — DSN-THM-01 (PROPOSED DESIGN)

Rev A · {date} · generator `tools/design_thermal.py` · inputs `engineering/DESIGN/design_parameters.json` · decisions D-10, D-11, D-14. First-order estimates; no measurement.

## 1. Duty cycle from the firmware timing (`main.cpp:180-186`)

| Quantity | Value |
|---|---|
| TX time per beam position | {v(tm['chirps_long'])} × {v(tm['T1_us'])} µs + {v(tm['chirps_short'])} × {v(tm['T2_us'])} µs = **{tx:.1f} µs** |
| Frame per beam position | {v(tm['chirps_long'])} × {v(tm['PRI1_us'])} + {v(tm['guard_us'])} + {v(tm['chirps_short'])} × {v(tm['PRI2_us'])} = **{frame:.1f} µs** |
| RF duty | **{duty_rf*100:.2f} %** |
| Drain-gate duty (switch on {gate_overhead_us:.0f} µs around each chirp, assumption) | **{duty_gate*100:.2f} %** |

## 2. Dissipation per QPA2962 (datasheet: VD {vd} V, IDQ {idq} A, PSAT {v(rf['pa_psat_dbm'])} dBm, PAE {v(rf['pa_pae_pct'])} %)

| State | DC power | Dissipation |
|---|---|---|
| Quiescent, no RF | {p_q:.1f} W | **{p_q:.1f} W** |
| At PSAT (PIN 27 dBm) | {p_dc_rf:.1f} W | {p_diss_rf:.1f} W |
| Design value per PA while the drain is on | — | **{p_diss_on:.1f} W** |

## 3. System cases ({n} PAs)

| Case | Total PA dissipation | Verdict |
|---|---|---|
""" + "\n".join(f"| {k} | **{w:.0f} W** | {'INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ ' + format(q_air_A, '.0f') + ' CFM at ΔT_air 12 K)' if w > 300 else 'design case' if 'B ' in k else 'as A'} |" for k, w in cases.items()) + f"""

**Conclusion (D-10/D-14):** the firmware as coded (VD left on after bias-up, `main.cpp:1560-1601`) puts the head in case A. The proposal therefore requires per-chirp drain gating (D-14) — a hardware function (the 22 V switch module) driven by a timing line; after that the thermal design is case B: **{p_total_b:.0f} W** average.

## 4. Heat path, case B

| Element | Value | Basis |
|---|---|---|
| Average dissipation per PA | {p_pa:.2f} W | §1–2 |
| R(PA board thermal-via field) | {r_pcb_via} °C/W | ASSUMPTION — the RF_PA board stack-up and via field under U$1 must be checked (`engineering/PCB/RF_PA/`) |
| R(TIM) + local spreading | {r_tim} + {r_spread_local} °C/W | assumption (thermal pad 1–3 W/mK, 5 × 5 mm) |
| ΔT PA base → plate | {dT_local:.1f} °C | |
| Plate temperature allowed (TBASE ≤ {t_base_max} °C) | ≤ {t_plate_max:.0f} °C | datasheet |
| Required plate-to-air resistance at {t_amb} °C ambient | ≤ **{r_sa_required:.2f} °C/W** | (T_plate,max − T_amb)/P |
| Heat spreader (D-11) | 300 × 300 × {v(th['heat_spreader_thickness_mm'])} mm Al; PAs 4 × 4 on the rear centre; antenna panel on the front centre | `MECHANICAL/` |
| Fin fields | 2 side strips {strip_w:.0f} mm wide × {fin_len:.0f} mm, {n_fins} fins {fin_h:.0f} × {fin_t:.0f} mm at {fin_pitch:.0f} mm pitch, area {a_fin:.2f} m² | D-11 |
| R(lateral spreading, 10 mm Al, ~100 mm, both sides) | {r_spread_lat:.2f} °C/W | k = {k_al:.0f} W/mK |
| R(fins → air, forced, h = {h_forced:.0f} W/m²K) | {r_sa_fins:.2f} °C/W | ASSUMPTION h |
| Resulting plate / PA base temperature | **{t_plate:.0f} °C / {t_base:.0f} °C** at {t_amb} °C ambient | margin to 85 °C: {t_base_max - t_base:.0f} °C |
| Airflow for ΔT_air = {dT_air:.0f} K with margin ×{v(th['fan_margin'])} | **{q_cfm:.0f} CFM** ({q_air*1000*v(th['fan_margin']):.1f} L/s) → 2 × 60 mm fans (≥ 15 CFM each) in the side ducts, intake bottom, exhaust top, controlled by the existing fan relay (xlsx row 64) | |

Not included: Power Board regulator losses (currents UNKNOWN), Main Board (FPGA/ADC/clock ≈ 10–20 W estimate), solar load on the radome — add a 30 % margin when selecting the fans.

## 5. 22 V drain supply (D-14)

| Quantity | Value |
|---|---|
| Peak drain current (all 16 PAs at ID_max {id_max} A) | **{i_peak:.1f} A** during each {v(tm['T1_us'])} µs chirp |
| Average current, case B (IDQ × gate duty + RF increment × RF duty) | **{i_avg:.2f} A** → {p_avg:.0f} W |
| Average current, case A (continuous bias) | {i_avg_A:.1f} A → {i_avg_A*vd:.0f} W (not supported by the proposal) |
| Bulk capacitance for ΔV ≤ {dv} V over a chirp (total) | **{c_bulk_total*1e6:.0f} µF** → ≥ 220 µF low-ESR polymer per PA board (local, {c_bulk_total*1e6/n:.0f} µF each) + 2 × 1000 µF/35 V at the switch module |
| Input current at VIN_min {vin_min} V, η {eff:.0%} | {i_in_max:.1f} A average (case B) |
| Converter | synchronous boost 12–17 V → 22 V, 2-phase interleaved (LM5122 ×2 or equivalent), 150 W continuous rating, 300 kHz, 2 × 10 µH / 15 A inductors, output ripple < 100 mV |
| Protection / enable | LM5069 hot-swap controller + N-FET high-side switch on the 22 V bus, EN from `EN/DIS_RFPA_VDD` (STM32), current limit 12 A average, dv/dt-limited turn-on; status to the MCU |
| Per-PA pulse gating | 16 × high-side P-FET (−40 V, 30 A pulsed) with fast high-side driver (e.g. LTC7003, ≤ 100 ns), common `TX_GATE` TTL input from the FPGA (spare I/O to be allocated — UNRESOLVED), local 220 µF per channel |
| Sequencing | VG (−4 V via DAC5578) before VD (firmware already does this); gate switch only after `EN/DIS_RFPA_VDD`; power-down reverse |

See `../ELECTRICAL/PA_SUPPLY_22V/` for the block schematic, netlist and BOM.
"""
    open(os.path.join(OUT, "THERMAL_AND_PA_SUPPLY.md"), "w", encoding="utf-8").write(md)
    json.dump({"duty_rf": duty_rf, "duty_gate": duty_gate, "p_diss_on_w": p_diss_on, "cases_w": cases, "p_total_case_b_w": p_total_b,
               "t_plate_c": t_plate, "t_base_c": t_base, "airflow_cfm": q_cfm, "i_peak_a": i_peak, "i_avg_a": i_avg,
               "c_bulk_uF": c_bulk_total * 1e6, "fins": {"n": n_fins, "h": fin_h, "t": fin_t, "pitch": fin_pitch, "len": fin_len, "strip_w": strip_w}},
              open(os.path.join(OUT, "thermal_summary.json"), "w"), indent=2)
    print(f"duty RF {duty_rf*100:.2f}% gate {duty_gate*100:.2f}%; per PA on {p_diss_on:.1f} W; case A {cases[list(cases)[0]]:.0f} W, case B {p_total_b:.0f} W; "
          f"plate {t_plate:.0f} C base {t_base:.0f} C; {q_cfm:.0f} CFM; peak {i_peak:.1f} A avg {i_avg:.2f} A; bulk {c_bulk_total*1e6:.0f} uF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
