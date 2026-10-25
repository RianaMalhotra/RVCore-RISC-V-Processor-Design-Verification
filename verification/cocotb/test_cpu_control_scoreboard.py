"""Architectural control-flow scoreboard for the stored branch-loop/JAL program."""
from pathlib import Path

import cocotb
from cocotb.triggers import Timer

MASK = 0xffffffff
PROGRAM = [int(line, 16) for line in Path("programs/control_flow.hex").read_text().splitlines() if line.strip()]

def signed(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

class Reference:
    def __init__(self):
        self.pc = 0
        self.regs = [0] * 32
        self.halted = False
        self.counts = {"addi": 0, "branch_taken": 0, "branch_not_taken": 0, "jal": 0, "illegal": 0}

    def step(self, word):
        opcode = word & 127
        rd = (word >> 7) & 31
        rs1 = (word >> 15) & 31
        rs2 = (word >> 20) & 31
        funct3 = (word >> 12) & 7
        pc = self.pc
        next_pc = (pc + 4) & MASK
        write = None
        if opcode == 0x13 and funct3 == 0:
            write = (rd, (self.regs[rs1] + signed(word >> 20, 12)) & MASK)
            self.counts["addi"] += 1
        elif opcode == 0x63:
            imm = (((word >> 31) & 1) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
            a, b = self.regs[rs1], self.regs[rs2]
            comparisons = {0: a == b, 1: a != b, 4: signed(a, 32) < signed(b, 32),
                           5: signed(a, 32) >= signed(b, 32), 6: a < b, 7: a >= b}
            if funct3 not in comparisons:
                self.halted = True
                self.counts["illegal"] += 1
                return None
            taken = comparisons[funct3]
            self.counts["branch_taken" if taken else "branch_not_taken"] += 1
            if taken:
                next_pc = (pc + signed(imm, 13)) & MASK
        elif opcode == 0x6f:
            imm = (((word >> 31) & 1) << 20) | (((word >> 12) & 255) << 12) | (((word >> 20) & 1) << 11) | (((word >> 21) & 1023) << 1)
            next_pc = (pc + signed(imm, 21)) & MASK
            write = (rd, (pc + 4) & MASK)
            self.counts["jal"] += 1
        elif opcode == 0x67 and funct3 == 0:
            next_pc = (self.regs[rs1] + signed(word >> 20, 12)) & 0xfffffffe
            write = (rd, (pc + 4) & MASK)
        else:
            self.halted = True
            self.counts["illegal"] += 1
            return None
        if next_pc & 3:
            self.halted = True
            self.counts["illegal"] += 1
            return None
        if write and write[0]:
            self.regs[write[0]] = write[1]
        self.pc = next_pc
        return write

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

@cocotb.test()
async def architectural_branch_loop_and_link(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    model = Reference()
    seen_pcs = []
    for cycle in range(32):
        await Timer(2, units="ns")
        pc = model.pc
        assert pc % 4 == 0 and pc // 4 < len(PROGRAM)
        word = PROGRAM[pc // 4]
        seen_pcs.append(pc)
        assert int(dut.pc.value) == pc, f"cycle {cycle}: PC"
        assert int(dut.instruction.value) == word, f"cycle {cycle}: instruction"
        assert int(dut.illegal.value) == (word == 0), f"cycle {cycle}: illegal"
        expected = model.step(word)
        if expected is not None and expected[0]:
            assert int(dut.effective_write.value) == 1, f"cycle {cycle}: write enable"
            assert int(dut.write_data.value) == expected[1], f"cycle {cycle}: writeback"
        else:
            assert int(dut.effective_write.value) == 0, f"cycle {cycle}: unexpected write"
        await tick(dut)
        assert int(dut.pc.value) == model.pc, f"cycle {cycle}: next PC"
        assert int(dut.halted.value) == int(model.halted), f"cycle {cycle}: halted"
        if model.halted:
            break
    else:
        assert False, "program did not halt within 32 cycles"
    assert seen_pcs == [0, 4, 8, 12, 16, 8, 12, 16, 8, 12, 16, 20, 28, 32]
    assert model.regs[1] == 0 and model.regs[2] == 3
    assert model.regs[4] == 24 and model.regs[5] == 7 and model.regs[3] == 0
    assert model.counts == {"addi": 8, "branch_taken": 2, "branch_not_taken": 1, "jal": 1, "illegal": 1}
    dut._log.info("Control-flow scoreboard coverage: %s", model.counts)
