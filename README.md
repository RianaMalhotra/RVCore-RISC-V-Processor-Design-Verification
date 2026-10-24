# RISC-V SoC Design & Verification

[![RTL Verification](https://github.com/RianaMalhotra/riscv-soc-verification/actions/workflows/rtl-ci.yml/badge.svg)](https://github.com/RianaMalhotra/riscv-soc-verification/actions/workflows/rtl-ci.yml)

**Simulation-only digital hardware design and verification with SystemVerilog, Verilator, and Python/cocotb.**

> **Project status: Early development.** Standalone 32-bit ALU and RV32I register-file RTL and cocotb tests are implemented. They are not yet integrated into a processor. Check GitHub Actions for actual test results.

## Objectives
- Build synthesizable RTL for a small RV32I-based processor incrementally.
- Verify each module with directed and deterministic randomized Python tests.
- Run repeatable RTL linting and regression tests in GitHub Actions.
- Explore scan-chain and built-in self-test (BIST) concepts after core functionality.

## Current implementation

| Component | Status |
| --- | --- |
| 32-bit ALU (ADD/SUB/AND/OR/XOR, zero flag) | Implemented |
| 32 × 32-bit register file (dual read, single write, x0 hardwired zero) | Implemented |
| cocotb ALU and register-file reference-model tests | Implemented; check CI results |
| Verilator lint and GitHub Actions workflow | Configured; check CI results |
| RV32I decoder and integrated processor | Planned |
| Functional coverage and DFT experiments | Planned |

## Quick start

Requirements: Python 3.11+, Verilator, GNU Make and a C++ compiler.

```bash
git clone https://github.com/RianaMalhotra/riscv-soc-verification.git
cd riscv-soc-verification
python -m pip install -r requirements.txt
make lint
make test
```

Individual suites: `make test-alu` and `make test-register-file`. No physical hardware required.

## Repository layout

```text
rtl/core/                 # Standalone RTL building blocks
verification/cocotb/      # Python simulation tests
docs/                    # Architecture and verification plans
.github/workflows/       # Automated CI
Makefile                 # Lint and separate test targets
```

See [architecture](docs/architecture.md) and [verification plan](docs/verification_plan.md).

## Development roadmap
- [x] Initial ALU RTL and testbench
- [x] Register-file RTL and testbench
- [x] Configure automated lint and test workflow
- [ ] Confirm first green CI run
- [ ] Instruction decoder and program counter
- [ ] Integrated CPU and RV32I subset program execution
- [ ] Functional coverage and assertions
- [ ] Scan-chain and BIST exploration

## Author
Riana Malhotra — Computer Engineering, University of Toronto

## License
[MIT](LICENSE)
