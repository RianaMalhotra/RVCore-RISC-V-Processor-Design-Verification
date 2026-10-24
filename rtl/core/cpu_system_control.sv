// Single-cycle RV32I arithmetic + branch/jump CPU with instruction memory.
// Existing arithmetic modules are reused. No load/store or data memory.
module cpu_system_control #(
    parameter int IMEM_DEPTH = 64,
    parameter IMEM_FILE = "programs/control_flow.hex"
) (
    input logic clk,
    input logic rst,
    output logic [31:0] pc,
    output logic [31:0] instruction,
    output logic [31:0] alu_result,
    output logic halted,
    output logic illegal
);
    logic [4:0] rs1, rs2, rd;
    logic [31:0] immediate, rd1, rd2, operand_b;
    logic [2:0] alu_op;
    logic use_imm, reg_write, decode_illegal, zero;
    logic control_flow, cf_legal, taken, link, jalr;
    logic [31:0] offset, next_pc, target_pc, write_data;
    logic effective_write;

    instruction_memory #(.DEPTH(IMEM_DEPTH), .INIT_FILE(IMEM_FILE)) imem (
        .address(pc), .instruction(instruction)
    );
    instruction_decoder decoder (
        .instruction(instruction), .rs1(rs1), .rs2(rs2), .rd(rd),
        .immediate(immediate), .alu_op(alu_op), .use_imm(use_imm),
        .reg_write(reg_write), .illegal(decode_illegal)
    );
    cpu_control_flow flow (
        .instruction(instruction), .rs1_value(rd1), .rs2_value(rd2),
        .control_flow(control_flow), .legal(cf_legal), .taken(taken),
        .link(link), .offset(offset), .jalr(jalr)
    );
    assign illegal = control_flow ? !cf_legal : decode_illegal;
    assign effective_write = !halted && !illegal && !(control_flow && taken && next_pc[1:0] != 2'b00) && (reg_write || link);
    assign write_data = link ? pc + 32'd4 : alu_result;
    register_file rf (
        .clk(clk), .rst(rst), .we(effective_write),
        .rs1(rs1), .rs2(rs2), .rd(rd), .wd(write_data),
        .rd1(rd1), .rd2(rd2)
    );
    assign operand_b = use_imm ? immediate : rd2;
    alu execute_alu (
        .a(rd1), .b(operand_b), .op(alu_op), .result(alu_result), .zero(zero)
    );
    assign target_pc = jalr ? ((rd1 + offset) & 32'hfffffffe) : (pc + offset);
    assign next_pc = (control_flow && taken) ? target_pc : pc + 32'd4;

    always_ff @(posedge clk) begin
        if (rst) begin
            pc <= 32'b0;
            halted <= 1'b0;
        end else if (!halted) begin
            if (illegal || (control_flow && taken && next_pc[1:0] != 2'b00)) begin
                halted <= 1'b1;
            end else begin
                pc <= next_pc;
            end
        end
    end
endmodule
