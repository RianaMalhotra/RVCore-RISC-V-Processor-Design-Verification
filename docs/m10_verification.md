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

## Branch and jump CPU architectural scoreboard (third increment)

`make test-cpu-control-scoreboard` runs the existing stored branch-loop/JAL program against a Python reference model that independently decodes B/J/I immediates, computes taken/not-taken branch targets, tracks registers and link writeback, and checks instruction fetch, PC, illegal/halt, and writeback at each clock step. The test requires two taken BNEs, one not-taken BNE, one JAL, and the illegal sentinel; it checks that the skipped instruction is not executed. This is deterministic scenario coverage, **not** measured functional coverage closure. JALR is modeled but not exercised by this stored program; randomized programs, fault injection, and assertions remain future work.

## Data-memory fault injection and safety invariants (fourth increment)

`make test-data-memory-fault-invariants` initializes a known word, attempts seven rejected writes (misaligned halfword/word, out-of-range addresses, and invalid store encodings), and reads the word back after every rejected clock edge to assert **no unintended modification**. It also checks that an idle interface does not raise a fault even with invalid address/function inputs. The assertions are **cocotb temporal checks** against the RTL, not embedded SystemVerilog Assertions (SVA); SVA and full-memory atomicity proof remain future work. The test observes one protected word rather than every possible byte, and does not yet inject CPU-level misaligned branch targets.

## Integrated CPU fault injection and temporal checks (fifth increment)

`make test-cpu-fault-assertions` compiles a verification-only wrapper around the existing `cpu_system_memory` RTL, loading `programs/cpu_faults.hex`. The program sets an aligned base address, stores a word, then attempts a **misaligned LW**. Cocotb checks the fault and illegal signals, suppresses register writeback on the faulting instruction, confirms PC does not advance, checks halt remains sticky for four more clocks, and verifies reset recovery. The wrapper exposes existing internal commit/fault signals without changing the synthesizable CPU implementation.

These are executable cocotb temporal assertions, **not IEEE SVA properties**. They cover one CPU-level fault scenario, not all misaligned branches/stores, invalid instructions, or complete memory noninterference. Additional fault matrices, synthesizable SVA-compatible property checks, and coverage closure remain future work.
