# Manual style guide (binding)

- **Audience**: an engineering team that will manufacture, assemble, program and test the radar without access to the original authors.
- **Status vocabulary** (append to every caption and procedure title): `ORIGINAL PROJECT FILE` (as found in the repository), `SOURCE-DERIVED` (generated from the native design files), `PARTIAL`, `CONCEPTUAL`, `PROPOSED DESIGN` (new engineering content, decisions D-xx), `BETA` (builds/simulates/tests on a workstation, not on hardware), `BLOCKED — MISSING DATA`. `VERIFIED` is reserved for hardware/vendor-confirmed items and is currently unused.
- **Citations**: inline `(source: engineering/…/file.md §3)` or `(source: beta/stm32/Core/Src/main.cpp:1241)`; a table copied from a source states the source once in its caption.
- **Numbers**: SI units, mm for mechanics, dB/dBm/dBi for RF; keep the source's precision; mark assumptions as `ASSUMED` and estimates as `ESTIMATE` exactly as the sources do.
- **Figures**: `Figure <chapter>.<n> — <what it shows> [<STATUS>] (source: <path>; produced by <tool>)`; PNG for PDF builds, SVG retained; never crop away title blocks of drawings; one figure per claim, no decorative images; photographs from `8_Utils/` are `ORIGINAL PROJECT FILE` and carry no dimensions.
- **Procedures**: numbered steps `Step <chapter>.<n>`; fields: Purpose / Parts & tools / Action / Check / Figure / ⚠ Decision (if any). Safety notes (22 V drain supply, RF radiation, rotating pedestal) precede the first step that needs them.
- **Headings**: `#` chapter, `##` section, `###` subsection; chapter files start with a front-matter block: title, status summary, sources list.
- **Cross-references**: use the IDs already in use (K1–K8 conflicts, D-01…D-19 decisions, DSN-* drawings, R-* tasks, AC-* acceptance criteria, CBL-* cables, G-* geometry gaps, MDR-* recovery guides).
- **No marketing language, no speculation, no "should work"**; say what was executed and what was not.
- **Authorship**: every page header/footer, the title page, drawing title blocks and chapter front-matter carry `Antidrone Ukraine · antidrone.cc`; captions of original upstream files keep `ORIGINAL PROJECT FILE` and do not claim authorship.
