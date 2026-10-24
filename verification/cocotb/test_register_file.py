"""Directed and reproducible randomized tests for the RV32I register file."""
import random

import cocotb
from cocotb.triggers import Timer

MASK = (1 << 32) - 1


async def settle():
    await Timer(1, unit="ns")


async def tick(dut):
    dut.clk.value = 0
    await settle()
    dut.clk.value = 1
    await settle()
    dut.clk.value = 0
    await settle()


async def read(dut, a, b):
    dut.rs1.value = a
    dut.rs2.value = b
    await settle()
    return int(dut.rd1.value), int(dut.rd2.value)


async def write(dut, addr, value, enabled=1):
    dut.rd.value = addr
    dut.wd.value = value & MASK
    dut.we.value = enabled
    await tick(dut)
    dut.we.value = 0


@cocotb.test()
async def register_file_directed(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.we.value = 0
    dut.rd.value = 0
    dut.wd.value = 0
    dut.rs1.value = 0
    dut.rs2.value = 0
    await tick(dut)
    dut.rst.value = 0

    for i in range(32):
        assert await read(dut, i, 0) == (0, 0)

    await write(dut, 0, MASK)
    assert await read(dut, 0, 0) == (0, 0)

    await write(dut, 1, 0x12345678)
    await write(dut, 31, MASK)
    assert await read(dut, 1, 31) == (0x12345678, MASK)
    assert await read(dut, 31, 1) == (MASK, 0x12345678)

    await write(dut, 1, 0, enabled=0)
    assert await read(dut, 1, 1) == (0x12345678, 0x12345678)

    # Writes take effect on the rising edge, not before it.
    dut.rd.value = 1
    dut.wd.value = 0xABCDEF01
    dut.we.value = 1
    await settle()
    assert await read(dut, 1, 1) == (0x12345678, 0x12345678)
    await tick(dut)
    dut.we.value = 0
    assert await read(dut, 1, 1) == (0xABCDEF01, 0xABCDEF01)

    # Synchronous reset has priority over an attempted write.
    dut.rst.value = 1
    dut.we.value = 1
    dut.rd.value = 2
    dut.wd.value = MASK
    await tick(dut)
    dut.rst.value = 0
    dut.we.value = 0
    for i in range(32):
        assert await read(dut, i, 0) == (0, 0)


@cocotb.test()
async def register_file_randomized(dut):
    rng = random.Random(2026)
    model = [0] * 32
    dut.clk.value = 0
    dut.rst.value = 1
    dut.we.value = 0
    dut.rd.value = 0
    dut.wd.value = 0
    dut.rs1.value = 0
    dut.rs2.value = 0
    await tick(dut)
    dut.rst.value = 0

    for _ in range(500):
        addr = rng.randrange(32)
        value = rng.getrandbits(32)
        enabled = rng.randrange(2)
        await write(dut, addr, value, enabled)
        if enabled and addr != 0:
            model[addr] = value
        a, b = rng.randrange(32), rng.randrange(32)
        actual = await read(dut, a, b)
        expected = (model[a], model[b])
        assert actual == expected, (
            f"rs1=x{a}, rs2=x{b}: got {actual}, expected {expected}"
        )

    for a in range(32):
        for b in range(32):
            assert await read(dut, a, b) == (model[a], model[b])
