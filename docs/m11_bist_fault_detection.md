# M11 — Signature-based BIST fault detection

This extension forces one bit of the **toy circuit's 8-bit response** to a constant stuck-at-0 or stuck-at-1 value *before* the MISR captures it. It runs the same 16-pattern LFSR sequence and compares the final MISR signature against a fault-free baseline.

The cocotb test checks each signature against an independent Python reference and records detection/aliasing across **16 modeled response faults** (8 bit positions × 2 polarities). It does not assume all faults are detectable: a fault may fail to sensitize, or its effects may alias in the MISR.

Run `make test-bist-faults`. This is not ATPG, CPU-level fault coverage, or physical silicon fault simulation.
