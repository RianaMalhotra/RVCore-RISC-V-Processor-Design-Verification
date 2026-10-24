"""RV32I subset decoder checks; independent encoding reference vectors."""
import random
import cocotb
from cocotb.triggers import Timer

R_FUNCS = {(0, 0): 0, (0, 0x20): 1, (7, 0): 2, (6, 0): 3, (4, 0): 4}
I_FUNCS = {0: 0, 7: 2, 6: 3, 4: 4}

def encode_r(f3, f7, rs1=3, rs2=5, rd=7):
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x33

def encode_i(f3, imm, rs1=3, rd=7):
    return ((imm & 0xfff) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x13

async def check(dut, insn, op, imm_select, legal, rs1, rs2, rd, imm):
    dut.instruction.value = insn
    await Timer(1, unit="ns")
    assert int(dut.rs1.value) == rs1
    assert int(dut.rs2.value) == rs2
    assert int(dut.rd.value) == rd
    assert int(dut.immediate.value) == (imm & 0xffffffff)
    assert int(dut.illegal.value) == (not legal)
    assert int(dut.reg_write.value) == legal
    if legal:
        assert int(dut.alu_op.value) == op
        assert int(dut.use_imm.value) == imm_select

@cocotb.test()
async def directed_and_random_decoder(dut):
    rng = random.Random(2026)
    for _ in range(100):
        rs1, rs2, rd = (rng.randrange(32) for _ in range(3))
        for (f3, f7), op in R_FUNCS.items():
            insn = encode_r(f3, f7, rs1, rs2, rd)
            imm = (insn >> 20) & 0xfff
            imm = imm - 4096 if imm & 0x800 else imm
            await check(dut, insn, op, False, True, rs1, rs2, rd, imm)
        for f3, op in I_FUNCS.items():
            signed_imm = rng.randrange(-2048, 2048)
            insn = encode_i(f3, signed_imm, rs1, rd)
            await check(dut, insn, op, True, True, rs1, (insn >> 20) & 31, rd, signed_imm)

    # Unsupported shift, multiply, load, store, branch, and zero word.
    invalid = [encode_r(1, 0), encode_r(0, 1),
               encode_i(1, 3), encode_i(5, 3),
               0x00000003, 0x00000023, 0x00000063, 0]
    for insn in invalid:
        dut.instruction.value = insn
        await Timer(1, unit="ns")
        assert int(dut.illegal.value) == 1, hex(insn)
        assert int(dut.reg_write.value) == 0, hex(insn)
