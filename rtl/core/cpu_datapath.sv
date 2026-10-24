// Single-cycle arithmetic-subset RV32I datapath.
// The instruction is supplied externally (instruction memory is a future milestone).
// The PC advances by four for each valid instruction; illegal instructions halt
// without a register write or PC advance until reset.
module cpu_datapath (
    input  logic        clk,
    input  logic        rst,
    input  logic [31:0] instruction,
    output logic [31:0] pc,
    output logic        halted,
    output logic        illegal,
    output logic [31:0] alu_result,
    output logic [31:0] rs1_value,
    output logic [31:0] rs2_value
);
    logic [4:0] rs1, rs2, rd;
    logic [31:0] immediate;
    logic [2:0] alu_op;
    logic use_imm, reg_write;
    logic [31:0] operand_b;
    logic zero;

    instruction_decoder decoder (
        .instruction(instruction), .rs1(rs1), .rs2(rs2), .rd(rd),
        .immediate(immediate), .alu_op(alu_op), .use_imm(use_imm),
        .reg_write(reg_write), .illegal(illegal)
    );

    register_file rf (
        .clk(clk), .rst(rst), .we(reg_write && !halted && !illegal),
        .rs1(rs1), .rs2(rs2), .rd(rd), .wd(alu_result),
        .rd1(rs1_value), .rd2(rs2_value)
    );

    assign operand_b = use_imm ? immediate : rs2_value;
    alu execute_alu (
        .a(rs1_value), .b(operand_b), .op(alu_op),
        .result(alu_result), .zero(zero)
    );

    always_ff @(posedge clk) begin
        if (rst) begin
            pc <= 32'b0;
            halted <= 1'b0;
        end else if (!halted) begin
            if (illegal) begin
                halted <= 1'b1;
            end else begin
                pc <= pc + 32'd4;
            end
        end
    end
endmodule
