// Fault injection on the observable scan outputs, not physical scan cells.
// fault_enable=1 forces selected observable bit to fault_value.
module scan_fault_harness (
 input logic clk, rst, scan_enable, scan_in,
 input logic [7:0] parallel_in,
 input logic fault_enable, fault_value,
 input logic [2:0] fault_bit,
 output logic scan_out,
 output logic [7:0] parallel_out
);
 logic [7:0] good_state;
 logic unused_scan_out;
 scan_chain #(.WIDTH(8)) dut (
  .clk(clk), .rst(rst), .scan_enable(scan_enable), .scan_in(scan_in),
  .parallel_in(parallel_in), .scan_out(unused_scan_out),
  .parallel_out(good_state)
 );
 always_comb begin
  parallel_out = good_state;
  if (fault_enable) parallel_out[fault_bit] = fault_value;
 end
 assign scan_out = parallel_out[7];
endmodule
