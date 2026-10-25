"""Independent cycle-by-cycle LFSR/MISR oracle and restart/done checks."""
import cocotb
from cocotb.triggers import Timer

STEPS = 16

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

def next_pattern(p):
    return ((p << 1) & 255) | (((p >> 7) ^ (p >> 5) ^ (p >> 4) ^ (p >> 3)) & 1)

def next_signature(sig, response):
    return (((sig << 1) & 255) ^ (0x1d if sig & 0x80 else 0) ^ response)

async def run_bist(dut):
    dut.start.value = 1
    await tick(dut)
    dut.start.value = 0
    assert int(dut.busy.value) == 1
    assert int(dut.done.value) == 0
    p, sig = 1, 0
    seen = set()
    for i in range(STEPS):
        assert int(dut.pattern.value) == p
        assert int(dut.signature.value) == sig
        assert int(dut.patterns_tested.value) == i
        assert p not in seen, "unexpected short LFSR repetition"
        seen.add(p)
        sig = next_signature(sig, p ^ 0xa5)
        p = next_pattern(p)
        await tick(dut)
        assert int(dut.pattern.value) == p, f"pattern mismatch cycle {i}"
        assert int(dut.signature.value) == sig, f"MISR mismatch cycle {i}"
        assert int(dut.patterns_tested.value) == i + 1
        assert int(dut.busy.value) == int(i != STEPS - 1)
        assert int(dut.done.value) == int(i == STEPS - 1)
    for _ in range(3):
        await tick(dut)
        assert int(dut.signature.value) == sig
        assert int(dut.patterns_tested.value) == STEPS
        assert int(dut.done.value) == 1
    return sig

@cocotb.test()
async def lfsr_misr_reference_and_restart(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.start.value = 0
    await tick(dut)
    assert int(dut.signature.value) == 0
    assert int(dut.busy.value) == 0
    dut.rst.value = 0
    first = await run_bist(dut)
    second = await run_bist(dut)
    assert first == second, "same seed and response stream must produce same signature"
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.done.value) == 0
    assert int(dut.signature.value) == 0
    assert int(dut.patterns_tested.value) == 0
    dut._log.info("BIST 16-pattern reference signature: 0x%02x", first)
