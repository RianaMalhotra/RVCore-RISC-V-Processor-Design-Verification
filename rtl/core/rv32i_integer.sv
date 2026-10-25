// RV32I integer execute unit. Independent of legacy arithmetic-subset decoder.
module rv32i_integer (
    input logic [31:0] instruction, pc, rs1_value, rs2_value,
    output logic [31:0] result,
    output logic valid
);
    logic [6:0] opcode, funct7;
    logic [2:0] funct3;
    logic [31:0] operand, imm_i;
    assign opcode = instruction[6:0];
    assign funct3 = instruction[14:12];
    assign funct7 = instruction[31:25];
    assign imm_i = {{20{instruction[31]}},instruction[31:20]};
    assign operand = opcode == 7'b0010011 ? imm_i : rs2_value;
    always_comb begin
        result = 32'b0;
        valid = 1'b0;
        case (opcode)
            7'b0110111: begin // LUI
                result = {instruction[31:12],12'b0};
                valid = 1'b1;
            end
            7'b0010111: begin // AUIPC
                result = pc + {instruction[31:12],12'b0};
                valid = 1'b1;
            end
            7'b0110011, 7'b0010011: begin
                case (funct3)
                    3'b000: begin
                        if (opcode == 7'b0010011 || funct7 == 7'b0000000) begin
                            result = rs1_value + operand; valid = 1'b1;
                        end else if (funct7 == 7'b0100000) begin
                            result = rs1_value - operand; valid = 1'b1;
                        end
                    end
                    3'b001: if (opcode == 7'b0110011 ? funct7 == 7'b0000000 : funct7 == 7'b0000000) begin
                        result = rs1_value << (opcode == 7'b0010011 ? instruction[24:20] : rs2_value[4:0]);
                        valid = 1'b1;
                    end
                    3'b010: if (opcode == 7'b0010011 || funct7 == 7'b0000000) begin
                        result = {31'b0,($signed(rs1_value) < $signed(operand))}; valid = 1'b1;
                    end
                    3'b011: if (opcode == 7'b0010011 || funct7 == 7'b0000000) begin
                        result = {31'b0,(rs1_value < operand)}; valid = 1'b1;
                    end
                    3'b100: if (opcode == 7'b0010011 || funct7 == 7'b0000000) begin
                        result = rs1_value ^ operand; valid = 1'b1;
                    end
                    3'b101: begin
                        if (funct7 == 7'b0000000) begin
                            result = rs1_value >> (opcode == 7'b0010011 ? instruction[24:20] : rs2_value[4:0]);
                            valid = 1'b1;
                        end else if (funct7 == 7'b0100000) begin
                            result = $signed(rs1_value) >>> (opcode == 7'b0010011 ? instruction[24:20] : rs2_value[4:0]);
                            valid = 1'b1;
                        end
                    end
                    3'b110: if (opcode == 7'b0010011 || funct7 == 7'b0000000) begin
                        result = rs1_value | operand; valid = 1'b1;
                    end
                    3'b111: if (opcode == 7'b0010011 || funct7 == 7'b0000000) begin
                        result = rs1_value & operand; valid = 1'b1;
                    end
                    default: ;
                endcase
            end
            default: ;
        endcase
    end
endmodule
