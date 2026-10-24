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
async def byte_halfword_word_and_faults(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.read_en.value = 0
    dut.write_en.value = 0
    dut.address.value = 0
    dut.funct3.value = 0
    dut.write_data.value = 0
    await tick(dut)
    dut.rst.value = 0

    async def store(addr, f, data):
        dut.read_en.value = 0
        dut.write_en.value = 1
        dut.address.value = addr
        dut.funct3.value = f
        dut.write_data.value = data
        await settle()
        assert int(dut.fault.value) == 0
        await tick(dut)
        dut.write_en.value = 0

    async def read(addr, f, expected):
        dut.read_en.value = 1
        dut.write_en.value = 0
        dut.address.value = addr
        dut.funct3.value = f
        await settle()
        assert int(dut.fault.value) == 0
        assert int(dut.read_data.value) == expected
        dut.read_en.value = 0

    await store(4, 2, 0x80ff1234)
    await read(4, 2, 0x80ff1234)
    await read(4, 0, 0x34)
    await read(5, 0, 0x12)
    await read(6, 0, 0xffffffff)
    await read(6, 4, 0xff)
    await read(6, 1, 0xffff80ff)
    await read(6, 5, 0x80ff)
    await store(7, 0, 0x55)
    await read(4, 2, 0x55ff1234)
    await store(8, 1, 0xabcd)
    await read(8, 5, 0xabcd)
    await read(8, 1, 0xffffabcd)

    for addr, f, writing in [(5, 2, 0), (5, 1, 0), (255, 2, 1),
                             (256, 0, 0), (4, 3, 0), (4, 7, 1)]:
        dut.address.value = addr
        dut.funct3.value = f
        dut.read_en.value = 0 if writing else 1
        dut.write_en.value = 1 if writing else 0
        await settle()
        assert int(dut.fault.value) == 1, (addr, f, writing)
        dut.read_en.value = 0
        dut.write_en.value = 0
    await read(4, 2, 0x55ff1234)
