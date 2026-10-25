# Milestone 10 verification coverage and closure matrix

This report records **test-scenario coverage**, not a simulator-generated code/functional coverage percentage. Passing CI establishes that the listed tests ran successfully on that commit; it does not prove full RV32I ISA compliance.

| Objective | Status | Evidence |
| --- | --- | --- |
| RV32I R/I/U arithmetic semantics | Exercised | `test_rv32i_differential.py` — 1,701 boundary + 2,100 randomized comparisons |
| Unsupported integer encodings | Exercised | `test_rv32i_differential.py` — 64 negative checks |
| Integrated register and load/store semantics | Exercised | `test_cpu_arch_scoreboard.py` |
| Taken/untaken branch loop and JAL | Exercised | `test_cpu_control_scoreboard.py` |
| Rejected memory stores preserve protected word | Exercised | `test_data_memory_fault_invariants.py` — 7 injected invalid stores |
| CPU misaligned LW suppresses commit and halts | Exercised | `test_cpu_fault_assertions.py` |
| Illegal/fault write suppression, halt PC stability, reset | SVA properties added; confirm CI | `verification/rtl/cpu_fault_harness.sv` with `COMPILE_ARGS=--assert` |
| CPU-level misaligned store | Open | Add a stored program and memory side-effect check |
| CPU-level misaligned branch/jump target | Open | Add negative target program |
| End-to-end JALR | Open | Add a stored-program test |
| Randomized multi-instruction programs | Open | Expand architectural reference model |
| Formal proof / coverage percentage | Open | Requires appropriate formal or coverage tooling |

Machine-readable inventory: `verification/coverage/m10_matrix.json`. The inventory is manually curated and must be updated when tests change.

## Reproduce

```bash
make test-cpu-fault-assertions
make test
```

The fault harness uses **native concurrent SystemVerilog `assert property`** checks, with Verilator assertion evaluation enabled explicitly for that target. The existing cocotb checks provide independent cycle-level validation. SVA properties are evaluated in simulation, not formally proven.
