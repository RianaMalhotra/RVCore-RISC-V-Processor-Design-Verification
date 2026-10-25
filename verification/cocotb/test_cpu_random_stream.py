"""Deterministic seeded mixed ADDI/LW/SW program with independent state oracle."""
from pathlib import Path
import cocotb
from cocotb.triggers import Timer

WORDS = [int(x,16) for x in Path("programs/randomized_stream.hex").read_text().splitlines() if x.strip()]
MASK = 0xffffffff

def sext(n,b):
    n &= (1 << b)-1
    return n-(1 << b) if n & (1 << (b-1)) else n

async def tick(dut):
    dut.clk.value=0
    await Timer(2,units="ns")
    dut.clk.value=1
    await Timer(2,units="ns")
    dut.clk.value=0
    await Timer(2,units="ns")

@cocotb.test()
async def seeded_mixed_instruction_stream(dut):
    dut.clk.value=0
    dut.rst.value=1
    await tick(dut)
    dut.rst.value=0
    regs=[0]*32
    mem=bytearray(256)
    counts={"addi":0,"lw":0,"sw":0}
    for cycle,word in enumerate(WORDS):
        await Timer(2,units="ns")
        assert int(dut.pc.value)==cycle*4
        assert int(dut.instruction.value)==word
        op=word & 127
        rd=(word>>7)&31
        rs1=(word>>15)&31
        rs2=(word>>20)&31
        imm=sext(word>>20,12)
        expected=None
        if op==0x13:
            expected=(rd,(regs[rs1]+imm)&MASK)
            counts["addi"]+=1
        elif op==3:
            addr=(regs[rs1]+imm)&MASK
            assert addr%4==0 and addr+4<=256
            expected=(rd,int.from_bytes(mem[addr:addr+4],"little"))
            counts["lw"]+=1
        elif op==0x23:
            off=sext(((word>>25)<<5)|((word>>7)&31),12)
            addr=(regs[rs1]+off)&MASK
            assert addr%4==0 and addr+4<=256
            mem[addr:addr+4]=regs[rs2].to_bytes(4,"little")
            counts["sw"]+=1
        else:
            assert word==0
            assert int(dut.illegal.value)==1
            assert int(dut.write_enable.value)==0
            await tick(dut)
            assert int(dut.halted.value)==1
            assert int(dut.pc.value)==cycle*4
            break
        assert int(dut.illegal.value)==0
        assert int(dut.write_enable.value)==int(expected is not None and expected[0]!=0)
        if expected:
            assert int(dut.write_data.value)==expected[1],f"cycle {cycle}: writeback mismatch"
            if expected[0]: regs[expected[0]]=expected[1]
        await tick(dut)
        assert int(dut.halted.value)==0
    else:
        assert False,"missing termination"
    assert len(WORDS)==47
    assert counts["addi"]>10 and counts["sw"]>0 and counts["lw"]>0
    for _ in range(3):
        await tick(dut)
        assert int(dut.halted.value)==1
        assert int(dut.pc.value)==(len(WORDS)-1)*4
    dut._log.info("Seeded stream: %s",counts)
