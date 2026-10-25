# Milestone 11 — LFSR/MISR Built-In Self-Test demonstration

`rtl/dft/bist_engine.sv` implements an 8-bit pseudo-random test-pattern generator (LFSR), an 8-bit response compactor (MISR), and a finite test sequence. The **toy circuit under test** is `pattern XOR 8'hA5`, not the RISC-V CPU.

- **LFSR**: nonzero seed `0x01`, feedback taps 7, 5, 4, 3, left shift.
- **MISR**: left shift, conditional `0x1D` polynomial XOR, then XOR in the 8-bit response.
- **Controller**: `start` restarts; `busy` during execution; `done` remains asserted on completion until restart/reset; `patterns_tested` counts captured responses.
- **Test**: independent Python model checks all 16 cycles, signature, pattern uniqueness within the tested window, completion, hold, restart and reset.

Run `make test-bist`.

This experiment verifies algorithmic behavior of a small BIST architecture. It **does not** claim ATPG quality, fault coverage, physical implementation, or CPU scan/BIST integration. A MISR signature can alias different responses, so matching signatures alone do not prove absence of faults.
