# Architecture

## Implemented standalone blocks

### 32-bit ALU
The combinational ALU implements ADD, SUB, AND, OR and XOR with a zero flag. Its three-bit selectors are internal, not RV32I instruction encodings.

### RV32I register file
The register file contains 32 32-bit registers (x0–x31), two asynchronous read ports and one rising-edge synchronous write port. Writes are gated by `we`; writes to x0 are ignored, and x0 always reads zero. A synchronous active-high reset clears all storage for deterministic simulation. Reads of a register being written return the old value until the rising edge, then the new value after the edge.

This reset behavior is a project design choice, not a requirement of the RV32I ISA. The register file is not yet connected to the ALU or a CPU.

### RV32I arithmetic instruction decoder
The combinational `instruction_decoder` handles R-type ADD, SUB, AND, OR, XOR and I-type ADDI, ANDI, ORI, XORI. It extracts rs1, rs2, rd, sign-extends bits [31:20], and emits `alu_op`, `use_imm`, `reg_write`, and `illegal`. Unsupported instructions are flagged illegal and do not enable register writes. `rs2` on I-type is a raw instruction bit-field, not an architectural source operand. No datapath integration is implemented yet.

## Planned
- Complete RV32I instruction coverage, program counter and remaining control
- Integrated CPU datapath and instruction/data memory interfaces
- Functional coverage, assertions, scan-chain and built-in self-test experiments

These are independent building blocks, **not yet a functioning processor**.
