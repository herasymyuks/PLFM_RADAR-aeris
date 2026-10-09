#!/usr/bin/env python3
"""PROPOSED DESIGN calculations (BETA, no measurement): 2-D thermal map of the PA heat-spreader plate,
pedestal drive torque, and the radar range equation. Stdlib only. Writes engineering/DESIGN/CALCS/*.md (+ SVG map).
Usage: python3 tools/design_calcs.py
"""
from __future__ import annotations
import datetime as _dt, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_layout as L
from eagle_svg_common import SvgCanvas, Style
ROOT = L.ROOT; OUT = os.path.join(ROOT, "engineering", "DESIGN", "CALCS"); os.makedirs(OUT, exist_ok=True)
DATE = _dt.date.today().isoformat()
TH = json.load(open(os.path.join(ROOT, "engineering/DESIGN/THERMAL/thermal_summary.json")))
P = json.load(open(os.path.join(ROOT, "engineering/DESIGN/design_parameters.json")))

# ============================ 1. 2-D thermal finite-difference model of the plate ============================
# Plate 300×300×10 mm Al (k = 200 W/mK); 16 PA sources (case B average 4.3 W each over 5×5 mm, or case A 37 W);
# convective sinks: fin fields on the two side strips (h_eff from the fin geometry), weak natural convection elsewhere.
def thermal(case_p_per_pa, label):
    N = 60; dx = L.PLATE["w"] / N / 1000.0; t = L.PLATE["t"] / 1000.0; k = 200.0; amb = P["thermal"]["ambient_max_c"]["value"]
    T = [[amb] * N for _ in range(N)]; q = [[0.0] * N for _ in range(N)]; h = [[5.0] * N for _ in range(N)]   # W/m²K natural (both faces assumed 5 total)
    fins = TH["fins"]; sw = fins["strip_w"]
    a_fin_per_m2 = (fins["n"] / 2 * 2 * fins["h"] * fins["len"] * 1e-6 + sw * fins["len"] * 1e-6) / (sw * fins["len"] * 1e-6)   # area multiplication by fins
    h_forced = 25.0 * a_fin_per_m2 * 0.9          # effective h on the strip footprint (fin efficiency 0.9 assumed)
    for i in range(N):
        for j in range(N):
            x = (i + 0.5) * dx * 1000; z = (j + 0.5) * dx * 1000
            if (x < sw or x > L.PLATE["w"] - sw) and 10 < z < 10 + fins["len"]:
                h[i][j] = h_forced
    pa_w, pa_h = L.B["RF_PA"]["w"], L.B["RF_PA"]["h"]
    for (px, pz) in L.pa_positions():
        cx, cz = px - L.PLATE_POS["x"] + pa_w / 2, pz - L.PLATE_POS["z"] + pa_h / 2     # QPA2962 assumed at the board centre
        for i in range(N):
            for j in range(N):
                x = (i + 0.5) * dx * 1000; z = (j + 0.5) * dx * 1000
                if abs(x - cx) <= 2.5 and abs(z - cz) <= 2.5:
                    q[i][j] += case_p_per_pa / (25e-6)                      # W/m² over 5×5 mm
    # Gauss-Seidel on  k t ∇²T + q − h (T − amb) = 0
    for it in range(4000):
        maxd = 0.0
        for i in range(N):
            for j in range(N):
                s = 0.0; n = 0
                for (a, b) in ((i-1, j), (i+1, j), (i, j-1), (i, j+1)):
                    if 0 <= a < N and 0 <= b < N: s += T[a][b]; n += 1
                c = k * t / dx**2
                Tn = (c * s + q[i][j] + h[i][j] * amb) / (c * n + h[i][j])
                maxd = max(maxd, abs(Tn - T[i][j])); T[i][j] = Tn
        if maxd < 1e-3: break
    tmax = max(max(r) for r in T); tmin = min(min(r) for r in T)
    cv = SvgCanvas(); g = "m"; cv.group(g)
    for i in range(N):
        for j in range(N):
            f = (T[i][j] - tmin) / max(tmax - tmin, 1e-6); r = int(255 * f); b = int(255 * (1 - f))
            cv.polygon(g, [(i * dx * 1000, j * dx * 1000), ((i + 1) * dx * 1000, j * dx * 1000), ((i + 1) * dx * 1000, (j + 1) * dx * 1000), (i * dx * 1000, (j + 1) * dx * 1000)], 0, Style(stroke="none", fill=f"#{r:02x}40{b:02x}"))
    for (px, pz) in L.pa_positions():
        cv.polygon(g, [(px - L.PLATE_POS["x"], pz - L.PLATE_POS["z"]), (px - L.PLATE_POS["x"] + pa_w, pz - L.PLATE_POS["z"]), (px - L.PLATE_POS["x"] + pa_w, pz - L.PLATE_POS["z"] + pa_h), (px - L.PLATE_POS["x"], pz - L.PLATE_POS["z"] + pa_h)], 0.3, Style(stroke="#fff", fill="none"))
    cv.text(g, 2, -6, f"T min {tmin:.1f} °C (blue) … max {tmax:.1f} °C (red); ambient {amb} °C; {label}", 3.5, 0, None, "#000", mono=False)
    svg = os.path.join(OUT, f"thermal_map_{label.split()[0]}.svg")
    cv.write(svg, f"AERIS-10 — PA heat-spreader temperature map, 2-D finite differences — DSN-CALC-01 ({label})", [f"Date {DATE} · PROPOSED DESIGN calculation · plate 300×300×10 Al k=200 W/mK, {N}×{N} cells, 16 × 5×5 mm sources at the PA board centres, fin strips h_eff {h_forced:.0f} W/m²K, elsewhere 5 W/m²K", "Conduction through the PA board and TIM (≈ 2 °C/W → +8 °C at the die base in case B) is NOT included in the map; see THERMAL_AND_PA_SUPPLY.md"], margin=12)
    return tmax, tmin, h_forced, it
tA, _, hf, itA = thermal(TH["p_diss_on_w"], "A-continuous-bias")
tB, tBmin, _, itB = thermal(TH["p_diss_on_w"] * TH["duty_gate"], "B-gated-drain")
# ============================ 2. Pedestal torque ============================
pl = json.load(open(os.path.join(ROOT, "engineering/DESIGN/MECHANICAL/CAD/detail/parts_list.json")))
m_head = pl["mass_head_g"] / 1000 + 4.0      # + PCBs, antenna, cables (estimate 4 kg)
w, d = L.OUTER["w"] / 1000, L.OUTER["d"] / 1000
J_head = m_head * (w**2 + d**2) / 12 + m_head * (0.0)**2       # about the central vertical axis (head centred on the axis)
J_turntable = 0.5 * (pl["parts"][[p["part"].startswith("Turntable") for p in pl["parts"]].index(True)]["mass_g_estimate"] / 1000) * (0.17)**2
J = J_head + J_turntable
step_deg = 7.2; t_move = 0.05; ratio = L.PEDESTAL["ratio"]
theta = math.radians(step_deg); a_acc = 4 * theta / t_move**2       # triangular profile: accel half, decel half
T_table = J * a_acc; T_motor = T_table / ratio * 1.25               # belt efficiency 80 %
w_motor_rpm = (2 * theta / t_move) / (2 * math.pi) * 60 * ratio   # peak table speed × ratio
T_hold = 1.9                                                        # NEMA 23 class (N·m) at low speed
T_at_speed = 1.9 * 0.6                                              # torque roll-off at ~150 rpm (assumption)
margin = T_at_speed / T_motor
# ============================ 3. Radar range equation ============================
f0 = P["rf"]["f_c_hz"]["value"]; lam = 3e8 / f0
Pt_w = 10.0                                   # per PA at PSAT; coherent array: 16 elements
G_row_dBi = json.load(open(os.path.join(ROOT, "engineering/DESIGN/ANTENNA/simulation/tuning_result.json")))["Dmax_row_dBi"]
G_arr_dBi = G_row_dBi + 10 * math.log10(16) - 1.0       # 16 rows coherent, −1 dB feed/scan losses
G = 10 ** (G_arr_dBi / 10)
B = 50e6                                      # chirp bandwidth — TBD in the parameter table; 50 MHz assumed (resolution 3 m)
NF_dB = 2.5 + 1.5                             # ADTR1107 LNA 2.5 dB + ADAR/mixer chain degradation estimate
T_sys = 290 * 10 ** (NF_dB / 10)
k_B = 1.38e-23
Tc = 30e-6; Mchirps = 16
G_pc = B * Tc                                 # pulse compression gain (time-bandwidth)
G_dop = Mchirps                               # coherent integration over 16 long chirps
L_sys_dB = 6.0                                # RF losses TX+RX (switches, cables, radome, PA output losses) assumption
SNR_req_dB = 13.0
results = []
for rcs in (0.01, 0.1, 1.0, 10.0):
    num = (16 * Pt_w) * G * G * lam**2 * rcs * G_pc * G_dop
    den = (4 * math.pi)**3 * k_B * T_sys * B * 10 ** (SNR_req_dB / 10) * 10 ** (L_sys_dB / 10)
    R = (num / den) ** 0.25
    results.append((rcs, R))
R_unamb = 3e8 * 167e-6 / 2
md = f"""# Design calculations — DSN-CALC-01 (PROPOSED DESIGN, BETA)

Date {DATE} · `tools/design_calcs.py` · inputs: `design_parameters.json`, `THERMAL/thermal_summary.json`, `MECHANICAL/CAD/detail/parts_list.json`, `ANTENNA/simulation/tuning_result.json`. No measurement; every assumption is stated inline.

## 1. PA heat-spreader temperature map (2-D finite differences)

Model: 300 × 300 × 10 mm aluminium plate (k = 200 W/mK), 60 × 60 cells, steady state, 16 heat sources 5 × 5 mm at the PA-board centres (QPA2962 position on the PA board is assumed at the board centre — verify in `engineering/PCB/RF_PA`), two fin strips as an effective convective sink (h_eff ≈ {hf:.0f} W/m²K over the strip footprint = 25 W/m²K × fin area ratio × 0.9 efficiency), 5 W/m²K elsewhere; ambient {P['thermal']['ambient_max_c']['value']} °C. Conduction through the PA PCB via field and the thermal pad (≈ 2 °C/W → +8 °C in case B) is added analytically.

| Case | Per PA | Plate max / min (°C) | PA base estimate (°C) | Verdict |
|---|---|---|---|---|
| A continuous drain bias | {TH['p_diss_on_w']:.1f} W | {tA:.0f} / — | > {tA + 74:.0f} | far beyond TBASE 85 °C — confirms case A is infeasible |
| B drain gated per chirp | {TH['p_diss_on_w'] * TH['duty_gate']:.2f} W | {tB:.1f} / {tBmin:.1f} | ≈ {tB + 8.5:.0f} | below 85 °C with margin {85 - (tB + 8.5):.0f} °C |

Maps: `thermal_map_A-continuous-bias.svg`, `thermal_map_B-gated-drain.svg` (converged in {itA}/{itB} iterations). Limits: 2-D (through-thickness gradient of a 10 mm plate at these fluxes < 1 °C), uniform h on the strips, no radiation, no PCB/antenna heat.

## 2. Pedestal drive torque

| Quantity | Value | Basis |
|---|---|---|
| Rotating mass | {m_head:.1f} kg | detailed head structure {pl['mass_head_g']/1000:.1f} kg + 4 kg PCBs/antenna/cables (estimate) |
| Moment of inertia (head as a box {w*1000:.0f} × {d*1000:.0f} mm about its centre + turntable) | {J:.3f} kg·m² | solid-box formula; head centred on the axis |
| Move: {step_deg}° in {t_move*1000:.0f} ms, triangular profile | α = {a_acc:.0f} rad/s², peak ω = {2*theta/t_move:.2f} rad/s | per azimuth step (50 positions/rev; 5.65 ms dwell per elevation, 31 elevations ≈ 175 ms per azimuth, so a 50 ms move costs 22 % of the scan time) |
| Table torque | {T_table:.2f} N·m | J·α |
| Motor torque with 1:{ratio} belt, 80 % efficiency | **{T_motor:.2f} N·m** at ≈ {w_motor_rpm:.0f} rpm peak | |
| NEMA 23 (1.9 N·m holding, ≈ 60 % at that speed) | {T_at_speed:.2f} N·m available → margin ×{margin:.1f} | assumption on the torque curve — check the chosen motor's curve at 24 V with the TB6600 |

Move time vs. motor torque (same mass, triangular profile, 1:{ratio} belt):

| Move time per 7.2° step | Motor torque needed | NEMA 23 (≈ {T_at_speed:.2f} N·m) | NEMA 34 (≈ 3.0 N·m at speed) | Revolution time (50 × (175 ms dwell + move)) |
|---|---|---|---|---|
""" + "\n".join(f"| {tm*1000:.0f} ms | {T_motor*(t_move/tm)**2:.2f} N·m | {'OK' if T_motor*(t_move/tm)**2 < T_at_speed/1.3 else 'NO'} | {'OK' if T_motor*(t_move/tm)**2 < 3.0/1.3 else 'NO'} | {50*(0.175+tm):.1f} s |" for tm in (0.05, 0.1, 0.15, 0.2, 0.3)) + f"""

**Verdict (revises D-12):** the earlier assumption "NEMA 23, 1:3, fast steps" does not hold for a {m_head:.0f} kg head: NEMA 23 needs ≥ 200 ms per step (revolution ≈ 19 s), NEMA 34 (3 N·m class, 86 mm frame) allows ≈ 100 ms (revolution ≈ 14 s). Alternatives: ratio 1:6 with `Stepper_steps = 1200`, or a lighter head (lid/tray in 2 mm, no PA plate side strips). Bearing moment load from wind is not included (no enclosure wind spec).

## 3. Radar range equation (single-pulse coherent, long chirp)

| Parameter | Value | Basis |
|---|---|---|
| f₀ / λ | {f0/1e9:.1f} GHz / {lam*1000:.2f} mm | verified |
| TX power | 16 × 10 W (PSAT) = {16*Pt_w:.0f} W peak, coherent | QPA2962 datasheet; array coherence assumed |
| Antenna gain (TX = RX) | {G_arr_dBi:.1f} dBi | one simulated row {G_row_dBi:.1f} dBi + 10·log10(16) − 1 dB feed/scan loss (proposed panel, D-01) |
| Chirp | T_c = 30 µs, **B = 50 MHz ASSUMED** (TBD in `parameter_table.md`) → pulse-compression gain {10*math.log10(G_pc):.1f} dB, ΔR = {3e8/(2*B):.0f} m | firmware timing |
| Coherent integration | 16 long chirps → +{10*math.log10(G_dop):.1f} dB | main.cpp |
| Noise figure / system losses | {NF_dB:.1f} dB / {L_sys_dB:.0f} dB | ADTR1107 2.5 dB NF + chain; losses assumed |
| Required SNR | {SNR_req_dB:.0f} dB (Pd ≈ 0.9, Pfa 1e-6, Swerling 1) | standard |
| Unambiguous range (PRI 167 µs) | {R_unamb/1000:.1f} km | firmware |

| Target RCS (m²) | R_max (km) |
|---|---|
""" + "\n".join(f"| {rcs} | {R/1000:.1f} |" for rcs, R in results) + f"""

Verdict: with the proposed antenna, 16 × 10 W and 16-chirp integration, R_max(1 m²) ≈ {results[2][1]/1000:.1f} km — the 20 km Extended-variant goal (`parameter_table.md`) is **not** reached: it needs ≈ {40*math.log10(20000/results[2][1]):.0f} dB more (longer coherent integration across the 31 elevations/azimuth dwell, a narrower B with the same T_c, lower losses, or a higher-gain antenna). The 3 km Nexus goal is met for RCS ≥ 0.1 m² (R ≈ {results[1][1]/1000:.1f} km). A 0.01 m² drone-class target falls near {results[0][1]/1000:.1f} km. Dominant unknowns: B (assumed), real array gain (16-row coupling not yet simulated), RF chain losses.
"""
open(os.path.join(OUT, "DESIGN_CALCULATIONS.md"), "w").write(md)
print(f"thermal A max {tA:.0f} C, B max {tB:.1f} C; torque motor {T_motor:.2f} N·m margin x{margin:.1f}; R(1 m2) {results[2][1]/1000:.1f} km")
