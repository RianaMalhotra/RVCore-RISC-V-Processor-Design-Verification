# Architecture

## Current implementation

The project currently implements a standalone combinational 32-bit ALU. This is **not yet a RISC-V processor**.

| Operation code | Function |
| --- | --- |
| 000 | ADD (modulo 2^32) |
| 001 | SUB (modulo 2^32) |
| 010 | AND |
| 011 | OR |
| 100 | XOR |
| 101–111 | Zero result |

Inputs are `a`, `b` (32-bit), and `op` (3-bit). Outputs are `result` (32-bit) and `zero` (true when result is zero). These operation codes are internal ALU selectors, not RISC-V instruction encodings.

## Planned

- RV32I register file, instruction decoder, program counter, and control
- CPU datapath, instruction/data memory interfaces
- Scan-chain and built-in self-test experiments

All planned blocks must be separately implemented and verified before claims of CPU functionality.
