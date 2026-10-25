"""Fault injection and clock-by-clock safety invariants for the data-memory RTL.

Checks rejected accesses never modify memory, no spurious fault appears when idle,
and valid reads preserve the previous stored value after each rejected store.
"""
import cocotb
from cocotb.triggers import Timer

async def settle():
    await Timer(2, units="ns")

async def tick(dut):
    dut.clk.value = 0
    await settle()
    dut.clk.value = 1
    await settle()
    dut.clk.value = 0
    await settle()

@cocotb.test()
async def rejected_stores_are_atomic_and_idle_is_safe(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.read_en.value = 0
    dut.write_en.value = 0
    dut.funct3.value = 2
    dut.address.value = 0
    dut.write_data.value = 0
    await tick(dut)
    dut.rst.value = 0

    # Initialize a known word and use legal reads to observe state.
    dut.write_en.value = 1
    dut.address.value = 4
    dut.write_data.value = 0x12345678
    await settle()
    assert int(dut.fault.value) == 0
    await tick(dut)
    dut.write_en.value = 0

    async def check_word():
        dut.read_en.value = 1
        dut.write_en.value = 0
        dut.address.value = 4
        dut.funct3.value = 2
        await settle()
        assert int(dut.fault.value) == 0
        assert int(dut.read_data.value) == 0x12345678
        dut.read_en.value = 0

    await check_word()
    # Misalignment, address bounds, and unsupported store encodings.
    for addr, kind in [(5, 2), (5, 1), (255, 2), (256, 0),
                       (0xffffffff, 0), (4, 3), (4, 7)]:
        dut.read_en.value = 0
        dut.write_en.value = 1
        dut.address.value = addr
        dut.funct3.value = kind
        dut.write_data.value = 0xdeadbeef
        await settle()
        assert int(dut.fault.value) == 1, (addr, kind)
        await tick(dut)
        dut.write_en.value = 0
        await check_word()

    # When neither read nor write is enabled, bad addresses must not fault.
    dut.address.value = 0xffffffff
    dut.funct3.value = 7
    dut.read_en.value = 0
    dut.write_en.value = 0
    await settle()
    assert int(dut.fault.value) == 0
    await tick(dut)
    await check_word()
    dut._log.info("Fault invariants passed: 7 rejected stores, idle no-fault")
