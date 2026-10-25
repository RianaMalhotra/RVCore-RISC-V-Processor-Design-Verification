// Fault-injectable version of the educational toy BIST experiment.
// Forces one bit of CUT response to stuck-at-0 or stuck-at-1 before MISR capture.
module bist_fault_engine #(
    parameter int STEPS = 16
) (
    input logic clk, rst, start,
    input logic fault_enable, fault_value,
    input logic [2:0] fault_bit,
    output logic busy, done,
    output logic [7:0] pattern, signature,
    output logic [31:0] patterns_tested
);
    logic [7:0] response, misr_next, lfsr_next;
    always_comb begin
        response = pattern ^ 8'hA5;
        if (fault_enable) response[fault_bit] = fault_value;
    end
    assign lfsr_next = {pattern[6:0], pattern[7] ^ pattern[5] ^ pattern[4] ^ pattern[3]};
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
