"""DFT scan chain: capture, shift order, serial observability, reset and random patterns."""
import random
import cocotb
from cocotb.triggers import Timer

WIDTH = 8
MASK = (1 << WIDTH) - 1

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

async def capture(dut, word):
    dut.scan_enable.value = 0
    dut.parallel_in.value = word
    await tick(dut)
    assert int(dut.parallel_out.value) == word

async def shift(dut, bit, state):
    dut.scan_enable.value = 1
    dut.scan_in.value = bit
    await Timer(2, units="ns")
    assert int(dut.scan_out.value) == (state >> (WIDTH-1)) & 1
    await tick(dut)
    new_state = ((state << 1) | bit) & MASK
    assert int(dut.parallel_out.value) == new_state
    return new_state

@cocotb.test()
async def scan_capture_shift_and_reset(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.scan_enable.value = 0
    dut.scan_in.value = 0
    dut.parallel_in.value = 0
    await tick(dut)
    assert int(dut.parallel_out.value) == 0
    dut.rst.value = 0

    for word in [0x00, 0xff, 0xa5, 0x81, 0x3c]:
        await capture(dut, word)
        state = word
        for _ in range(WIDTH):
            state = await shift(dut, 0, state)
        assert state == 0

    rng = random.Random(20261025)
    for _ in range(40):
        word = rng.randrange(1 << WIDTH)
        await capture(dut, word)
        state = word
        observed = []
        for _ in range(WIDTH):
            observed.append((state >> (WIDTH-1)) & 1)
            state = await shift(dut, rng.randrange(2), state)
        assert observed == [(word >> i) & 1 for i in reversed(range(WIDTH))]

    # Scan mode overrides parallel input, and reset overrides scan shifting.
    dut.parallel_in.value = 0xff
    dut.scan_enable.value = 1
    dut.scan_in.value = 1
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.parallel_out.value) == 0
    dut.rst.value = 0
    await tick(dut)
    assert int(dut.parallel_out.value) == 1
