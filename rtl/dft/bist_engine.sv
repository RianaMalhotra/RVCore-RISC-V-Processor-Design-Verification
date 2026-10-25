// Educational 8-bit LFSR pattern generator + MISR response compactor.
// Toy combinational circuit under test: response = pattern XOR 8'hA5.
// Standalone DFT experiment, not a CPU BIST implementation.
module bist_engine #(
    parameter int STEPS = 16
) (
    input logic clk, rst, start,
    output logic busy, done,
    output logic [7:0] pattern, signature,
    output logic [31:0] patterns_tested
);
    logic [7:0] response;
    logic [7:0] lfsr_next, misr_next;
    assign response = pattern ^ 8'hA5;
    // LFSR polynomial x^8+x^6+x^5+x^4+1, nonzero seed 8'h01.
    assign lfsr_next = {pattern[6:0], pattern[7] ^ pattern[5] ^ pattern[4] ^ pattern[3]};
    // MISR polynomial x^8+x^4+x^3+x^2+1, inject response each cycle.
    assign misr_next = {signature[6:0], 1'b0} ^
                       (signature[7] ? 8'h1D : 8'h00) ^ response;
    initial assert (STEPS > 0) else $fatal(1, "STEPS must be positive");
    always_ff @(posedge clk) begin
        if (rst) begin
            busy <= 1'b0;
            done <= 1'b0;
            pattern <= 8'h01;
            signature <= 8'h00;
            patterns_tested <= 32'd0;
        end else if (start) begin
            busy <= 1'b1;
            done <= 1'b0;
            pattern <= 8'h01;
            signature <= 8'h00;
            patterns_tested <= 32'd0;
        end else if (busy) begin
            pattern <= lfsr_next;
            signature <= misr_next;
            patterns_tested <= patterns_tested + 32'd1;
            if (patterns_tested == STEPS - 1) begin
                busy <= 1'b0;
                done <= 1'b1;
            end
        end
    end
endmodule
