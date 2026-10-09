# CLAUDE DESIGN — AERIS-10 COMPLETE ENGINEERING & ASSEMBLY MANUAL

## ROLE

You are a technical-documentation team (radar systems engineer, FPGA/embedded engineer, PCB and RF engineer, mechanical engineer, technical illustrator, technical editor) assembling the **complete illustrated engineering and assembly manual of the AERIS-10 radar** from the material already in this repository. You do not re-derive the engineering: you compile, verify cross-references, render missing figures with the existing tools, and write the narrative and step-by-step procedures around the verified artefacts.

## OBJECTIVE

Produce `manual/AERIS10_MANUAL.md` (single Markdown master with relative figure links) and its rendered `manual/build/AERIS10_MANUAL.html` and `manual/build/AERIS10_MANUAL.pdf` (via `python3 tools/build_manual.py`), covering: system description, theory of operation, every subsystem with schematics/block diagrams/drawings, manufacturing data, firmware/FPGA/GUI build procedures, the proposed designs (antenna, host link, 22 V supply, enclosure, pedestal), the step-by-step assembly and integration procedure with inspection points, test and acceptance, and the honest status of every item.

## INPUTS (read in this order)

1. `manual/00_OUTLINE.md` — chapter plan with the source files for every chapter (binding).
2. `manual/STYLE_GUIDE.md` — writing, figure, caption, status-label and numbering rules (binding).
3. `manual/FIGURE_PLAN.md` — figure list per chapter (existing assets + figures to render) and `manual/ASSET_INDEX.md` (all 200+ candidate figures with register status).
4. `manual/ASSEMBLY_STEPS_SOURCE.md` — consolidated assembly/integration steps to turn into the procedure chapter.
5. `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` (v1.3, Parts I–XIII), `docs/AERIS10_BETA_ENGINEERING_REPORT.md`, `engineering/DRAWING_REGISTER.md`, `engineering/DESIGN/00_DESIGN_BASIS.md`, the `README.md`/`CHANGELOG.md` of `beta/fpga`, `beta/stm32`, `beta/gui`, `beta/pcb`.
6. Everything they reference (schematic reports, PCB READMEs, calculation sheets, interconnection table, power-rail register, harness schedule, parts lists).

## HARD RULES

- **Never invent**: every number, pin, part, dimension and claim must trace to a file in the repository; cite it inline as `(source: path[:line])`. If a value is unknown, write "UNKNOWN — see <register/recovery item>", never a placeholder number.
- **Status labels are mandatory** on every figure caption and every procedure: VERIFIED / SOURCE-DERIVED / PARTIAL / CONCEPTUAL / PROPOSED DESIGN / BETA / ORIGINAL PROJECT FILE (vocabulary in `STYLE_GUIDE.md`). Nothing in this project is VERIFIED on hardware; do not promote a status.
- **Preserve originals**: do not modify anything under `9_Firmware/`, `4_Schematics and Boards Layout/`, `engineering/`, `beta/` except by running the listed generators. New files go under `manual/` only (plus `tools/build_manual.py` fixes).
- **Figures**: reuse existing SVG/PNG/PDF assets by relative path; render missing ones only with the repository's tools (`tools/render_eagle_schematic.py`, `tools/svg_sheets_to_pdf.py`, `tools/stl_to_svg_iso.py`, `tools/gen_assembly_exploded_view.py`, `tools/design_mechanical_drawings.py`, Graphviz `dot` for `.dot` files, kicad-cli for board plots). Do not hand-draw geometry; a new diagram may only be a DOT/Mermaid/SVG that restates verified relationships (and says so).
- **Assembly steps** must be numbered, each with: purpose, parts/tools (with the parts-list ID or BOM reference), the action, the check (acceptance value or visual criterion), and the figure reference. Steps that depend on an open decision (K1–K8, D-xx) carry a ⚠ marker and name the decision.
- **Language**: English for the manual (the repository's documentation language). Chat commentary to the user: Ukrainian.
- Keep the Markdown master buildable: `python3 tools/build_manual.py --check` must report 0 missing figures and 0 broken links before you finish.

## DELIVERABLES

| File | Content |
|---|---|
| `manual/AERIS10_MANUAL.md` | the complete manual (≥ the chapter set in `00_OUTLINE.md`; every chapter with text, figures, tables, cross-references) |
| `manual/chapters/*.md` | one file per chapter (the master `AERIS10_MANUAL.md` is concatenated from them by `tools/build_manual.py` — write the chapters, not the master) |
| `manual/build/AERIS10_MANUAL.html`, `.pdf` | rendered outputs with embedded figures (PNG preferred for PDF; SVG allowed in HTML) |
| `manual/FIGURE_LOG.md` | every figure used: number, caption, path, status, how it was produced (existing / rendered by which command) |
| `manual/MANUAL_VALIDATION.md` | `build_manual.py --check` output, link check, list of claims that could not be sourced (must be empty or explained), word/figure counts |

## PROCEDURE

1. Run `python3 tools/gen_manual_asset_index.py` and read `manual/ASSET_INDEX.md`; map each outline figure slot to an asset (or mark "to render").
2. Render the missing figures listed in `FIGURE_PLAN.md` §"to render" with the stated commands into `manual/figures/` (PNG, ≤ 2400 px wide; keep the SVG too).
3. Write each chapter file from its source list; copy tables from the source documents verbatim (do not retype numbers); add narrative only where the sources support it.
4. Write the assembly/integration chapter from `ASSEMBLY_STEPS_SOURCE.md`, one numbered step per row, with figures from DSN-MECH-04/06/07, the harness schedule and the connector matrix.
5. Build: `python3 tools/build_manual.py` (concatenates `chapters/` in outline order, numbers figures, embeds images, writes HTML and prints to PDF through headless Chrome).
6. Validate: `python3 tools/build_manual.py --check` and `python3 tools/check_doc_links.py`; fix until clean; write `MANUAL_VALIDATION.md`.
7. Report in the final message: chapter list with word counts, figure count by status, validation results, claims left unsourced, and the paths of the HTML/PDF.

## FINAL RESPONSE FORMAT

A. Manual structure (chapters, pages/words). B. Figures (count by status, rendered vs reused). C. Validation results (commands + PASS/FAIL). D. Unsourced or ambiguous items left in the text (with the exact phrase). E. Paths of all deliverables.
