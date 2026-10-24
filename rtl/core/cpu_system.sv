// Instruction-fetch wrapper for the arithmetic-subset single-cycle CPU.
// Instruction memory is read-only; no branch, jump, load/store, or data memory.
module cpu_system #(
    parameter int IMEM_DEPTH = 64,
    parameter IMEM_FILE = "programs/arithmetic.hex"
) (
    input logic clk,
    input logic rst,
    output logic [31:0] pc,
    output logic [31:0] instruction,
    output logic [31:0] alu_result,
    output logic halted,
    output logic illegal
);
    logic [31:0] rs1_value, rs2_value;
    instruction_memory #(.DEPTH(IMEM_DEPTH), .INIT_FILE(IMEM_FILE)) imem (
        .address(pc), .instruction(instruction)
    );
    cpu_datapath core (
        .clk(clk), .rst(rst), .instruction(instruction), .pc(pc),
        .halted(halted), .illegal(illegal), .alu_result(alu_result),
        .rs1_value(rs1_value), .rs2_value(rs2_value)
    );
endmodule
