"""End-to-end arithmetic program and illegal-instruction halt tests."""
import cocotb
from cocotb.triggers import Timer

MASK = (1 << 32) - 1

def i_type(funct3, imm, rs1, rd):
    return ((imm & 0xfff) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0x13

def r_type(funct3, funct7, rs1, rs2, rd):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | 0x33

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
async def execute_arithmetic_program(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.instruction.value = 0
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
    dut.rst.value = 0

    # Instruction, expected destination register, expected writeback.
    program = [
        (i_type(0, 12, 0, 1), 1, 12),           # addi x1,x0,12
        (i_type(0, -5, 0, 2), 2, MASK - 4),     # addi x2,x0,-5
        (r_type(0, 0, 1, 2, 3), 3, 7),          # add x3,x1,x2
        (r_type(0, 0x20, 1, 2, 4), 4, 17),     # sub x4,x1,x2
        (r_type(7, 0, 1, 3, 5), 5, 4),         # and x5,x1,x3
        (r_type(6, 0, 1, 3, 6), 6, 15),        # or x6,x1,x3
        (r_type(4, 0, 1, 3, 7), 7, 11),        # xor x7,x1,x3
        (i_type(7, 6, 1, 8), 8, 4),           # andi x8,x1,6
        (i_type(6, 1, 3, 9), 9, 7),           # ori x9,x3,1
        (i_type(4, -1, 3, 10), 10, MASK ^ 7), # xori x10,x3,-1
        (i_type(0, 99, 0, 0), 0, 99),         # x0 ignores write
    ]
    for index, (insn, rd, result) in enumerate(program):
        dut.instruction.value = insn
        await settle()
        assert int(dut.illegal.value) == 0
        assert int(dut.alu_result.value) == result, f"ALU mismatch at {index}"
        await tick(dut)
        assert int(dut.pc.value) == 4 * (index + 1)
        assert int(dut.halted.value) == 0
        if rd:
            # Read back written register through rs1 of a harmless ADDI.
            dut.instruction.value = i_type(0, 0, rd, 0)
            await settle()
            assert int(dut.rs1_value.value) == result, f"register x{rd} mismatch"
        else:
            dut.instruction.value = i_type(0, 0, 0, 0)
            await settle()
            assert int(dut.rs1_value.value) == 0

    dut.instruction.value = 0xffffffff
    await settle()
    assert int(dut.illegal.value) == 1
    pc_before = int(dut.pc.value)
    await tick(dut)
    assert int(dut.halted.value) == 1
    assert int(dut.pc.value) == pc_before

    # A valid instruction after a halt must not commit.
    dut.instruction.value = i_type(0, 123, 0, 11)
    await tick(dut)
    assert int(dut.pc.value) == pc_before
    dut.instruction.value = i_type(0, 0, 11, 0)
    await settle()
    assert int(dut.rs1_value.value) == 0

    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
    dut.rst.value = 0
    dut.instruction.value = i_type(0, 0, 1, 0)
    await settle()
    assert int(dut.rs1_value.value) == 0
