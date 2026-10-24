// RV32I B-type and J-type control-flow decoder and branch comparator.
// Combinational outputs; all offsets are sign-extended byte offsets.
module cpu_control_flow (
    input  logic [31:0] instruction,
    input  logic [31:0] rs1_value,
    input  logic [31:0] rs2_value,
    output logic        control_flow,
    output logic        legal,
    output logic        taken,
    output logic        link,
    output logic [31:0] offset,
    output logic        jalr
);
    logic [6:0] opcode;
    logic [2:0] funct3;
    assign opcode = instruction[6:0];
    assign funct3 = instruction[14:12];
    always_comb begin
        control_flow = 1'b0;
        legal = 1'b0;
        taken = 1'b0;
        link = 1'b0;
        offset = 32'b0;
        jalr = 1'b0;
        case (opcode)
            7'b1100011: begin // conditional branches
                control_flow = 1'b1;
                offset = {{19{instruction[31]}},instruction[31],instruction[7],
                          instruction[30:25],instruction[11:8],1'b0};
                case (funct3)
                    3'b000: begin legal = 1'b1; taken = rs1_value == rs2_value; end
                    3'b001: begin legal = 1'b1; taken = rs1_value != rs2_value; end
                    3'b100: begin legal = 1'b1; taken = $signed(rs1_value) < $signed(rs2_value); end
                    3'b101: begin legal = 1'b1; taken = $signed(rs1_value) >= $signed(rs2_value); end
                    3'b110: begin legal = 1'b1; taken = rs1_value < rs2_value; end
                    3'b111: begin legal = 1'b1; taken = rs1_value >= rs2_value; end
                    default: ;
                endcase
            end
            7'b1101111: begin // JAL
                control_flow = 1'b1;
                legal = 1'b1;
                taken = 1'b1;
                link = 1'b1;
                offset = {{11{instruction[31]}},instruction[31],instruction[19:12],
                          instruction[20],instruction[30:21],1'b0};
            end
            7'b1100111: begin // JALR
                control_flow = 1'b1;
                if (funct3 == 3'b000) begin
                    legal = 1'b1;
                    taken = 1'b1;
                    link = 1'b1;
                    jalr = 1'b1;
                    offset = {{20{instruction[31]}},instruction[31:20]};
                end
            end
            default: ;
        endcase
    end
endmodule
