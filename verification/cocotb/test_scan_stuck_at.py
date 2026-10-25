"""Exhaustive single-bit output stuck-at detection with complementary capture patterns."""
import cocotb
from cocotb.triggers import Timer

async def tick(dut):
    dut.clk.value=0
    await Timer(2,units="ns")
    dut.clk.value=1
    await Timer(2,units="ns")
    dut.clk.value=0
    await Timer(2,units="ns")

@cocotb.test()
async def exhaustive_output_stuck_at_faults(dut):
    dut.clk.value=0
    dut.rst.value=1
    dut.scan_enable.value=0
    dut.scan_in.value=0
    dut.parallel_in.value=0
    dut.fault_enable.value=0
    dut.fault_value.value=0
    dut.fault_bit.value=0
    await tick(dut)
    dut.rst.value=0
    detected=0
    for bit in range(8):
        for stuck in (0,1):
            # Capture the opposite value to sensitize the chosen fault.
            pattern=(1<<bit) if stuck==0 else (0xff ^ (1<<bit))
            dut.parallel_in.value=pattern
            dut.fault_enable.value=0
            await tick(dut)
            assert int(dut.parallel_out.value)==pattern
            dut.fault_bit.value=bit
            dut.fault_value.value=stuck
            dut.fault_enable.value=1
            await Timer(2,units="ns")
            observed=int(dut.parallel_out.value)
            assert observed==(pattern ^ (1<<bit)),(bit,stuck,observed)
            detected+=int(observed!=pattern)
            # A matching value does not expose the fault.
            dut.parallel_in.value=(pattern ^ (1<<bit))
            dut.fault_enable.value=0
            await tick(dut)
            dut.fault_enable.value=1
            await Timer(2,units="ns")
            assert int(dut.parallel_out.value)==(pattern ^ (1<<bit))
            dut.fault_enable.value=0
    assert detected==16
    dut._log.info("Detected %d/16 modeled observable-output stuck-at faults",detected)
