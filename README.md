<p align="center"><img src="docs/images/readme-overview-v3.svg" alt="Updated RISC-V SoC architecture, milestone status, timing diagram, operation tables and verification flow" width="100%"></p>

> **Visual overview:** Updated through the completed and CI-verified Milestone 6 branches/jumps integration. The timing diagrams, operation tables, and verification flow remain included. [Original reference image](docs/images/reference.jpeg) is preserved. Detailed design explanations, tests, and setup instructions follow below.

---

# RISC-V SoC Design & Verification

[![RTL Verification](https://github.com/RianaMalhotra/riscv-soc-verification/actions/workflows/rtl-ci.yml/badge.svg)](https://github.com/RianaMalhotra/riscv-soc-verification/actions/workflows/rtl-ci.yml)
![SystemVerilog](https://img.shields.io/badge/RTL-SystemVerilog-445a83)
![Verification](https://img.shields.io/badge/Verification-cocotb%20%2B%20Verilator-326d64)
![License](https://img.shields.io/badge/License-MIT-blue)

**Building and verifying the hardware building blocks of a 32-bit RISC-V processor—entirely in simulation.**

This project is a hands-on exploration of **digital RTL design, processor architecture, and hardware verification**. I implement synthesizable hardware modules in SystemVerilog, test their behavior against Python reference models with cocotb, and run automated regressions through GitHub Actions. The longer-term goal is a small RV32I-based CPU followed by design-for-test (DFT) experiments.

> **Current scope:** The **32-bit ALU**, **32 × 32-bit register file**, and **limited RV32I arithmetic decoder** are implemented as **independently tested modules**. They are wired into arithmetic and control-flow CPU prototypes; a data-memory integration is now in review. This is not a complete SoC.

## At a glance

| | |
| --- | --- |
| **Focus** | RTL design, digital verification, RISC-V fundamentals, future DFT/DFX exploration |
| **Implemented hardware** | 32-bit ALU; 32-register file; RV32I arithmetic-subset decoder |
| **Verification** | Directed + seeded randomized cocotb tests with Python reference models |
| **Automation** | Verilator lint and simulation, GNU Make, GitHub Actions CI |
| **Hardware required** | None—runs entirely in software |
| **Current milestone** | Milestones 1–7 merged and CI verified |

## Architecture

### 1. Implemented modules and their interfaces

These independently tested building blocks are now connected in the CPU integration modules. The illustration is a historical module-level view.

![Implemented ALU and register file blocks](docs/images/implemented-blocks.svg)

**How the pieces will eventually work together:** An instruction will select two source registers. Their values will feed the ALU, which computes a result. Control logic will decide whether that result is written back to a destination register. **Instruction decoding, control, and arithmetic interconnections are implemented in RTL.**

### 2. Planned processor architecture (future work)

![Conceptual future RV32I CPU datapath](docs/images/planned-cpu.svg)

The planned diagram is an architectural roadmap. The current CPU already executes arithmetic, branches and jumps, with load/store integration under review.

## How the implemented hardware works

### Arithmetic Logic Unit (ALU)

[`rtl/core/alu.sv`](rtl/core/alu.sv) is a **combinational** 32-bit datapath block: changing its inputs changes its outputs without waiting for a clock. It takes two 32-bit operands and a three-bit operation selector.

| `op` | Operation | Behavior |
| --- | --- | --- |
| `000` | ADD | `a + b`, wrapped to 32 bits |
| `001` | SUB | `a - b`, wrapped to 32 bits |
| `010` | AND | Bitwise AND |
| `011` | OR | Bitwise OR |
| `100` | XOR | Bitwise XOR |
| `101–111` | Default | Result is zero |

The `zero` output is asserted whenever `result == 0`. The three-bit `op` values are **internal ALU control codes**, not RISC-V instruction encodings.

**Example:** With `a = 7`, `b = 5`, and `op = 000`, the ALU produces `result = 12` and `zero = 0`.

### Register file

[`rtl/core/register_file.sv`](rtl/core/register_file.sv) stores the values that a future processor would use as its architectural integer registers.

- **32 registers, 32 bits each:** `x0` through `x31`.
- **Two asynchronous read ports:** `rs1` and `rs2` select registers; `rd1` and `rd2` expose their values without a clock edge.
- **One synchronous write port:** If `we = 1`, `wd` is stored at `rd` on the **rising edge** of `clk`.
- **Hardwired zero:** Reads from `x0` always return zero; writes to `x0` are ignored, as required by RISC-V.
- **Synchronous active-high reset:** `rst` clears the storage on a rising edge. Clearing all registers is a **project-specific simulation/design choice**, not an RV32I architectural requirement.

**Example:** Write `0x12345678` to `x1` with `we = 1`; after the next rising edge, selecting `rs1 = 1` returns `0x12345678`. Selecting `rs2 = 0` still returns zero.

### Instruction decoder (Milestone 3)

[`rtl/core/instruction_decoder.sv`](rtl/core/instruction_decoder.sv) decodes a **limited RV32I arithmetic subset**: R-type `ADD`, `SUB`, `AND`, `OR`, `XOR` and I-type `ADDI`, `ANDI`, `ORI`, `XORI`. It extracts register indices, sign-extends the I-immediate, and emits ALU operation, immediate-select, register-write and illegal-instruction signals. Unsupported encodings assert `illegal` and disable writes. **Loads, stores, branches, jumps, shifts and a complete CPU remain unimplemented.**

## Verification: how correctness is checked

Rather than relying on visual waveform inspection alone, each module is tested by a **Python reference model** that independently computes the expected output and compares it to the simulated RTL.

![Automated cocotb and Verilator verification flow](docs/images/verification-flow.svg)

| Module | Verification performed |
| --- | --- |
| **ALU** | All 8 selector values, boundary operands, 200 deterministic random operand pairs, output and zero-flag comparisons |
| **Register file** | Reset, immutable `x0`, `x1`/`x31` boundaries, two independent reads, write enable, edge timing, overwrite, reset priority |
| **Decoder** | Directed and seeded randomized valid R/I instruction encodings, sign extension, register indices, control outputs, and rejection of unsupported encodings |
| **Register file randomized** | 500 seeded transactions against a software register model, then a 32 × 32 exhaustive read-address sweep |
| **CI** | RTL lint followed by both cocotb suites on pushes and pull requests |

A passing GitHub Actions run demonstrates that **these particular checks passed for that commit**; it does **not** establish full ISA compliance, measured functional coverage, or silicon readiness. See [the verification plan](docs/verification_plan.md) for details.

## Technology stack

| Tool | Role in this project |
| --- | --- |
| **SystemVerilog** | Describes the combinational and sequential hardware in synthesizable RTL |
| **Verilator** | Lints RTL and compiles it into a fast software simulation |
| **Python + cocotb** | Drives hardware signals, creates test scenarios, and checks outputs |
| **GNU Make** | Provides repeatable local commands for linting and simulation |
| **GitHub Actions** | Runs automated checks for pushes and pull requests |
| **Git / GitHub** | Version control, issues, feature branches, pull requests, and review history |

This is **hardware design expressed as code**, not a Python emulation of a CPU. Python is the *verification environment*; SystemVerilog defines the hardware being tested.

## Run locally

**Prerequisites:** Verilator, GNU Make, a C++ compiler, and Python with `venv` support. CI uses Ubuntu's system Python and [the pinned cocotb dependency](requirements.txt) for simulator compatibility. A Linux environment (including WSL on Windows) is recommended.

```bash
git clone https://github.com/RianaMalhotra/riscv-soc-verification.git
cd riscv-soc-verification

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

make lint                # Lint both SystemVerilog modules
make test                # Run ALU + register-file tests
make test-alu            # Run only ALU tests
make test-register-file  # Run only register-file tests
make test-decoder        # Run only decoder tests
```

No FPGA, development board, or other physical hardware is needed.

## Repository structure

```text
riscv-soc-verification/
├── .github/workflows/rtl-ci.yml    # Automated lint and regression
├── rtl/core/
│   ├── alu.sv                      # 32-bit combinational ALU
│   ├── register_file.sv            # 32 × 32-bit register file
│   └── instruction_decoder.sv     # RV32I arithmetic subset decoder
├── verification/cocotb/
│   ├── test_alu.py                 # ALU directed/random tests
│   ├── test_register_file.py       # Register-file tests
│   └── test_instruction_decoder.py # Decoder tests
├── docs/
│   ├── architecture.md             # Detailed design notes
│   └── verification_plan.md        # Test coverage by behavior
├── Makefile                         # Build/test entry points
├── requirements.txt                 # Python dependency
└── LICENSE
```

## Development roadmap

- [x] **Milestone 1 — ALU:** Implement 32-bit arithmetic/logic and Python verification.
- [x] **Milestone 2 — Register file:** Implement two-read/one-write 32-register storage and directed/randomized tests.
- [x] **Verification infrastructure:** Configure Verilator lint, cocotb regression, and passing CI for the implemented modules.
- [x] **Milestone 3 — RV32I decoder:** Implement and test a limited arithmetic instruction subset; additional instruction classes remain planned.
- [x] **Milestone 4 — CPU datapath:** Add program counter, connect blocks, and execute a small RV32I subset in simulation.
- [x] **Milestone 5 — Instruction memory and automatic fetch:** Load a hex program and execute arithmetic instructions from PC-addressed memory.
- [ ] **Next — Verification depth:** Add assertions, functional coverage metrics, and integration-level regression.
- [x] **Milestone 6 — Branches and jumps:** BEQ, BNE, BLT, BGE, BLTU, BGEU, JAL, JALR with loop execution.
- [ ] **Future — DFT/DFX exploration:** Prototype scan-chain and built-in self-test (BIST) mechanisms with fault-injection tests.

Follow progress through [GitHub Issues](https://github.com/RianaMalhotra/riscv-soc-verification/issues) and [Actions](https://github.com/RianaMalhotra/riscv-soc-verification/actions).

## Engineering decisions and limitations

- **Modular development:** Verify individual blocks before integrating a processor, so failures are easier to isolate.
- **Deterministic random tests:** Fixed seeds make failures reproducible.
- **Architectural vs implementation behavior:** `x0` semantics follow RV32I; clearing the register file on reset is a deliberate implementation choice.
- **Scope honesty:** No processor integration, FPGA deployment, measured functional coverage, or scan/BIST implementation is claimed at this stage.

## Author

**Riana Malhotra** · Computer Engineering, University of Toronto

## License

Distributed under the [MIT License](LICENSE).

## Milestone 4 — Single-cycle arithmetic datapath (completed)

The `cpu_datapath` top-level connects the existing **RV32I arithmetic-subset decoder → 32 × 32-bit register file → ALU → register writeback**. It adds a 32-bit program counter starting at zero and advancing by four bytes for each supported instruction. Unsupported instructions assert `illegal` and latch `halted`, freezing the PC and preventing subsequent writes until reset.

**This is a CPU integration prototype, not a complete RV32I processor.** The standalone `cpu_datapath` accepts externally supplied instructions; Milestone 5 adds instruction memory through `cpu_system`. Branches, jumps, loads/stores, and data memory are not yet present. The original uploaded reference JPEG remains available in `docs/images/reference.jpeg`. The updated SVG overview above reflects the completed datapath milestone while retaining timing and verification diagrams.

```text
External instruction[31:0]
        │
        ▼
   RV32I decoder ────── control ───────────────┐
        │                                      │
        ▼                                      ▼
  Register file ── rs1_value ───────────────► ALU
        │                                      │
        └─ rs2_value ── immediate mux ────────►│
                                               │
                    register writeback ◄───────┘
        PC: reset to 0, +4 per valid instruction; halt on illegal
```

Run `make test-cpu` for the end-to-end arithmetic program, register writeback, x0, illegal-instruction halt and reset checks. `make test` now includes the CPU suite. **CI results must pass before merging this milestone.**

## Milestone 5 — Instruction memory and automatic fetch (CI verified)

The new `cpu_system` top level connects a 64-word, read-only `instruction_memory` to the Milestone 4 arithmetic datapath. The PC is a **byte address**; the instruction memory uses `PC >> 2` to fetch 32-bit aligned words from `programs/arithmetic.hex`. An invalid or unaligned fetch returns an illegal zero word and halts the core.

The example program executes eight arithmetic instructions, writes results into registers, and stops on a zero-word sentinel. The cocotb system test verifies each fetched instruction's ALU result, sequential PC updates, halt behavior, and reset replay. Run `make test-system` or `make test` (all suites). The CI workflow already invokes `make test` and `make lint`, so the new suite is automatically included.

**Limits:** This is still an arithmetic-subset prototype, not a full RV32I processor. There is no branch/jump control flow, load/store, data memory, external bus, or interrupt support. The memory image is loaded for simulation with `$readmemh`.

## Milestone 6 — Conditional branches and jumps (completed, CI verified)

The new `cpu_system_control` top-level integrates a `cpu_control_flow` decoder/comparator with the instruction memory, arithmetic decoder, register file, and ALU. Supported control flow: **BEQ, BNE, BLT, BGE, BLTU, BGEU, JAL, JALR**. Branch offsets are signed B-type immediates, JAL uses a signed J-type offset, and JALR computes `(rs1 + signed immediate) & ~1`. Taken branches/jumps update the PC; untaken branches use `PC + 4`. JAL/JALR write `PC + 4` to `rd` (except `x0`). Illegal encodings and misaligned taken targets halt execution; misaligned targets do not commit link writes.

The stored `programs/control_flow.hex` executes a decrementing loop and skips an instruction with JAL. The cocotb suites `test_cpu_control_flow.py` and `test_cpu_system_control.py` test branch signedness, offsets, legal/illegal encodings, PC trace, and reset. Run `make test-control-flow`, `make test-control-system`, or `make test`.

**Scope:** This is still a small arithmetic-and-control-flow CPU prototype, not a complete RV32I core. Loads/stores, data memory, system instructions, exceptions, and interrupts are not implemented. The existing timing diagram remains a register-file timing illustration.

## Milestone 7 — Data memory and RV32I load/store (completed, CI verified)

Added `rtl/core/data_memory.sv`: 256-byte default little-endian data memory, supporting `LB`, `LBU`, `LH`, `LHU`, `LW`, `SB`, `SH`, and `SW`. Byte and halfword reads sign-extend or zero-extend as appropriate. Misaligned, out-of-range, or invalid accesses raise a fault and do not commit stores.

The new `rtl/core/cpu_system_memory.sv` integrates memory into the existing arithmetic/branch/jump CPU, computes effective addresses as `rs1 + signed 12-bit immediate`, and routes load data to register writeback. The existing CPU modules are retained for regression compatibility. The program `programs/load_store.hex` exercises stores and loads of all three sizes; cocotb unit and integration tests run with `make test-data-memory` and `make test-memory-system` (included in `make test`).

**Limitations:** This is a simulation-only CPU prototype. There is no bus, cache, MMU, exception handler, or full RV32I support yet. Invalid memory accesses halt the CPU instead of raising architecturally compliant exceptions.
