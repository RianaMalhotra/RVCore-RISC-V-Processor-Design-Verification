module alu (
    input logic [31:0] a, b,
    input logic [2:0] op,
    output logic [31:0] result,
    output logic zero
);
    always_comb begin
        case (op)
            3'b000: result = a + b;
            3'b001: result = a - b;
            3'b010: result = a & b;
            3'b011: result = a | b;
            3'b100: result = a ^ b;
            default: result = 32'b0;
        endcase
    end
    assign zero = (result == 0);
endmodule
