import cocotb
from cocotb.triggers import Timer

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, unit="ns")
    dut.clk.value = 1
    await Timer(2, unit="ns")
    dut.clk.value = 0
    await Timer(2, unit="ns")

@cocotb.test()
async def integrated_integer_program(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    expected = [
        (0x00500093, 5),          # addi x1,x0,5
        (0x00309113, 40),         # slli x2,x1,3
        (0x0020a1b3, 1),          # slt x3,x1,x2
        (0xfff00213, 0xffffffff), # addi x4,x0,-1
        (0x40125293, 0xffffffff), # srai x5,x4,1
        (0x12345337, 0x12345000), # lui x6,0x12345
        (0x00001397, 0x1018),    # auipc x7,0x1 (pc=24)
    ]
    for index, (instruction, value) in enumerate(expected):
        await Timer(2, unit="ns")
        assert int(dut.pc.value) == index * 4
        assert int(dut.instruction.value) == instruction
        assert int(dut.illegal.value) == 0
        assert int(dut.write_data.value) == value
        await tick(dut)
    assert int(dut.pc.value) == 28
    assert int(dut.illegal.value) == 1
    await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == 28
