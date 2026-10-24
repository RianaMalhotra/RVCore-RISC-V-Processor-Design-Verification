# RISC-V SoC Design & Verification

[![RTL Verification](https://github.com/RianaMalhotra/riscv-soc-verification/actions/workflows/rtl-ci.yml/badge.svg)](https://github.com/RianaMalhotra/riscv-soc-verification/actions/workflows/rtl-ci.yml)

**Simulation-only digital hardware design and verification with SystemVerilog, Verilator, and Python/cocotb.**

> **Project status: Early development.** A standalone 32-bit ALU and its verification testbench are implemented. A RISC-V CPU, SoC peripherals, coverage framework, and DFT features are planned—not yet implemented.

## Objectives

- Build synthesizable RTL for a small RV32I-based processor, incrementally.
- Verify each module with directed and randomized Python testbenches.
- Run repeatable RTL linting and regression tests in GitHub Actions.
- Explore scan-chain and built-in self-test (BIST) concepts after core functionality.

## Current implementation

| Component | Status |
| --- | --- |
| 32-bit ALU (ADD/SUB/AND/OR/XOR, zero flag) | Implemented |
| cocotb ALU reference-model tests | Implemented; check CI for results |
| Verilator lint and GitHub Actions workflow | Configured; check CI for results |
| Register file and RV32I decoder | Planned |
| Processor datapath and memory interface | Planned |
| Functional coverage and DFT experiments | Planned |

## Quick start

Requirements: Python 3.11+, Verilator, GNU Make, and a C++ compiler.

```bash
git clone https://github.com/RianaMalhotra/riscv-soc-verification.git
cd riscv-soc-verification
python -m pip install -r requirements.txt
make lint
make test
```

No physical hardware is required.

## Repository layout

```text
rtl/core/                 # RTL building blocks
verification/cocotb/      # Python simulation tests
docs/                    # Architecture and verification plans
.github/workflows/       # Automated CI
Makefile                 # Local lint and test commands
```

See [architecture](docs/architecture.md) and [verification plan](docs/verification_plan.md).

## Development roadmap

- [x] Initial ALU RTL and testbench
- [x] Add automated lint and test workflow
- [ ] Verify first green CI run
- [ ] Register file and instruction decoder
- [ ] Program counter and integrated CPU
- [ ] RV32I subset program execution
- [ ] Functional coverage and assertions
- [ ] Scan-chain and BIST exploration

## Author

Riana Malhotra — Computer Engineering, University of Toronto

## License

[MIT](LICENSE)
