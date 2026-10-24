"""End-to-end control-flow tests and instruction encoding coverage."""
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
async def branch_loop_and_jump(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0

    # addi x1,3; addi x2,0; addi x2,x2,1; addi x1,x1,-1;
    # bne x1,x0,-8 loops until x1=0; jal x4,+8 skips addi x3,99;
    # addi x5,7; illegal sentinel halts.
    pcs = [0,4,8,12,16,8,12,16,8,12,16,20,28,32]
    for i, pc in enumerate(pcs):
        await settle()
        assert int(dut.pc.value) == pc, f"step {i}"
        assert int(dut.illegal.value) == (1 if pc == 32 else 0)
        if pc == 32:
            await tick(dut)
            assert int(dut.halted.value) == 1
            assert int(dut.pc.value) == 32
        else:
            await tick(dut)
    # Verify x2=3, x3=0 (skipped), x4=24 link, x5=7 via register reads
    # Internal register state is checked only after execution; x0 is immutable.
    assert int(dut.rf.registers[2].value) == 3
    assert int(dut.rf.registers[3].value) == 0
    assert int(dut.rf.registers[4].value) == 24
    assert int(dut.rf.registers[5].value) == 7
    assert int(dut.rf.registers[0].value) == 0

@cocotb.test()
async def reset_restarts_fetch(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    await tick(dut)
    assert int(dut.pc.value) == 4
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
