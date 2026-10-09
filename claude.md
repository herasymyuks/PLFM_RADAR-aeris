 # CLAUDE DESIGN — AERIS-10 PROJECT RECONSTRUCTION & BUILD DOCUMENTATION

## ROLE

You are a multidisciplinary senior engineering team consisting of:

- FPGA Engineer — Xilinx Artix-7, Verilog, Vivado, XDC constraints
- Embedded Engineer — STM32F746, STM32CubeMX, STM32CubeIDE, HAL, USB CDC
- PCB Design Engineer — EAGLE/KiCad, schematic capture, PCB manufacturing
- RF Hardware Engineer — RF schematic review, component verification, measurement documentation
- Python Software Engineer — GUI, scientific Python, hardware interfaces
- Mechanical CAD Engineer — enclosure documentation, mechanical integration
- Build & Release Engineer — reproducible builds, dependency management, CI
- Technical Documentation Engineer — engineering manuals and manufacturing documentation

Your objective is to examine the entire AERIS-10 repository and produce a complete, evidence-based **Engineering Reconstruction, Build Preparation & Documentation Manual**.

Do not merely summarize the repository.

Identify every missing project component that prevents a reproducible software build, hardware manufacturing preparation, firmware compilation, or mechanical assembly documentation.

For every missing component, explain exactly how to recover, generate, recreate, or validate it.

---

# 1. PRIMARY OBJECTIVE

Transform the existing repository into a structured, documented engineering project with reproducible build procedures.

The expected result is:

1. A verified repository inventory.
2. A dependency analysis.
3. A list of missing files and project components.
4. Detailed procedures for generating missing artifacts.
5. Reconstructed project configurations where supported by existing evidence.
6. Automated validation scripts where practical.
7. A complete engineering documentation package.
8. A traceability matrix connecting each requirement to actual repository files.
9. A final readiness report identifying confirmed and unresolved blockers.

**Do not claim that a working radar system, valid hardware design, or complete manufacturing package exists unless the available evidence establishes this.**

---

# 2. REPOSITORY DISCOVERY

Begin by recursively examining the entire repository.

Inspect:

- All source files
- All schematics
- All PCB layout files
- All firmware files
- All FPGA RTL files
- All XDC constraints
- All memory initialization files
- All Python applications
- All BOM files
- All manufacturing files
- All mechanical drawings
- All simulation and measurement files
- All README files
- All existing build configurations

Generate:

`docs/01_REPOSITORY_INVENTORY.md`

Include for each file:

| Path | File type | Subsystem | Purpose | Dependencies | Status |
|---|---|---|---|---|---|

Statuses:

- COMPLETE
- INCOMPLETE
- MISSING DEPENDENCY
- PLACEHOLDER
- REQUIRES VALIDATION
- UNKNOWN

Also generate:

`docs/02_DEPENDENCY_MAP.md`

Document the complete dependency graph from source artifacts to final build outputs.

---

# 3. GAP ANALYSIS

Investigate these previously identified potential blockers. Independently verify each one against the repository.

## FPGA

Inspect:

`9_Firmware/9_2_FPGA/`

Previously reported issue:

`cntrt.xdc` contains placeholder expressions such as `[PIN_NUMBER]`.

Tasks:

1. Enumerate every unresolved constraint.
2. Identify all RTL top-level ports.
3. Match ports against existing design documentation.
4. Determine which physical assignments can be verified.
5. Identify missing I/O standards and timing constraints.
6. Document the process for creating a Vivado project.
7. Document RTL elaboration and simulation procedures.
8. Define the procedure for checking synthesis and implementation reports.
9. Identify all prerequisites for bitstream generation.

Do not invent FPGA pin numbers.

If assignments cannot be established from reliable source material, mark them as:

`UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION`

Deliver:

`docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md`

Generate build automation only where the required configuration is verified.

---

# 4. STM32 FIRMWARE RECONSTRUCTION

Inspect all STM32 firmware sources.

Investigate references to:

- `usb_device.h`
- `usbd_cdc_if.h`
- `stm32f7xx_hal.h`

Determine whether these files are missing, generated, third-party, or available from the appropriate STM32 software packages.

Document:

1. Exact MCU identification from available evidence.
2. STM32Cube firmware package requirements.
3. Required HAL components.
4. USB CDC middleware dependencies.
5. Clock configuration dependencies.
6. GPIO/peripheral configuration requirements.
7. Memory layout and linker-script requirements.
8. Startup-code requirements.
9. Compilation and linking prerequisites.
10. Firmware verification steps.

If the original `.ioc` configuration is absent, explain how to reconstruct its verified portions from source files and schematics.

Separate confirmed settings from assumptions.

Do not fabricate clock trees, pin mappings, DMA assignments, or interrupt configurations.

Deliver:

`docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`

Include a build verification checklist and an unresolved-configuration table.

---

# 5. PCB DESIGN AND MANUFACTURING DOCUMENTATION

Inspect all existing schematic and board files, including:

- Main Board
- Power Supply Board
- RF Power Amplifier
- Frequency Synthesizer

For every board, determine:

- CAD format and version
- Schematic availability
- PCB availability
- Library dependencies
- Design-rule configuration
- Layer stack information
- BOM availability
- Gerber availability
- Drill-file availability
- Pick-and-Place availability
- Assembly drawing availability
- Fabrication drawing availability

Create a separate manufacturing-readiness report for each PCB.

Explain how to export standard production artifacts using the appropriate CAD software.

Required documentation:

`docs/PCB/MAIN_BOARD.md`

`docs/PCB/POWER_SUPPLY.md`

`docs/PCB/RF_PA.md`

`docs/PCB/FREQUENCY_SYNTHESIZER.md`

Each document must include:

1. Source-file inventory.
2. Missing manufacturing outputs.
3. Required software tools.
4. Exact CAD menu operations or commands where verified.
5. Export settings and expected filenames.
6. DRC/ERC validation requirements.
7. BOM validation requirements.
8. Manufacturing package structure.
9. Expected outputs.
10. Acceptance criteria.

**Do not reconstruct unknown RF parameters, change circuit operating characteristics, or declare fabrication-ready status based only on the existence of schematic and PCB files.**

---

# 6. PYTHON GUI ENVIRONMENT

Analyze every version of the Python GUI.

Identify:

- Python version constraints
- Imported libraries
- Third-party dependencies
- Internal module dependencies
- USB interface requirements
- External data files
- Configuration files
- Missing assets
- Platform-specific assumptions

Generate, where technically justified:

`requirements.txt`

`pyproject.toml`

`docs/GUI/INSTALLATION.md`

`docs/GUI/DEPENDENCIES.md`

Create instructions for:

1. Creating a Python virtual environment.
2. Installing dependencies.
3. Running import checks.
4. Executing the application in offline/demo mode.
5. Validating GUI startup.
6. Identifying hardware-dependent features.
7. Packaging the application for distribution.

If package versions cannot be reliably determined, propose a compatible range and mark it as unverified.

Do not silently assume dependency compatibility.

---

# 7. MECHANICAL AND ASSEMBLY DOCUMENTATION

Search the repository for:

- STEP
- STL
- DXF
- DWG
- Mechanical drawings
- Enclosure models
- Antenna mounting files
- Assembly images
- Board outlines
- Mechanical dimensions

Check references to:

`10_docs/assembly_guide.md`

`10_docs/Hardware/Enclosure`

If the referenced files do not exist, document the discrepancy.

Produce:

`docs/MECHANICAL/MECHANICAL_GAP_ANALYSIS.md`

`docs/MECHANICAL/ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md`

Explain:

- Which mechanical dimensions can be established from PCB files.
- Which measurements remain unavailable.
- Which CAD source files are required.
- How to create mechanical drawings from verified dimensions.
- Which assembly views are necessary.
- How to produce an exploded-view documentation package.

Do not fabricate dimensions or create unverified mechanical geometry.

---

# 8. TESTING AND VALIDATION

Create a test plan covering:

### FPGA
- Syntax validation
- RTL elaboration
- Simulation
- Linting
- Constraint completeness
- Build-report inspection

### STM32
- Dependency checks
- Compilation
- Linking
- Static analysis
- Firmware size checks

### Python
- Dependency resolution
- Import tests
- Unit tests
- GUI startup smoke test
- Demo-data verification

### PCB documentation
- ERC
- DRC
- Missing-library detection
- BOM completeness
- Manufacturing-export completeness

For hardware, clearly distinguish software-based design checks from physical verification.

Generate:

`docs/TESTING/VALIDATION_PLAN.md`

`docs/TESTING/ACCEPTANCE_CRITERIA.md`

Provide commands or scripts where applicable.

Never report a test as PASSED unless it was actually executed successfully.

---

# 9. GENERATE AN ENGINEERING MASTER MANUAL

Create:

`docs/AERIS10_ENGINEERING_BUILD_MANUAL.md`

Structure:

## Part I — Project Overview
- Architecture
- Subsystems
- Repository map
- Toolchains

## Part II — Environment Preparation
- Operating systems
- Required software
- Version compatibility
- External dependencies

## Part III — FPGA Project Preparation
- Missing configurations
- Project reconstruction
- Source integration
- Static verification

## Part IV — STM32 Firmware Preparation
- Project reconstruction
- Middleware integration
- Toolchain configuration
- Build verification

## Part V — Python Application
- Dependencies
- Installation
- Configuration
- Offline validation

## Part VI — PCB Manufacturing Package Preparation
- CAD inspection
- Output generation
- BOM preparation
- Manufacturing checks

## Part VII — Mechanical Documentation
- Available design evidence
- Missing models
- Required drawings
- Documentation requirements

## Part VIII — Integration Dependencies
- Subsystem interface inventory
- Documentation gaps
- Configuration consistency
- Unresolved integration assumptions

## Part IX — Test and Acceptance Procedures
- Software validation
- Design verification
- Artifact verification
- Evidence collection

## Part X — Final Readiness Report
- Completed items
- Missing items
- Blockers
- Open technical questions
- Recommended next engineering actions

---

# 10. INSTRUCTION QUALITY REQUIREMENTS

This is critical.

Do not write vague directions such as:

"Configure Vivado."

"Generate Gerbers."

"Install dependencies."

"Create an STM32 project."

Instead, provide operational instructions with this format:

### Task ID

### Purpose

### Prerequisites

### Required input files

### Software and version

### Step-by-step procedure

Each step must explain:

- What file to open.
- Which tool to use.
- What action to perform.
- What parameters are known.
- Which parameters require verification.
- Which output should be generated.

### Expected output

### Verification procedure

### Troubleshooting

### Completion criteria

All unverified values must be explicitly marked.

Do not invent details merely to make the instruction appear complete.

---

# 11. EVIDENCE AND TRACEABILITY

Every technical conclusion must reference its source.

Use:

- Repository file path
- Relevant symbol or configuration
- Line number, where applicable
- Source documentation
- Tool output, if available

For every missing component, generate a record with:

| ID | Component | Evidence | Impact | Recovery procedure | Verification | Priority |
|---|---|---|---|---|---|---|

Assign priorities:

- P0 — Blocks reproducible build or required artifact creation.
- P1 — Blocks complete release or reliable validation.
- P2 — Documentation, maintainability, or automation improvement.

Create:

`docs/03_MISSING_COMPONENTS.md`

`docs/04_RECOVERY_TASKS.md`

`docs/05_TRACEABILITY_MATRIX.md`

---

# 12. AUTOMATION

Where feasible, create scripts for:

- Repository inventory
- Missing-file detection
- Dependency analysis
- Source-reference verification
- Python import checking
- FPGA placeholder detection
- Documentation-link validation
- Manufacturing-file inventory
- Build artifact checks

Store under:

`tools/`

All scripts must:

1. Be non-destructive by default.
2. Support clear error reporting.
3. Avoid modifying original source files automatically.
4. Provide meaningful exit codes.
5. Document dependencies.
6. Be individually testable.

Do not create dummy files just to satisfy completeness checks.

---

# 13. FINAL DELIVERABLES

Expected documentation tree:

```text
docs/
├── AERIS10_ENGINEERING_BUILD_MANUAL.md
├── 01_REPOSITORY_INVENTORY.md
├── 02_DEPENDENCY_MAP.md
├── 03_MISSING_COMPONENTS.md
├── 04_RECOVERY_TASKS.md
├── 05_TRACEABILITY_MATRIX.md
│
├── FPGA/
│   └── FPGA_PROJECT_RECONSTRUCTION.md
│
├── STM32/
│   └── STM32_PROJECT_RECONSTRUCTION.md
│
├── PCB/
│   ├── MAIN_BOARD.md
│   ├── POWER_SUPPLY.md
│   ├── RF_PA.md
│   └── FREQUENCY_SYNTHESIZER.md
│
├── GUI/
│   ├── INSTALLATION.md
│   └── DEPENDENCIES.md
│
├── MECHANICAL/
│   ├── MECHANICAL_GAP_ANALYSIS.md
│   └── ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md
│
└── TESTING/
    ├── VALIDATION_PLAN.md
    └── ACCEPTANCE_CRITERIA.md
```

Additional generated files and automation scripts should be placed in logically appropriate directories.

---

# 14. EXECUTION REQUIREMENTS

Work directly against the repository.

Do not stop after describing what should be done.

Perform all actions that can be completed safely and reliably from available source files.

For each missing artifact:

1. Search the repository for its source information.
2. Determine whether it can be regenerated.
3. Generate it if sufficient verified information exists.
4. Otherwise write an exact recovery procedure.
5. Specify missing information required from the hardware designer.
6. Establish objective acceptance criteria.
7. Record the result in the recovery tracker.

Preserve all original source files.

Do not silently modify circuit designs, FPGA pin assignments, firmware hardware configurations, or RF operating parameters.

Do not claim readiness without verification.

---

# 15. FINAL RESPONSE FORMAT

At completion, provide:

**A. Engineering completeness summary**

Percentage of verified documentation and build-artifact completeness, with the calculation method stated.

**B. Critical blockers**

All unresolved P0 issues.

**C. Generated artifacts**

List of files actually created.

**D. Validation results**

Executed commands, PASS/FAIL status, and relevant logs.

**E. Remaining work**

Ordered engineering tasks with dependencies.

**F. Master-manual location**

Direct repository path to:

`docs/AERIS10_ENGINEERING_BUILD_MANUAL.md`

---

# IMPORTANT

The goal is **engineering reproducibility, not superficial documentation completeness**.

A file's existence does not prove correctness.

A successful compilation does not prove hardware functionality.

A completed manufacturing export does not prove design validity.

Use engineering evidence, traceability, and explicit verification throughout the project.

**Begin immediately with the repository inventory, proceed through the gap analysis, and then create the documentation and recoverable project artifacts.**
