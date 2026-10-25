# Milestone 10 — Differential verification and coverage

This first Milestone 10 increment verifies the combinational RV32I integer execution unit against an independent Python instruction-semantic reference model.

## Reproduce

From the repository root, activate the project virtual environment, then run:

```bash
make test-rv32i-differential
```

The test is also part of `make test` and the GitHub Actions regression. The fixed seed is `0x20261025`; a failure prints the seed, iteration, instruction word, operand values, and expected/actual result.

## Verification strategy

- **Directed boundary matrix:** all 21 supported R/I/U integer operations against 9 × 9 operand pairs (1,701 comparisons).
- **Seeded differential fuzzing:** 2,100 additional instruction/operand/PC combinations, cycling across every supported operation.
- **Negative tests:** 8 illegal/unsupported encodings with 8 randomized input combinations each (64 validity checks).
- **Stimulus coverage:** an operation histogram is logged, with a minimum of 100 randomized-plus-directed samples per supported operation. This is **operation sampling coverage**, not a functional-coverage closure claim.
- **Reference independence:** expected values come from Python integer semantics, with explicit 32-bit masking, signed comparisons, sign-extended immediates, and arithmetic/logical shifts.

The test checks **combinational integer execution only**. It does not establish instruction-stream correctness, branch/load/store coverage, formal properties, or full ISA compliance. FENCE, ECALL, EBREAK, exceptions, and privileged ISA behavior remain outside the implemented scope.

## Next verification increments

Add a CPU-level instruction-stream scoreboard with architectural register and memory state; cover branches, jumps, load/store alignment and faults; add assertion-based control invariants; then produce machine-readable functional-coverage summaries and a documented closure matrix.

## CPU-level architectural scoreboard (second increment)

The `test-cpu-arch-scoreboard` target runs the stored `programs/load_store.hex` program against an independent instruction decoder and Python model of the 32 architectural registers, 256-byte little-endian memory, PC progression, and halt behavior. It checks every fetched instruction, the pre- and post-clock PC, illegal/halt signals, write enables, and expected register writeback values. Loads after stores indirectly verify modeled memory contents. It deliberately does **not** rely on Verilator-private register or memory arrays, and does **not** claim to directly inspect every register/memory location. This first CPU-level scoreboard covers the existing fixed load/store program; randomized instruction streams, branch/jump sequences, misalignment fault scenarios, and architectural assertions remain planned.

```bash
make test-cpu-arch-scoreboard
```
