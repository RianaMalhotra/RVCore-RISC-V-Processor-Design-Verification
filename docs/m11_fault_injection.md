# M11: Observable scan-output stuck-at fault model

The wrapper `rtl/dft/scan_fault_harness.sv` injects a **single stuck-at-0 or stuck-at-1** fault at a selected bit of the scan register's **observable parallel output**. It does not corrupt the internal flop state, represent all physical stuck-at sites, or perform ATPG.

The directed cocotb test exercises 8 bit positions × 2 stuck values = **16 modeled faults**. It captures the complementary value to sensitize each fault, checks detection against the fault-free reference, and checks a non-sensitizing pattern. This gives **16/16 detection for this limited model only**, not chip-level fault coverage.

Run `make test-scan-stuck-at`. Future work: internal state fault injection, shift-out diagnosis, BIST signature analysis, and integration into processor test architecture.
