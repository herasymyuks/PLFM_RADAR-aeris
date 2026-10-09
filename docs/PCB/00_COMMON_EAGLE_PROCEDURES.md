# Common PCB Procedures (EAGLE / Fusion 360 Electronics / KiCad) — AERIS-10

All four boards are Autodesk EAGLE XML files (`<!DOCTYPE eagle SYSTEM "eagle.dtd">`). Versions: Main Board 7.4.0 (sch+brd), Frequency Synthesizer 9.6.2, RF PA 9.6.2, Power Board **sch 9.6.2 / brd 7.4.0** (mismatch). Libraries are embedded in every file (no external `.lbr` needed). Autodesk ended EAGLE sales in 2026; EAGLE 9.6.2 Free/Standard still opens all of them, as does Fusion 360 Electronics; KiCad 7/8/9 imports EAGLE 6+ XML.

The procedures below are the exact menu paths of the stated versions. Output file names are the tools' defaults; where the AERIS-10 project never produced them, the names are **expected**, not observed.

---

## P-EAGLE-01 — Open and consistency-check a board pair

- **Software:** EAGLE 9.6.2 (Windows/macOS/Linux). EAGLE 7.4 cannot open the 9.6.2 files.
- **Procedure:** File → Open → Schematic (`.sch`); the board opens automatically when the `.brd` with the same base name is in the same folder. Confirm the title bar shows both windows and no "forward/back annotation severed" dialog. If the dialog appears (expected for Power Board: sch 9.6.2 vs brd 7.4.0), run in the schematic command line `ERC` and in the board `DRC` and compare the part/net lists (use `EXPORT NETLIST` in both; or `tools/extract_eagle_netlist.py --list-parts` on the `.sch` and the `elements` of the `.brd`).
- **Verification:** ERC → *Consistency check* reports "Board and schematic are consistent".
- **Troubleshooting:** inconsistency → use the schematic as master, delete the board's stale items only with the designer's approval.

## P-EAGLE-02 — ERC

- **Procedure:** schematic window → Tools → ERC (or type `ERC`). Review every entry; "approved" entries (stored in the file as `<approved hash=...>`) were waived by the author without text — reopen each.
- **Expected output:** `ERC: no errors` or a list; save the report with *File → Export → ...* is not available for ERC, so screenshot or copy the list into `docs/PCB/reports/<board>_ERC_<date>.txt` (directory to be created; does not exist yet).
- **Acceptance:** 0 errors; every warning dispositioned in writing.

## P-EAGLE-03 — DRC with the stored design rules

- **Procedure:** board window → Tools → DRC → *Load...* is not needed (rules are stored in the `.brd` `<designrules>`), → *Check*. The DRU names in the files are `PCBWay_8L_100um-Track` (Main; note the board has 10 copper layers), `PCBWay_6L_100um-Track` (Synth), `PCBWay_4L_100um-Track` (RF PA), `PCBWay_2L_100um-Track` (Power).
- **Before checking:** type `RATSNEST` and read the status bar: "Ratsnest: Nothing to do" means fully routed; "N airwires" means unrouted connections. The Main Board stores 2 390 airwires (2 354 on GND, 33 on +3V3_FPGA, 3 on +3V3_FT) and the Power Board 309 — these are expected to show.
- **Expected output:** DRC error list; export with *DRC → Errors* → right-click → *Export*… (EAGLE 9) or manual transcription.
- **Acceptance:** 0 unapproved errors; each approved error justified in `docs/PCB/reports/` (directory to be created).

## P-EAGLE-04 — Gerber + drill export (EAGLE 9.6.2 CAM Processor)

- **Procedure:** board window → File → CAM Processor… → *Load Job File* → *Templates* → choose the template matching the layer count (`2 Layer`, `4 Layer`, `6 Layer`; for the 10-layer Main Board start from `6 Layer` and add layers 3,4,5,12,13,14 as *Copper → Inner* in the *Gerber* section, each with the inner layer number). In *Output* set *Export as ZIP*, Gerber format RS-274X, units mm, 4.4 decimal, *Drill* section Excellon with *Drill unit mm*, PTH and NPTH as separate files. Press *Process Job*.
- **Expected output (defaults of 9.6.2):** `CAMOutputs/GerberFiles/copper_top.gbr, copper_bottom.gbr, copper_inner_<n>.gbr, soldermask_top.gbr, soldermask_bottom.gbr, silkscreen_top.gbr, silkscreen_bottom.gbr, solderpaste_top.gbr, solderpaste_bottom.gbr, profile.gbr`, `CAMOutputs/DrillFiles/drill_1_16.xln` (plated), `drill_1_16_npth.xln` or `drill_npth.xln`, plus `gerber_job.gbrjob`. Store under `4_Schematics and Boards Layout/4_7_Production Files/<Board>/Gerber/`.
- **Verification:** open the set in a Gerber viewer (`gerbv`, KiCad GerbView, or the fab's online viewer); layer count and outline dimensions must match `docs/MECHANICAL/drawings/<BOARD>_outline.svg`; drill count must match the via/hole counts in `docs/PCB/<BOARD>.md`.
- **Troubleshooting:** missing inner layers in the template → add them manually; mirrored bottom layers are a viewer setting, not an error.

## P-EAGLE-05 — Gerber + drill export (EAGLE 7.4 CAM Processor, for the 7.4.0 files)

- **Procedure:** File → CAM Processor → File → Open → Job → `gerb274x.cam` (2-layer) or build a job with one section per layer: *Device* GERBER_RS274X, *File* `%N.<ext>`, layers as below; then `excellon.cam` for drills (Device EXCELLON, file `%N.drd`, layers 44 Drills + 45 Holes).
- **Expected output:** `<board>.cmp` (top copper), `.sol` (bottom), `.ly2..` (inner), `.plc/.pls` (silk), `.stc/.sts` (mask), `.crc/.crs` (paste), `.gko` or outline from layer 20, `.drd` + `.dri` drill.
- **Note:** EAGLE 7.4 is end-of-life; prefer opening in 9.6.2 (it upgrades 7.4 files on load) unless the designer requires 7.4.

## P-KICAD-01 — Alternative export through KiCad 8/9 (open-source path)

- **Procedure:** KiCad → File → Import → Non-KiCad Project → *EAGLE project* → select the `.sch` (the `.brd` is imported together). Save the project. Open the PCB editor → Inspect → DRC (set rules per the PCBWay DRU values listed in each board document) → File → Fabrication Outputs → Gerbers (Protel extensions, X2 attributes, include netlist) → *Plot* → *Generate Drill Files* (Excellon, mm, PTH/NPTH separate). Command line: `kicad-cli pcb export gerbers --board-plot-params -o out/ board.kicad_pcb` and `kicad-cli pcb export drill -o out/ board.kicad_pcb`.
- **Caveat:** the EAGLE importer approximates polygons, thermals and some DRU settings; the imported board must be re-DRC'd and compared with the EAGLE output before use. The 10-layer Main Board layer setup must be re-entered in Board Setup → Physical Stackup.
- **Expected output:** `board-F_Cu.gbr, board-B_Cu.gbr, board-In1_Cu.gbr ..., board-F_Mask.gbr, board-Edge_Cuts.gbr, board-PTH.drl, board-NPTH.drl, board-job.gbrjob`.

## P-EAGLE-06 — BOM export

- **Procedure:** schematic → File → Run ULP → `bom.ulp` → *List type: Parts* or *Values*, *Output format: CSV*, tick all attributes → *Save*. Compare with `docs/BOM/BOM_<BOARD>.csv` generated by `tools/gen_eagle_bom.py` (same source, no EAGLE needed).
- **Acceptance (BOM validation):** every line has a manufacturer part number (MPN) and a package; passives have values (the schematics currently leave 244/80/6/47 references without a value — Main/Power/PA/Synth); quantities match the reference count; connectors and mechanical parts included; a "do-not-populate" column exists.

## P-EAGLE-07 — Pick-and-place and assembly drawing

- **Pick-and-place:** board → File → Run ULP → `mountsmd.ulp` → produces `<board>-smd.mnt` (and `mount.ulp` for THT). Format: `RefDes,Value,Package,X,Y,Rot,Side` (verified on the existing Frequency Synthesizer files).
- **Assembly drawing:** board → Layer settings: show only 20 Dimension, 21 tPlace, 25 tNames, 51 tDocu (and bottom equivalents) → File → Print → PDF, scale 1:1, with *Black* and *Caption*. Expected `<board>_assembly_top.pdf`, `<board>_assembly_bottom.pdf`.
- **Fabrication drawing:** same, layers 20 + 44 Drills + 45 Holes + dimension annotations (use `DIMENSION` tool on layer 48 Document) + a text block with: layer count, material, finished thickness, copper weight, finish, mask/silk colours, impedance table (from `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf`), minimum track/space (0.1 mm per DRU), minimum drill (0.15 mm Main/Synth/PA; 0.3 mm Power). Expected `<board>_fab.pdf`.

## P-EAGLE-08 — Schematic PDF export

- **Procedure:** schematic → File → Print → *Printer: PDF*, *All sheets*, *Fit to page*, *Black*, *Caption* → `<board>_schematic.pdf`. Store under `docs/PCB/schematics/` (not generated here: EAGLE is not installed on the authoring machine).

## P-EAGLE-09 — Netlist export (for cross-checks without EAGLE)

- `python3 tools/extract_eagle_netlist.py <sch> --part <REF> --out <csv>` gives net ↔ pin ↔ pad for any part; `--list-parts` lists all parts. EAGLE alternative: schematic → File → Export → Netlist (or `EXPORT NETSCRIPT`).

## Manufacturing package structure (expected per board)

```
4_7_Production Files/<Board>/
├── Gerber/        copper_*.gbr, soldermask_*.gbr, silkscreen_*.gbr, solderpaste_*.gbr, profile.gbr, *.gbrjob
├── Drill/         drill_*_pth.xln, drill_npth.xln, drill map pdf
├── <Board>_fab.pdf
├── <Board>_assembly_top.pdf, <Board>_assembly_bottom.pdf
├── <Board>_BOM.csv            (with MPN, manufacturer, DNP)
├── <Board>-smd.mnt, <Board>-tht.mnt
├── <Board>_schematic.pdf
├── <Board>_netlist.ipc (IPC-D-356, optional) 
└── reports/ ERC, DRC, impedance/stack-up confirmation from the fab
```
