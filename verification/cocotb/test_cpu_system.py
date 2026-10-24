"""Fetch-and-execute smoke test for the stored arithmetic program."""
import cocotb
from cocotb.triggers import Timer

async def settle():
    await Timer(2, unit="ns")

async def tick(dut):
    dut.clk.value = 0
    await settle()
    dut.clk.value = 1
    await settle()
    dut.clk.value = 0
    await settle()

@cocotb.test()
async def fetch_execute_and_halt(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
    dut.rst.value = 0

    # 5, 7, 12, 7, 4, 7, 3, 9
    expected_results = [5, 7, 12, 7, 4, 7, 3, 9]
    for index, expected in enumerate(expected_results):
        await settle()
        assert int(dut.pc.value) == index * 4
        assert int(dut.illegal.value) == 0
        assert int(dut.instruction.value) != 0
        assert int(dut.alu_result.value) == expected, f"step {index}"
        await tick(dut)
        assert int(dut.pc.value) == (index + 1) * 4
        assert int(dut.halted.value) == 0

    # Zero word is unsupported and halts the CPU without advancing PC.
    await settle()
    assert int(dut.instruction.value) == 0
    assert int(dut.illegal.value) == 1
    await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == 32
    await tick(dut)
    assert int(dut.pc.value) == 32

    # Reset replays the program from address zero.
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
    dut.rst.value = 0
    await settle()
    assert int(dut.instruction.value) == 0x00500093
