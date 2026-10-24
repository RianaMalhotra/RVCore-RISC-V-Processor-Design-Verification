# Verification Plan

## ALU

The cocotb testbench compares the RTL output against a Python reference model for all eight operation selectors across six directed and 200 reproducible random operand pairs. It also checks the zero flag on each case.

Run `make lint` and `make test` with Verilator, Python and cocotb installed.

## Planned

- Register-file read/write/reset behavior
- Decoder instruction classification and illegal cases
- CPU integration and program execution
- Functional coverage, assertions and fault injection

Coverage metrics and CPU compliance are **not yet claimed**. Verify the CI run status before reporting a passing regression.
