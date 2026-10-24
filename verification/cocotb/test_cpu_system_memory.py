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
async def stored_program_memory_roundtrip(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    # Load result appears on the register-file writeback bus before clock edge.
    expected = {3: 0xffffff80, 4: 0x80, 6: 0xffffff80,
                7: 0xff80, 9: 0xffffff80}
    for index in range(11):
        await settle()
        assert int(dut.pc.value) == index * 4
        if index in expected:
            assert int(dut.write_data.value) == expected[index], index
        assert int(dut.illegal.value) == (index == 10)
        await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == 40
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
