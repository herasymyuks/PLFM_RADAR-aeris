# Manual validation record

Date 2026-10-09 · Antidrone Ukraine · antidrone.cc · build .

| Check | Command | Result |
|---|---|---|
| Chapters present, no stubs, figures exist, links resolve | `python3 tools/build_manual.py --check` | chapters: 22, figures: 69, problems: 0 |
| Repository-wide link check restricted to manual/ | `python3 tools/check_doc_links.py` | 0 broken links under manual/ (after path fixes) |
| Figure log (status per caption, missing files) | `python3 tools/gen_figure_log.py` | 69 figures, 0 missing; 30 SOURCE-DERIVED, 20 PROPOSED DESIGN, 7 BETA, 7 PARTIAL, 3 ORIGINAL PROJECT FILE, 2 CONCEPTUAL, 0 VERIFIED |
| Build outputs | `python3 tools/build_manual.py` | `manual/AERIS10_MANUAL.md` (   97614 words), `manual/build/AERIS10_MANUAL.html` (64 MB, images embedded), `manual/build/AERIS10_MANUAL.pdf` (191 pages A4, 44 MB; pdfimages: 86 embedded images) |
| Authorship on every page | pdftotext count of "antidrone.cc" | 218 occurrences (title page, running header/footer, figure plots) |
| Drawing register consistency | `python3 tools/gen_drawing_register.py --check` | 89 drawings, 0 file problems |

## Claims flagged by the chapter authors as derived or unsourced (kept in the text with their labels)

- MAN-01 scan-angle statements contradict each other across README (±45°), parameter_table (≈±33°), 02_hardware/04 (±62.7° then ±33°) and 03_beamforming_theory (λ/2 grating-lobe-free); the arcsin(160/180) arithmetic is the manual's own.
- MAN-02 "10→30 MHz … 20 MHz span" is a subtraction of beta README values; B remains TBD (50 MHz ASSUMED in the range calculation).
- MAN-03 two CBL numbering schemes (interconnection table CBL-00…106 vs harness schedule CBL-001…144).
- MAN-04 stale statements in beta READMEs about the bridge v2 implementation — corrected in the repository on 2026-10-09 after the chapters were written; the manual text notes the correction.
- Nexus 1 W/element "10 dB lower" remark, T_c ratio 60, harness group counts, BOM confidence counts, CHANGELOG class counts — arithmetic/counts by the authors from cited rows.
- Assembly torques (0.5 N·m M3, 0.9 N·m SMA), tolerances (±2 mm coax, ±10 % IDQ, < 0.1 mm play, ±0.5 mm squareness) come only from manual/ASSEMBLY_STEPS_SOURCE.md — ASSUMED, no repository specification.
- GUI figure F13.3 is the matplotlib canvas saved off-screen, not a window screenshot.
- Rev. B (chapter 9): the bank-35 fan-out redo decided by the owner was still in progress when the chapters were written; the chapter states that no redone fan-out exists in the repository at the time of writing.
- Chapter 11 synthesis numbers are from snapshot 65cd160 (before the command-set-v2 edits); re-run `beta/fpga_synth/run_synth.sh` after each RTL change.
- Observations: pdftoppm of KiCad assembly PDFs needed the autoscale fix (applied); POWER_SUPPLY FAB_NOTES §3 repeats RF template text; 220 µF per-PA bulk capacitor of the proposal is not on the RF_PA schematic; window clamp screw count differs between the parts-list table (16) and the sealing text (18).

## Not validated

Nothing in the manual is hardware-verified; no procedure was executed on a physical radar; the PDF was not proof-read page by page (spot checks: title page, chapter 4 schematic page, step 15.1 page).
