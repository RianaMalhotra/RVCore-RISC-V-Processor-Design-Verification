# Visualizer trace verification and remaining acceptance scope

Run `make trace`, then `python3 verification/check_trace.py`, then `cd visualizer && npm install && npm run dev`.

The React UI replays an observed Verilator/cocotb trace, not live FPGA execution or a separate emulator. The CI validator checks the 8-cycle **integer example** (seven executed instructions plus illegal halt), sequential PC, x0 invariance, writeback-based register reconstruction, and halt. CI also builds the React app.

**Not yet satisfied:** Issue #14 additionally requires an 11-instruction load/store trace, memory-view replay, program selection, and a screenshot/GIF. The current 8-cycle integer example does not demonstrate these. Do not mark Issue #14 complete on the strength of this validator alone.

To capture a screenshot after launching the visualizer, open the browser at the local Vite URL and capture the UI; only add a screenshot to the README after it has been captured from a real run.
