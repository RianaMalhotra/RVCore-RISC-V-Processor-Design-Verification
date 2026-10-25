"""Independent observable-writeback scoreboard for the stored-program RV32I load/store CPU.

The oracle decodes instruction words from the program image and models registers,
little-endian memory, PC, and halt state; it never uses DUT writeback as expected data.
"""
from pathlib import Path

import cocotb
from cocotb.triggers import Timer

MASK = 0xFFFFFFFF
PROGRAM = [int(line.strip(), 16) for line in Path("programs/load_store.hex").read_text().splitlines() if line.strip()]

def sext(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

class ReferenceCPU:
    def __init__(self):
        self.pc = 0
        self.reg = [0] * 32
        self.mem = bytearray(256)
        self.halted = False
        self.counts = {"addi": 0, "load": 0, "store": 0, "illegal": 0}

    def step(self, insn):
        assert not self.halted
        opcode = insn & 127
        rd = (insn >> 7) & 31
        funct3 = (insn >> 12) & 7
        rs1 = (insn >> 15) & 31
        rs2 = (insn >> 20) & 31
        write = None
        if opcode == 0x13 and funct3 == 0:  # ADDI
            write = (rd, (self.reg[rs1] + sext(insn >> 20, 12)) & MASK)
            self.counts["addi"] += 1
        elif opcode in (0x03, 0x23):
            store = opcode == 0x23
            imm = (((insn >> 25) << 5) | ((insn >> 7) & 31)) if store else (insn >> 20)
            address = (self.reg[rs1] + sext(imm, 12)) & MASK
            sizes = ({0: 1, 1: 2, 2: 4} if store else {0: 1, 1: 2, 4: 1, 5: 2, 2: 4})
            size = sizes.get(funct3)
            if size is None or address + size > len(self.mem) or address % size:
                self.halted = True
                self.counts["illegal"] += 1
                return None
            if store:
                value = self.reg[rs2]
                for i in range(size):
                    self.mem[address + i] = (value >> (8 * i)) & 255
                self.counts["store"] += 1
            else:
                value = sum(self.mem[address + i] << (8 * i) for i in range(size))
                if funct3 in (0, 1):
                    value = sext(value, 8 * size) & MASK
                write = (rd, value)
                self.counts["load"] += 1
        else:
            self.halted = True
            self.counts["illegal"] += 1
            return None
        if write is not None and write[0] != 0:
            self.reg[write[0]] = write[1]
        self.pc = (self.pc + 4) & MASK
        return write

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

@cocotb.test()
async def architectural_register_and_memory_scoreboard(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    model = ReferenceCPU()
    for cycle, word in enumerate(PROGRAM):
        await Timer(2, units="ns")
        assert int(dut.pc.value) == model.pc, f"cycle={cycle}: PC mismatch"
        assert int(dut.instruction.value) == word, f"cycle={cycle}: fetch mismatch"
        expected_illegal = word == 0
        assert int(dut.illegal.value) == int(expected_illegal), f"cycle={cycle}: illegal mismatch"
        expected_write = model.step(word)
        if expected_write is not None and expected_write[0] != 0:
            assert int(dut.write_data.value) == expected_write[1], (
                f"cycle={cycle}: x{expected_write[0]} writeback expected "
                f"0x{expected_write[1]:08x}, got 0x{int(dut.write_data.value):08x}")
            assert int(dut.effective_write.value) == 1, f"cycle={cycle}: missing write enable"
        else:
            assert int(dut.effective_write.value) == 0, f"cycle={cycle}: spurious register write"
        await tick(dut)
        assert int(dut.pc.value) == model.pc, f"cycle={cycle}: next PC mismatch"
        assert int(dut.halted.value) == int(model.halted), f"cycle={cycle}: halt mismatch"
        # Architectural state is checked through observable writeback and
        # subsequent load results. Avoid relying on simulator-private arrays.
    assert model.halted and model.pc == 40
    assert model.counts == {"addi": 2, "load": 5, "store": 3, "illegal": 1}
    dut._log.info("CPU architectural scoreboard passed: %s", model.counts)
