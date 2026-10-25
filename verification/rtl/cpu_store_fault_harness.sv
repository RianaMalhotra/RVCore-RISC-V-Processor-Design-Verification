// Verification-only harness for CPU-level misaligned store atomicity.
module cpu_store_fault_harness (
    input logic clk, rst,
    output logic [31:0] pc, instruction, protected_word,
    output logic halted, illegal, write_enable, mem_fault, mem_store
);
    logic [31:0] alu_result;
    cpu_system_memory #(.IMEM_FILE("programs/misaligned_store.hex")) cpu (
        .clk(clk), .rst(rst), .pc(pc), .instruction(instruction),
        .alu_result(alu_result), .halted(halted), .illegal(illegal)
    );
    assign write_enable = cpu.effective_write;
    assign mem_fault = cpu.mem_fault;
    assign mem_store = cpu.mem_store;
    // Observe the word at byte address 4, including all bytes touched by SW.
    assign protected_word = {cpu.dmem.mem[7], cpu.dmem.mem[6],
                             cpu.dmem.mem[5], cpu.dmem.mem[4]};

    a_fault_no_reg_write: assert property (
        @(posedge clk) disable iff (rst)
        mem_fault |-> !write_enable
    ) else $error("Faulting store enabled register writeback");
    a_halt_stable_pc: assert property (
        @(posedge clk) disable iff (rst)
        halted |=> $stable(pc)
    ) else $error("PC changed after fault halt");
    a_halt_no_write: assert property (
        @(posedge clk) disable iff (rst)
        halted |-> !write_enable
    ) else $error("Register writeback while halted");
    // When a store is rejected, its targeted aligned word must remain unchanged.
    a_faulting_store_atomic: assert property (
        @(posedge clk) disable iff (rst)
        (mem_store && mem_fault && !halted) |=> $stable(protected_word)
    ) else $error("Faulting store modified protected memory");
endmodule
