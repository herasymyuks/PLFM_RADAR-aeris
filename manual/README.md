# manual/ — AERIS-10 complete manual (build kit)

This directory is the input kit for a Claude Design run that assembles the complete illustrated engineering & assembly manual. The instructions are in the repository root: **`MANUAL_BUILD_SPEC.md`** (role, hard rules, deliverables, procedure, response format).

| File | Purpose |
|---|---|
| `00_OUTLINE.md` | binding chapter list with sources and figure slots (concatenation order) |
| `STYLE_GUIDE.md` | writing/figure/caption/status rules |
| `FIGURE_PLAN.md` | figure per chapter: existing asset path or render command |
| `ASSET_INDEX.md` | generated index of 225 candidate figures with register status (`python3 tools/gen_manual_asset_index.py`) |
| `ASSEMBLY_STEPS_SOURCE.md` | consolidated assembly / harness / pedestal / bring-up steps with checks — source of chapter 15/16 |
| `chapters/*.md` | 22 chapter files (stubs until written) |
| `tools/build_manual.py` | `--check` validates chapters/figures/links; without flags builds `AERIS10_MANUAL.md`, `build/AERIS10_MANUAL.html` (images embedded) and `build/AERIS10_MANUAL.pdf` (headless Chrome) |

Workflow: write chapters → render missing figures into `manual/figures/` → `python3 tools/build_manual.py --check` (0 problems) → `python3 tools/build_manual.py` → fill `FIGURE_LOG.md` and `MANUAL_VALIDATION.md`.
