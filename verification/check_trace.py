"""Validate actual RTL trace export and architectural replay consistency."""
import json
from pathlib import Path

data = json.loads(Path("visualizer/public/trace.json").read_text())
assert data["schema_version"] == 1
assert "RTL simulation" in data["source"]
cycles = data["cycles"]
assert len(cycles) == 8, "Current integer program: seven instructions plus terminating illegal instruction"
regs = [0] * 32
for i, event in enumerate(cycles):
    assert event["cycle"] == i + 1
    assert event["pc"] == i * 4
    assert event["instruction"].startswith("0x") and len(event["instruction"]) == 10
    assert len(event["registers_after"]) == 32
    assert event["registers_after"][0] == 0
    assert isinstance(event["memory_fault"], bool)
    if event["write_enable"]:
        rd = event["rd"]
        assert 1 <= rd <= 31
        regs[rd] = event["write_data"]
    assert event["registers_after"] == regs, f"writeback replay mismatch at cycle {i + 1}"
assert cycles[-1]["illegal"] and cycles[-1]["halted_after"]
assert regs[7] == 0x1018
print("Trace schema, sequential PC, architectural register replay and halt verified")
