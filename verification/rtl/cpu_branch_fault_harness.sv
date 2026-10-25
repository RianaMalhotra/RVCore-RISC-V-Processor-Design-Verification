// Verification-only instance of the memory CPU with a misaligned branch program.
module cpu_branch_fault_harness (
    input logic clk, rst,
    output logic [31:0] pc, instruction, write_data,
    output logic halted, illegal, write_enable, branch_taken,
    output logic [31:0] next_pc
);
    logic [31:0] alu_result;
    cpu_system_memory #(.IMEM_FILE("programs/misaligned_branch.hex")) cpu (
        .clk(clk), .rst(rst), .pc(pc), .instruction(instruction),
        .alu_result(alu_result), .halted(halted), .illegal(illegal)
    );
    assign write_data = cpu.write_data;
    assign write_enable = cpu.effective_write;
    assign branch_taken = cpu.control_flow && cpu.taken;
    assign next_pc = cpu.next_pc;
    // A misaligned taken control-flow target must never write a register.
    a_misaligned_target_no_write: assert property (
        @(posedge clk) disable iff (rst)
        (branch_taken && next_pc[1:0] != 2'b00) |-> !write_enable
    ) else $error("Misaligned branch committed a register write");
    // Once halted, the PC must remain stable and writeback must stay disabled.
    a_halted_stable: assert property (
        @(posedge clk) disable iff (rst)
        halted |=> $stable(pc)
    ) else $error("PC changed after halt");
    a_halted_no_write: assert property (
        @(posedge clk) disable iff (rst)
        halted |-> !write_enable
    ) else $error("Halted CPU wrote a register");
endmodule
