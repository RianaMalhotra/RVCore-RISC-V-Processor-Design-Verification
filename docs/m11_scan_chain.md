# Milestone 11 — DFT scan-chain fundamentals

This educational scan-register bank is a **standalone DFT demonstration**, not an automatically inserted scan chain in the RISC-V CPU. It does not establish silicon test coverage or ATPG effectiveness.

- `scan_enable=0`: capture `parallel_in` on the rising clock edge.
- `scan_enable=1`: shift toward the MSB; `scan_in` enters bit 0.
- `scan_out`: current MSB, sampled **before** a shift edge.
- `rst=1`: synchronous clear with priority over capture/shift.
- `WIDTH`: parameterized register width (minimum 2); default regression uses 8.

Run `make test-scan-chain` or `make test`. The cocotb test checks reset priority, capture, shift ordering, serial observation, deterministic random patterns, and scan-mode precedence.

## Next work
1. Add a stuck-at-0/stuck-at-1 fault-injection wrapper and detection tests.
2. Add a simple pattern generator / MISR signature experiment.
3. Investigate integration with a CPU register-bank scan model, without implying that production CPU flops are already scan-inserted.
