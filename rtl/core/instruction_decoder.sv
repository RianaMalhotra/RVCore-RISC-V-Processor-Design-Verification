// Combinational decoder for an intentionally limited RV32I arithmetic subset.
// Supported: ADD, SUB, AND, OR, XOR, ADDI, ANDI, ORI, XORI.
// Unsupported instructions are marked illegal with write enable deasserted.
module instruction_decoder (
    input  logic [31:0] instruction,
    output logic [4:0]  rs1,
    output logic [4:0]  rs2,
    output logic [4:0]  rd,
    output logic [31:0] immediate,
    output logic [2:0]  alu_op,
    output logic        use_imm,
    output logic        reg_write,
    output logic        illegal
);
    logic [6:0] opcode;
    logic [2:0] funct3;
    logic [6:0] funct7;

    assign opcode = instruction[6:0];
    assign funct3 = instruction[14:12];
    assign funct7 = instruction[31:25];

    always_comb begin
        rs1 = instruction[19:15];
        rs2 = instruction[24:20];
        rd = instruction[11:7];
        immediate = {{20{instruction[31]}}, instruction[31:20]};
        alu_op = 3'b000;
        use_imm = 1'b0;
        reg_write = 1'b0;
        illegal = 1'b1;

        case (opcode)
            7'b0110011: begin // R-type
                if (funct3 == 3'b000 && funct7 == 7'b0000000) begin
                    alu_op = 3'b000; illegal = 1'b0;
                end else if (funct3 == 3'b000 && funct7 == 7'b0100000) begin
                    alu_op = 3'b001; illegal = 1'b0;
                end else if (funct3 == 3'b111 && funct7 == 7'b0000000) begin
                    alu_op = 3'b010; illegal = 1'b0;
                end else if (funct3 == 3'b110 && funct7 == 7'b0000000) begin
                    alu_op = 3'b011; illegal = 1'b0;
                end else if (funct3 == 3'b100 && funct7 == 7'b0000000) begin
                    alu_op = 3'b100; illegal = 1'b0;
                end
                if (!illegal) reg_write = 1'b1;
            end
            7'b0010011: begin // I-type ALU, excluding shifts
                use_imm = 1'b1;
                case (funct3)
                    3'b000: begin alu_op = 3'b000; illegal = 1'b0; end // ADDI
                    3'b111: begin alu_op = 3'b010; illegal = 1'b0; end // ANDI
                    3'b110: begin alu_op = 3'b011; illegal = 1'b0; end // ORI
                    3'b100: begin alu_op = 3'b100; illegal = 1'b0; end // XORI
                    default: ;
                endcase
                if (!illegal) reg_write = 1'b1;
            end
            default: ;
        endcase
    end
endmodule
