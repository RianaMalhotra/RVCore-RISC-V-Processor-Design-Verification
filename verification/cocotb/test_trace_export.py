"""Export observed cocotb/Verilator CPU cycles; never recompute RTL results."""
import json
import os
from pathlib import Path
import cocotb
from cocotb.triggers import Timer

def value(signal):
    return int(signal.value)

def mnemonic(word):
    opcode = word & 0x7f
    f3 = (word >> 12) & 7
    f7 = (word >> 25) & 0x7f
    if opcode == 0x03: return {0:"LB",1:"LH",2:"LW",4:"LBU",5:"LHU"}.get(f3,"ILLEGAL")
    if opcode == 0x23: return {0:"SB",1:"SH",2:"SW"}.get(f3,"ILLEGAL")
    if opcode == 0x37: return "LUI"
    if opcode == 0x17: return "AUIPC"
    if opcode == 0x13:
        return {0:"ADDI",1:"SLLI",2:"SLTI",3:"SLTIU",4:"XORI",5:("SRAI" if f7 == 0x20 else "SRLI"),6:"ORI",7:"ANDI"}.get(f3,"UNKNOWN")
    if opcode == 0x33:
        return {0:("SUB" if f7 == 0x20 else "ADD"),1:"SLL",2:"SLT",3:"SLTU",4:"XOR",5:("SRA" if f7 == 0x20 else "SRL"),6:"OR",7:"AND"}.get(f3,"UNKNOWN")
    return "ILLEGAL"

async def tick(dut):
    dut.clk.value = 0
    await Timer(2, units="ns")
    dut.clk.value = 1
    await Timer(2, units="ns")
    dut.clk.value = 0
    await Timer(2, units="ns")

@cocotb.test()
async def export_trace(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0
    registers = [0] * 32
    memory = [0] * 256
    is_load_store = os.getenv("TRACE_PROGRAM", "integer") == "load_store"
    expected_cycles = 11 if is_load_store else 8
    cycles = []
    for index in range(64):
        await Timer(2, units="ns")
        pc = value(dut.pc)
        word = value(dut.instruction)
        illegal = bool(value(dut.illegal))
        we = bool(value(dut.register_write)) and not illegal
        rd = value(dut.rd_index)
        data = value(dut.write_data)
        event = {
            "cycle": index + 1, "pc": pc, "instruction": f"0x{word:08x}",
            "mnemonic": mnemonic(word), "rs1": (word >> 15) & 31,
            "rs2": (word >> 20) & 31, "rd": rd,
            "rs1_value": value(dut.rs1_value), "rs2_value": value(dut.rs2_value),
            "write_enable": we and rd != 0, "write_data": data,
            "memory_load": bool(value(dut.memory_load)),
            "memory_store": bool(value(dut.memory_store)),
            "memory_address": value(dut.memory_address),
            "memory_read_data": value(dut.memory_read),
            "memory_write_data": value(dut.memory_write_data),
            "memory_fault": bool(value(dut.memory_fault)),
            "illegal": illegal, "halted": bool(value(dut.halted)),
        }
        if we and rd != 0:
            registers[rd] = data
        # Memory snapshot reconstructed from observed successful RTL store events.
        if event["memory_store"] and not illegal:
            width = {0: 1, 1: 2, 2: 4}.get((word >> 12) & 7, 0)
            address = event["memory_address"]
            assert width and 0 <= address <= len(memory) - width
            for byte in range(width):
                memory[address + byte] = (event["memory_write_data"] >> (8 * byte)) & 255
        event["memory_after"] = memory.copy()
        event["registers_after"] = registers.copy()
        cycles.append(event)
        await tick(dut)
        if value(dut.halted):
            cycles[-1]["halted_after"] = True
            break
    assert cycles[-1].get("halted_after"), "program must halt"
    assert len(cycles) == expected_cycles, f"expected {expected_cycles} cycles, got {len(cycles)}"
    if is_load_store:
        assert cycles[-1]["pc"] == 40
        assert registers[7] == 0xFFFFFF80
        assert memory[64:68] == [0x80, 0xFF, 0xFF, 0xFF]
    else:
        assert registers[7] == 0x1018
    path = Path(os.getenv("TRACE_OUTPUT", "visualizer/public/trace.json")).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version":1,"source":"Verilator + cocotb RTL simulation","program":("programs/load_store.hex" if is_load_store else "programs/rv32i_integer.hex"),"cycles":cycles}, indent=2) + "\n")
    dut._log.info("Exported %d observed cycles to %s", len(cycles), path)
