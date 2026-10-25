"""Validate the eleven-cycle RTL load/store trace and memory replay."""
import json
from pathlib import Path

data = json.loads(Path("visualizer/public/load_store_trace.json").read_text())
assert data["schema_version"] == 1
assert data["program"] == "programs/load_store.hex"
cycles = data["cycles"]
assert len(cycles) == 11
regs = [0] * 32
mem = [0] * 256
for index, event in enumerate(cycles):
    assert event["cycle"] == index + 1
    assert event["pc"] == index * 4
    assert len(event["registers_after"]) == 32
    assert len(event["memory_after"]) == 256
    if event["write_enable"]:
        assert event["rd"] != 0
        regs[event["rd"]] = event["write_data"]
    assert event["registers_after"] == regs
    if event["memory_store"] and not event["illegal"]:
        word = int(event["instruction"], 16)
        width = {0: 1, 1: 2, 2: 4}[(word >> 12) & 7]
        address = event["memory_address"]
        for b in range(width):
            mem[address+b] = (event["memory_write_data"] >> (8*b)) & 255
    assert event["memory_after"] == mem
assert sum(c["memory_store"] and not c["illegal"] for c in cycles) == 3
assert sum(c["memory_load"] and not c["illegal"] for c in cycles) == 5
assert cycles[-1]["illegal"] and cycles[-1]["halted_after"]
assert mem[64:72] == [0x80, 0x00, 0x80, 0xFF, 0x80, 0xFF, 0xFF, 0xFF]
print("11-cycle RTL load/store trace: register/memory replay and halt verified")
