"""Directed and deterministic randomized ALU tests."""
import random
import cocotb
from cocotb.triggers import Timer

MASK = (1 << 32) - 1

def reference(a, b, op):
    return {
        0: (a + b) & MASK,
        1: (a - b) & MASK,
        2: a & b,
        3: a | b,
        4: a ^ b,
    }.get(op, 0)

@cocotb.test()
async def alu_directed_and_random(dut):
    pairs = [
        (0, 0), (MASK, 1), (0, 1),
        (0x80000000, 0x80000000),
        (0xAAAAAAAA, 0x55555555), (123, 123),
    ]
    rng = random.Random(2026)
    pairs += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(200)]
    for a, b in pairs:
        for op in range(8):
            dut.a.value, dut.b.value, dut.op.value = a, b, op
            await Timer(1, unit="ns")
            expected = reference(a, b, op)
            assert int(dut.result.value) == expected, (
                f"op={op}, a={a:#x}, b={b:#x}: expected {expected:#x}")
            assert int(dut.zero.value) == (expected == 0)
