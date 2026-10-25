// Verification-only observability for indirect control flow and writeback.
module cpu_jalr_harness (
    input logic clk, rst,
    output logic [31:0] pc, instruction, write_data, next_pc,
    output logic halted, illegal, write_enable, jalr
);
    logic [31:0] alu_result;
    cpu_system_memory #(.IMEM_FILE("programs/jalr_end_to_end.hex")) cpu (
        .clk(clk), .rst(rst), .pc(pc), .instruction(instruction),
        .alu_result(alu_result), .halted(halted), .illegal(illegal)
    );
    assign write_data = cpu.write_data;
    assign write_enable = cpu.effective_write;
    assign next_pc = cpu.next_pc;
    assign jalr = cpu.jalr;
    a_jalr_link: assert property (
        @(posedge clk) disable iff (rst)
        (jalr && !halted && !illegal && next_pc[1:0] == 2'b00)
            |-> (write_data == pc + 32'd4 && write_enable)
    ) else $error("JALR failed to commit return address");
    a_jalr_target_bit_zero: assert property (
        @(posedge clk) disable iff (rst)
        (jalr && !halted && !illegal) |-> !next_pc[0]
    ) else $error("JALR target bit zero was not cleared");
    a_halted_pc_stable: assert property (
        @(posedge clk) disable iff (rst)
        halted |=> $stable(pc)
    ) else $error("PC advanced while halted");
endmodule
