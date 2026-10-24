"""Directed tests for all RV32I conditional branches and JAL/JALR."""
import cocotb
from cocotb.triggers import Timer

def branch(funct3, rs1=1, rs2=2, offset=-8):
    x = offset & 0x1fff
    return (((x >> 12) & 1) << 31 | ((x >> 5) & 63) << 25 |
            rs2 << 20 | rs1 << 15 | funct3 << 12 |
            ((x >> 1) & 15) << 8 | ((x >> 11) & 1) << 7 | 0x63)

def jal(rd=4, offset=8):
    x = offset & 0x1fffff
    return (((x >> 20) & 1) << 31 | ((x >> 1) & 1023) << 21 |
            ((x >> 11) & 1) << 20 | ((x >> 12) & 255) << 12 |
            rd << 7 | 0x6f)

async def evaluate(dut, insn, a, b):
    dut.instruction.value = insn
    dut.rs1_value.value = a & 0xffffffff
    dut.rs2_value.value = b & 0xffffffff
    await Timer(2, unit="ns")

@cocotb.test()
async def branches_signed_unsigned_and_jump(dut):
    cases = [
        (0, 7, 7, True), (0, 7, 8, False),
        (1, 7, 8, True), (1, 7, 7, False),
        (4, -1, 1, True), (4, 1, -1, False),
        (5, -1, 1, False), (5, 1, -1, True),
        (6, -1, 1, False), (6, 1, -1, True),
        (7, -1, 1, True), (7, 1, -1, False),
    ]
    for funct3, a, b, expected in cases:
        await evaluate(dut, branch(funct3), a, b)
        assert int(dut.control_flow.value) == 1
        assert int(dut.legal.value) == 1
        assert int(dut.taken.value) == expected
        assert int(dut.offset.value) == 0xfffffff8
        assert int(dut.link.value) == 0

    for offset in [8, -4, 2048, -2048]:
        await evaluate(dut, jal(offset=offset), 0, 0)
        assert int(dut.legal.value) == 1
        assert int(dut.taken.value) == 1
        assert int(dut.link.value) == 1
        assert int(dut.jalr.value) == 0
        assert int(dut.offset.value) == (offset & 0xffffffff)

    # jalr x4, -4(x1)
    await evaluate(dut, ((0xffc << 20) | (1 << 15) | (4 << 7) | 0x67), 20, 0)
    assert int(dut.legal.value) == 1
    assert int(dut.jalr.value) == 1
    assert int(dut.link.value) == 1
    assert int(dut.offset.value) == 0xfffffffc

    await evaluate(dut, branch(2), 0, 0)
    assert int(dut.control_flow.value) == 1
    assert int(dut.legal.value) == 0
    await evaluate(dut, 0x00001067, 0, 0)
    assert int(dut.control_flow.value) == 1
    assert int(dut.legal.value) == 0
