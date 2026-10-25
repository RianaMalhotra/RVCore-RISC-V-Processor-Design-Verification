"""Integrated CPU-level misaligned SW must not partially modify data memory."""
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
async def misaligned_sw_is_atomic_and_halts(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    for pc, insn in [
        (0, 0x00400093),   # addi x1,x0,4
        (4, 0x05500113),   # addi x2,x0,85
        (8, 0x0020a023),   # sw x2,0(x1) - valid
    ]:
        await Timer(2, units="ns")
        assert int(dut.pc.value) == pc
        assert int(dut.instruction.value) == insn
        assert int(dut.halted.value) == 0
        assert int(dut.illegal.value) == 0
        await tick(dut)
    await Timer(2, units="ns")
    assert int(dut.protected_word.value) == 85, "baseline store did not commit"
    assert int(dut.pc.value) == 12
    assert int(dut.instruction.value) == 0x0020a0a3, "expected SW x2,1(x1)"
    assert int(dut.mem_store.value) == 1
    assert int(dut.mem_fault.value) == 1
    assert int(dut.illegal.value) == 1
    assert int(dut.write_enable.value) == 0
    await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == 12
    assert int(dut.protected_word.value) == 85, "faulting store corrupted memory"
    for _ in range(4):
        await tick(dut)
        assert int(dut.halted.value) == 1
        assert int(dut.pc.value) == 12
        assert int(dut.protected_word.value) == 85
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.halted.value) == 0
    assert int(dut.pc.value) == 0
    assert int(dut.protected_word.value) == 0
