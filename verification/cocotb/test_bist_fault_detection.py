"""Measure detection of 16 modeled response stuck-at faults via BIST signatures."""
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

def oracle(bit=None, stuck=0):
    pattern, signature = 1, 0
    for _ in range(STEPS):
        response = pattern ^ 0xa5
        if bit is not None:
            response = (response & ~(1 << bit)) | (stuck << bit)
        signature = (((signature << 1) & 255) ^
                     (0x1d if signature & 0x80 else 0) ^ response)
        pattern = ((pattern << 1) & 255) | (
            ((pattern >> 7) ^ (pattern >> 5) ^ (pattern >> 4) ^ (pattern >> 3)) & 1)
    return signature

async def run(dut, bit=None, stuck=0):
    dut.fault_enable.value = int(bit is not None)
    dut.fault_bit.value = bit if bit is not None else 0
    dut.fault_value.value = stuck
    dut.start.value = 1
    await tick(dut)
    dut.start.value = 0
    assert int(dut.busy.value) == 1
    for _ in range(STEPS):
        await tick(dut)
    assert int(dut.busy.value) == 0
    assert int(dut.done.value) == 1
    assert int(dut.patterns_tested.value) == STEPS
    result = int(dut.signature.value)
    assert result == oracle(bit, stuck), (bit, stuck, result, oracle(bit, stuck))
    return result

@cocotb.test()
async def signature_based_stuck_at_detection(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.start.value = 0
    dut.fault_enable.value = 0
    dut.fault_bit.value = 0
    dut.fault_value.value = 0
    await tick(dut)
    dut.rst.value = 0
    golden = await run(dut)
    detected = 0
    aliased = []
    for bit in range(8):
        for stuck in (0, 1):
            faulty = await run(dut, bit, stuck)
            if faulty != golden:
                detected += 1
            else:
                aliased.append((bit, stuck))
    assert detected + len(aliased) == 16
    # Report measured outcomes, without assuming a 100% detection rate.
    dut._log.info("BIST signature 0x%02x: %d/16 detected; aliases=%s",
                  golden, detected, aliased)
    assert detected > 0, "No modeled faults detected"
    assert await run(dut) == golden, "Golden signature changed after fault campaigns"
