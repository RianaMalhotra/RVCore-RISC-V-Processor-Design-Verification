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
| Illegal/fault write suppression, halt PC stability, reset | Exercised in passing CI | `verification/rtl/cpu_fault_harness.sv` with `EXTRA_ARGS=--assert` |
| CPU-level misaligned store | Test added; awaiting CI | `test_cpu_store_fault.py` and `cpu_store_fault_harness.sv` |
| CPU-level misaligned taken branch target | Test added; awaiting CI | `test_cpu_branch_fault.py` and `cpu_branch_fault_harness.sv` |
| End-to-end JALR | Test added; awaiting CI | `test_cpu_jalr_end_to_end.py`: target bit clearing, signed offsets, link register, skipped instructions |
| Seeded randomized mixed ADDI/LW/SW instruction stream | Test added; awaiting CI | `test_cpu_random_stream.py` — 46 instructions plus illegal terminator; independent register/memory oracle |
| Formal proof / coverage percentage | Open | Requires appropriate formal or coverage tooling |

Machine-readable inventory: `verification/coverage/m10_matrix.json`. The inventory is manually curated and must be updated when tests change.

## Reproduce

```bash
make test-cpu-fault-assertions
make test-cpu-branch-fault
make test-cpu-store-fault
make test-cpu-jalr
make test-cpu-random-stream
make test
```

The fault harness uses **native concurrent SystemVerilog `assert property`** checks, with Verilator assertion evaluation enabled explicitly for that target. The existing cocotb checks provide independent cycle-level validation. SVA properties are evaluated in simulation, not formally proven.
