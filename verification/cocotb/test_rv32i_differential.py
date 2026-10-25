"""Seeded RV32I integer differential verification with a Python reference model.

The oracle uses instruction semantics, not DUT result signals. Coverage counts
are observed test stimuli (not a claim of complete ISA functional coverage).
"""
import random
import json
from pathlib import Path
from collections import Counter

import cocotb
from cocotb.triggers import Timer

MASK = 0xFFFFFFFF
SEED = 0x20261025
R_OPS = ("ADD", "SUB", "SLL", "SLT", "SLTU", "XOR", "SRL", "SRA", "OR", "AND")
I_OPS = ("ADDI", "SLLI", "SLTI", "SLTIU", "XORI", "SRLI", "SRAI", "ORI", "ANDI")
U_OPS = ("LUI", "AUIPC")
ALL_OPS = R_OPS + I_OPS + U_OPS
F3 = {"ADD":0, "SUB":0, "SLL":1, "SLT":2, "SLTU":3,
      "XOR":4, "SRL":5, "SRA":5, "OR":6, "AND":7,
      "ADDI":0, "SLLI":1, "SLTI":2, "SLTIU":3, "XORI":4,
      "SRLI":5, "SRAI":5, "ORI":6, "ANDI":7}

def signed(x):
    x &= MASK
    return x - (1 << 32) if x & (1 << 31) else x

def encode(op, imm, rs1=1, rs2=2, rd=3):
    if op in R_OPS:
        f7 = 0x20 if op in ("SUB", "SRA") else 0
        return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (F3[op] << 12) | (rd << 7) | 0x33
    if op in I_OPS:
        if op in ("SLLI", "SRLI", "SRAI"):
            imm = (imm & 31) | (0x400 if op == "SRAI" else 0)
        return ((imm & 0xFFF) << 20) | (rs1 << 15) | (F3[op] << 12) | (rd << 7) | 0x13
    return (imm & 0xFFFFF000) | (rd << 7) | (0x37 if op == "LUI" else 0x17)

def reference(op, a, b, imm, pc):
    a, b, pc = a & MASK, b & MASK, pc & MASK
    if op in U_OPS:
        upper = imm & 0xFFFFF000
        return (upper if op == "LUI" else pc + upper) & MASK
    rhs = (signed((imm & 0xFFF) | (0xFFFFF000 if imm & 0x800 else 0)) if op in I_OPS and op not in ("SLLI", "SRLI", "SRAI") else b) & MASK
    if op in ("ADDI", "ADD"): return (a + rhs) & MASK
    if op == "SUB": return (a - rhs) & MASK
    if op in ("SLL", "SLLI"): return (a << ((imm if op == "SLLI" else b) & 31)) & MASK
    if op in ("SLT", "SLTI"): return int(signed(a) < signed(rhs))
    if op in ("SLTU", "SLTIU"): return int(a < rhs)
    if op in ("XOR", "XORI"): return a ^ rhs
    if op in ("SRL", "SRLI"): return a >> ((imm if op == "SRLI" else b) & 31)
    if op in ("SRA", "SRAI"): return (signed(a) >> ((imm if op == "SRAI" else b) & 31)) & MASK
    if op in ("OR", "ORI"): return a | rhs
    if op in ("AND", "ANDI"): return a & rhs
    raise ValueError(op)

async def check(dut, instruction, a, b, pc, expected_valid, expected, context):
    dut.instruction.value = instruction
    dut.rs1_value.value = a & MASK
    dut.rs2_value.value = b & MASK
    dut.pc.value = pc & MASK
    await Timer(2, units="ns")
    valid = int(dut.valid.value)
    assert valid == int(expected_valid), (
        f"{context}: instruction=0x{instruction:08x}, valid={valid}, expected={expected_valid}")
    if expected_valid:
        result = int(dut.result.value)
        assert result == expected, (
            f"{context}: instruction=0x{instruction:08x}, a=0x{a:08x}, "
            f"b=0x{b:08x}, pc=0x{pc:08x}, result=0x{result:08x}, expected=0x{expected:08x}")

@cocotb.test()
async def seeded_differential_and_coverage(dut):
    rng = random.Random(SEED)
    coverage = Counter()
    operand_bins = Counter()
    validity_bins = Counter()
    boundaries = (0, 1, 31, 32, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0x55555555, 0xAAAAAAAA)
    # Exercise every operation with all boundary source values.
    for op in ALL_OPS:
        for a in boundaries:
            for b in boundaries:
                imm = (b & 0xFFF) if op not in U_OPS else (b & 0xFFFFF000)
                pc = 0x1000
                insn = encode(op, imm)
                await check(dut, insn, a, b, pc, True, reference(op, a, b, imm if op not in ("SLLI", "SRLI", "SRAI") else (imm & 31), pc), f"directed {op}")
                coverage[op] += 1
                for operand in (a, b):
                    operand_bins['zero' if operand == 0 else 'negative' if operand & 0x80000000 else 'positive'] += 1
                validity_bins['legal'] += 1
    # Randomized operands, signed immediates, shifts, and PC wraparound.
    for index in range(2100):
        op = ALL_OPS[index % len(ALL_OPS)]
        a, b, pc = rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32) & ~3
        imm = rng.randrange(-2048, 2048) if op in I_OPS else rng.getrandbits(32)
        if op in ("SLLI", "SRLI", "SRAI"): imm &= 31
        insn = encode(op, imm)
        await check(dut, insn, a, b, pc, True, reference(op, a, b, imm, pc),
                    f"random seed={SEED} iteration={index} op={op}")
        coverage[op] += 1
        for operand in (a, b):
            operand_bins['zero' if operand == 0 else 'negative' if operand & 0x80000000 else 'positive'] += 1
        validity_bins['legal'] += 1
    # Unsupported encodings must not assert valid, even when operands vary.
    invalid = [
        encode("ADD", 0) | (1 << 25),          # M extension
        encode("SLL", 0) | (0x20 << 25),      # illegal SLL funct7
        encode("SLLI", 1) | (1 << 25),        # illegal SLLI funct7
        encode("SRLI", 1) | (1 << 25),        # illegal SRLI funct7
        0x00000073,                          # ECALL not implemented
        0x00100073,                          # EBREAK not implemented
        0x0000000F,                          # FENCE not implemented
        0xFFFFFFFF,                          # reserved
    ]
    for insn in invalid:
        for _ in range(8):
            await check(dut, insn, rng.getrandbits(32), rng.getrandbits(32),
                        rng.getrandbits(32), False, None, "negative")
            coverage["illegal"] += 1
            validity_bins["illegal"] += 1
    assert all(coverage[op] >= 100 for op in ALL_OPS)
    assert coverage["illegal"] == 64
    dut._log.info("M10 deterministic differential coverage: seed=%d; total=%d; per-op=%s",
                  SEED, sum(coverage.values()), dict(sorted(coverage.items())))

    # Measured stimulus bins: generated only after all oracle checks succeed.
    report = {
        "schema_version": 1,
        "seed": SEED,
        "scope": "rv32i_integer combinational differential tests only",
        "operation_counts": dict(sorted(coverage.items())),
        "operand_sign_bins": dict(sorted(operand_bins.items())),
        "validity_bins": dict(sorted(validity_bins.items())),
        "operation_bin_coverage": {"hit": sum(coverage[op] > 0 for op in ALL_OPS), "total": len(ALL_OPS)},
        "limitations": "Stimulus counts, not RTL code coverage, branch coverage, cross coverage, or full ISA closure",
    }
    output = Path("verification/reports/rv32i_functional_coverage.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
