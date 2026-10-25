import cocotb
from cocotb.triggers import Timer

def rtype(f7, rs2, rs1, f3, rd=3):
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x33

def itype(imm, rs1, f3, rd=3):
    return ((imm & 0xfff) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x13

@cocotb.test()
async def integer_rv32i_operations(dut):
    cases = [
        (rtype(0, 2, 1, 1), 1, 4, 16), # SLL
        (rtype(0, 2, 1, 2), 0xffffffff, 2, 1), # SLT
        (rtype(0, 2, 1, 3), 0xffffffff, 2, 0), # SLTU
        (rtype(0, 2, 1, 5), 0x80000000, 4, 0x08000000), # SRL
        (rtype(0x20, 2, 1, 5), 0x80000000, 4, 0xf8000000), # SRA
        (itype(3, 1, 1), 7, 0, 56), # SLLI
        (itype(-1, 1, 2), 0, 0, 0), # SLTI
        (itype(1, 1, 3), 0xffffffff, 0, 0), # SLTIU
        (itype(3, 1, 5), 0x80000000, 0, 0x10000000), # SRLI
        (itype(0x403, 1, 5), 0x80000000, 0, 0xf0000000), # SRAI
        (0x123452b7, 0, 0, 0x12345000), # LUI
        (0x12345297, 0, 0, 0x12345020), # AUIPC (pc=0x20)
        (rtype(1, 2, 1, 1), 1, 2, None), # invalid M extension
        (itype(0x401, 1, 1), 1, 0, None), # invalid SLLI encoding
    ]
    for instruction, a, b, expected in cases:
        dut.instruction.value = instruction
        dut.pc.value = 0x20
        dut.rs1_value.value = a
        dut.rs2_value.value = b
        await Timer(2, unit="ns")
        assert int(dut.valid.value) == (expected is not None), hex(instruction)
        if expected is not None:
            assert int(dut.result.value) == expected, hex(instruction)
