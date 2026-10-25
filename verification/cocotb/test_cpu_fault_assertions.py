"""CPU-level fault injection with clock-by-clock halt and commit invariants."""
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
async def misaligned_load_halts_without_writeback(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    # ADDI x1,4; ADDI x2,85; SW x2,0(x1); misaligned LW x3,1(x1).
    for pc, insn, write in [
        (0, 0x00400093, 1),
        (4, 0x05500113, 1),
        (8, 0x0020a023, 0),
    ]:
        await settle()
        assert int(dut.pc.value) == pc
        assert int(dut.instruction.value) == insn
        assert int(dut.illegal.value) == 0
        assert int(dut.write_enable.value) == write
        await tick(dut)
        assert int(dut.halted.value) == 0
    assert int(dut.pc.value) == 12
    await settle()
    assert int(dut.instruction.value) == 0x0010a183
    assert int(dut.mem_fault.value) == 1, "misaligned LW must fault"
    assert int(dut.illegal.value) == 1
    assert int(dut.write_enable.value) == 0, "faulting LW must not commit register write"
    assert int(dut.mem_store.value) == 0
    await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == 12, "faulting instruction must not advance PC"
    # Once halted, no later instruction may execute or commit.
    for _ in range(4):
        await settle()
        assert int(dut.write_enable.value) == 0
        assert int(dut.pc.value) == 12
        await tick(dut)
        assert int(dut.halted.value) == 1
        assert int(dut.pc.value) == 12
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
    dut._log.info("CPU fault invariants: misaligned LW blocked; halt stable; reset recovered")
