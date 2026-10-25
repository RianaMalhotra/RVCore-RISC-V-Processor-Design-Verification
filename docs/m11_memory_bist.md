# Milestone 11 — Memory BIST prototype

A standalone 8-word × 8-bit memory test controller runs a **March-style** sequence:
1. Ascending addresses: write all zeros.
2. Ascending: read zero, then write ones.
3. Descending: read ones, then write zeros.
4. Ascending: read zeros.

It reports `busy`, sticky `done`, `pass`, `comparisons` (24), and `errors`. A new `start` restarts the sequence and clears counters.

## Modeled faults
`fault_enable`, `fault_address`, `fault_bit`, and `fault_value` force one observed bit of the selected memory location to stuck-at-0 or stuck-at-1. The test checks **128 modeled faults** (8 words × 8 bits × 2 polarities), and verifies a clean baseline and restart. The fault override is on the **read observation path**; it does not physically corrupt the stored cell. The RTL writes the test memory normally. Consequently, this detects the defined stuck-at observation faults, **not** all memory defects. No retention, coupling, address decoder, transition-delay, timing, ECC, or physical defect coverage is claimed.

Run `make test-memory-bist`. The controller is independent of the CPU memory and has no production DFT/ATPG integration.
