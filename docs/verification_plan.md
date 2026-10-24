# Verification Plan

## ALU
The cocotb testbench compares RTL against a Python reference model for all eight operation selectors across six directed and 200 reproducible random operand pairs. It checks the zero flag.

## Register file
Directed cocotb tests verify reset clearing, x0 immutability, x1/x31 boundary registers, independent dual read ports, write-enable gating, synchronous write timing, overwrite behavior and reset priority over writes.

A seeded randomized test performs 500 write/read transactions against a Python register model, followed by an exhaustive 32 × 32 dual-read address sweep. The reference model preserves x0 as zero.

## Commands
- `make lint`: lint both RTL modules using Verilator.
- `make test-alu`: verify the ALU.
- `make test-register-file`: verify the register file.
- `make test`: run both test suites in separate simulator build directories.

GitHub Actions runs lint and both suites on pushes and pull requests. Passing CI must be confirmed from the actual workflow run; no functional coverage or CPU compliance is claimed yet.
