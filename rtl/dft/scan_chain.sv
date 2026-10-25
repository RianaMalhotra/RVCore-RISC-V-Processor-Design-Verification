// Educational, parameterized scan-register bank (not a synthesis-inserted CPU scan chain).
// Shift direction: scan_in enters bit 0; scan_out observes the MSB before each edge.
module scan_chain #(
    parameter int WIDTH = 8
) (
    input logic clk,
    input logic rst,
    input logic scan_enable,
    input logic scan_in,
    input logic [WIDTH-1:0] parallel_in,
    output logic scan_out,
    output logic [WIDTH-1:0] parallel_out
);
    initial assert (WIDTH >= 2) else $fatal(1, "WIDTH must be >= 2");
    logic [WIDTH-1:0] state;
    always_ff @(posedge clk) begin
        if (rst)
            state <= '0;
        else if (scan_enable)
            state <= (state << 1) | {{(WIDTH-1){1'b0}}, scan_in};
        else
            state <= parallel_in;
    end
    assign scan_out = state[WIDTH-1];
    assign parallel_out = state;
endmodule
