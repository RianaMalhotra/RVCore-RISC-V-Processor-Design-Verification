// RV32I register file: two asynchronous read ports and one synchronous write port.
// Reset clears all registers for deterministic simulation; x0 always reads zero.
module register_file (
    input  logic        clk,
    input  logic        rst,
    input  logic        we,
    input  logic [4:0]  rs1,
    input  logic [4:0]  rs2,
    input  logic [4:0]  rd,
    input  logic [31:0] wd,
    output logic [31:0] rd1,
    output logic [31:0] rd2
);
    logic [31:0] registers [0:31];

    assign rd1 = (rs1 == 5'd0) ? 32'b0 : registers[rs1];
    assign rd2 = (rs2 == 5'd0) ? 32'b0 : registers[rs2];

    always_ff @(posedge clk) begin
        if (rst) begin
            for (int i = 0; i < 32; i++)
                registers[i] <= 32'b0;
        end else if (we && rd != 5'd0) begin
            registers[rd] <= wd;
        end
    end
endmodule
