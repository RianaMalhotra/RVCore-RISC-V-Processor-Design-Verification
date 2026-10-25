import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

DEPTH = 8

async def run_bist(dut, fault_enable, address=0, bit=0, value=0):
    dut.fault_enable.value = fault_enable
    dut.fault_address.value = address
    dut.fault_bit.value = bit
    dut.fault_value.value = value
    dut.start.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    dut.start.value = 0
    assert int(dut.busy.value) == 1
    for _ in range(4 * DEPTH + 8):
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        if int(dut.done.value):
            break
    else:
        assert False, "MBIST did not complete"
    assert int(dut.busy.value) == 0
    assert int(dut.comparisons.value) == 3 * DEPTH
    return int(dut._id('pass', extended=False).value), int(dut.errors.value)

@cocotb.test()
async def march_memory_bist_fault_campaign(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.start.value = 0
    dut.fault_enable.value = 0
    dut.fault_value.value = 0
    dut.fault_address.value = 0
    dut.fault_bit.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    dut.rst.value = 0
    passed, errors = await run_bist(dut, 0)
    assert passed == 1 and errors == 0
    detected = 0
    for addr in range(DEPTH):
        for bit in range(8):
            for stuck in (0, 1):
                passed, errors = await run_bist(dut, 1, addr, bit, stuck)
                assert passed == 0 and errors > 0, (addr, bit, stuck, errors)
                detected += 1
    dut._log.info("Detected %d/%d modeled stuck-at cell faults", detected, DEPTH * 8 * 2)
    passed, errors = await run_bist(dut, 0)
    assert passed == 1 and errors == 0
