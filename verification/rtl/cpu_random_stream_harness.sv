// Stored seeded instruction stream; no production RTL changes.
module cpu_random_stream_harness (
 input logic clk,rst,
 output logic [31:0] pc,instruction,write_data,
 output logic halted,illegal,write_enable
);
 logic [31:0] alu_result;
 cpu_system_memory #(.IMEM_FILE("programs/randomized_stream.hex")) cpu (
  .clk(clk),.rst(rst),.pc(pc),.instruction(instruction),
  .alu_result(alu_result),.halted(halted),.illegal(illegal)
 );
 assign write_data=cpu.write_data;
 assign write_enable=cpu.effective_write;
 a_halt_no_write: assert property (@(posedge clk) disable iff(rst)
   halted |-> !write_enable);
 a_halt_pc_stable: assert property (@(posedge clk) disable iff(rst)
   halted |=> $stable(pc));
endmodule
