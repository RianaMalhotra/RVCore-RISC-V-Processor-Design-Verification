"""Verify misaligned taken BNE/BEQ-style branch target halts without committing."""
import cocotb
from cocotb.triggers import Timer

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

@cocotb.test()
async def misaligned_taken_branch_halts(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    for pc, instruction in [(0, 0x00100093), (4, 0x00100113)]:
        await Timer(2, units="ns")
        assert int(dut.pc.value) == pc
        assert int(dut.instruction.value) == instruction
        assert int(dut.write_enable.value) == 1
        await tick(dut)
        assert int(dut.halted.value) == 0
    # BEQ x1,x2,+2 is taken but its target (PC=10) is not 4-byte aligned.
    assert int(dut.pc.value) == 8
    await Timer(2, units="ns")
    assert int(dut.instruction.value) == 0x00208163
    assert int(dut.branch_taken.value) == 1
    assert int(dut.next_pc.value) == 10
    assert int(dut.write_enable.value) == 0
    await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == 8
    for _ in range(4):
        assert int(dut.write_enable.value) == 0
        await tick(dut)
        assert int(dut.halted.value) == 1
        assert int(dut.pc.value) == 8
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.halted.value) == 0
    assert int(dut.pc.value) == 0
