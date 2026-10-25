"""Independent JALR program oracle: target masking, signed offset, links and skipped code."""
from pathlib import Path
import cocotb
from cocotb.triggers import Timer

PROGRAM = [int(s, 16) for s in Path("programs/jalr_end_to_end.hex").read_text().splitlines() if s.strip()]
MASK = 0xffffffff

def sext(value, width):
    value &= (1 << width) - 1
    return value - (1 << width) if value & (1 << (width - 1)) else value

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

@cocotb.test()
async def indirect_jumps_and_link_registers(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    pc, regs, seen, jumps = 0, [0] * 32, [], 0
    for cycle in range(16):
        await Timer(2, units="ns")
        assert pc % 4 == 0 and pc // 4 < len(PROGRAM)
        word = PROGRAM[pc // 4]
        seen.append(pc)
        assert int(dut.pc.value) == pc, f"cycle {cycle}: PC"
        assert int(dut.instruction.value) == word, f"cycle {cycle}: fetch"
        opcode = word & 0x7f
        rd = (word >> 7) & 31
        rs1 = (word >> 15) & 31
        funct3 = (word >> 12) & 7
        expected_write = None
        next_pc = (pc + 4) & MASK
        if opcode == 0x13 and funct3 == 0:
            expected_write = (rd, (regs[rs1] + sext(word >> 20, 12)) & MASK)
        elif opcode == 0x67 and funct3 == 0:
            jumps += 1
            next_pc = (regs[rs1] + sext(word >> 20, 12)) & 0xfffffffe
            assert next_pc % 4 == 0, "test program unexpectedly misaligned"
            expected_write = (rd, (pc + 4) & MASK)
            assert int(dut.jalr.value) == 1
            assert int(dut.next_pc.value) == next_pc, f"cycle {cycle}: indirect target"
        else:
            assert word == 0, f"unexpected illegal instruction: 0x{word:08x}"
            assert int(dut.illegal.value) == 1
            assert int(dut.write_enable.value) == 0
            await tick(dut)
            assert int(dut.halted.value) == 1
            assert int(dut.pc.value) == pc
            break
        assert int(dut.illegal.value) == 0
        assert int(dut.write_enable.value) == int(expected_write[0] != 0)
        assert int(dut.write_data.value) == expected_write[1], f"cycle {cycle}: link/data"
        if expected_write[0]:
            regs[expected_write[0]] = expected_write[1]
        pc = next_pc
        await tick(dut)
        assert int(dut.pc.value) == pc
        assert int(dut.halted.value) == 0
    else:
        assert False, "JALR program did not halt"
    assert seen == [0, 4, 16, 20, 24, 32, 36], seen
    assert jumps == 2
    assert regs[5] == 8 and regs[6] == 9
    assert regs[7] == 28 and regs[8] == 30
    assert regs[3] == 0 and regs[4] == 0, "skipped instructions executed"
    for _ in range(3):
        await tick(dut)
        assert int(dut.pc.value) == 36
        assert int(dut.write_enable.value) == 0
    dut.rst.value = 1
    await tick(dut)
    assert int(dut.pc.value) == 0
    assert int(dut.halted.value) == 0
