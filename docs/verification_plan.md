# Verification Plan

## ALU
The cocotb testbench compares RTL against a Python reference model for all eight operation selectors across six directed and 200 reproducible random operand pairs. It checks the zero flag.

## Register file
Directed cocotb tests verify reset clearing, x0 immutability, x1/x31 boundary registers, independent dual read ports, write-enable gating, synchronous write timing, overwrite behavior and reset priority over writes.

A seeded randomized test performs 500 write/read transactions against a Python register model, followed by an exhaustive 32 × 32 dual-read address sweep. The reference model preserves x0 as zero.

## Decoder
Directed and seeded randomized tests check nine supported R/I arithmetic instructions, immediate sign extension, source/destination indices, ALU selector and write control. Invalid opcode/funct combinations are rejected with `illegal=1` and `reg_write=0`. This is subset validation, not full RV32I compliance.

## Commands
- `make lint`: lint all three RTL modules using Verilator.
- `make test-alu`: verify the ALU.
- `make test-register-file`: verify the register file.
- `make test-decoder`: verify the arithmetic-subset decoder.
- `make test`: run all three test suites in separate simulator build directories.

GitHub Actions runs lint and all three suites on pushes and pull requests. Passing CI must be confirmed from the actual workflow run; no functional coverage or CPU compliance is claimed yet.
