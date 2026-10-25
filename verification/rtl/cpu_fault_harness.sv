// Verification-only wrapper: exposes commit/fault signals without changing CPU RTL.
module cpu_fault_harness (
    input logic clk,
    input logic rst,
    output logic [31:0] pc,
    output logic [31:0] instruction,
    output logic halted,
    output logic illegal,
    output logic write_enable,
    output logic mem_fault,
    output logic mem_store,
    output logic [31:0] write_data
);
    logic [31:0] alu_result;
    cpu_system_memory #(.IMEM_FILE("programs/cpu_faults.hex")) cpu (
        .clk(clk), .rst(rst), .pc(pc), .instruction(instruction),
        .alu_result(alu_result), .halted(halted), .illegal(illegal)
    );
    assign write_enable = cpu.effective_write;
    assign mem_fault = cpu.mem_fault;
    assign mem_store = cpu.mem_store;
    assign write_data = cpu.write_data;
    // Concurrent SVA properties evaluated at clock edges.
    // Reset is synchronous; disable checks while reset is asserted.
    property p_illegal_blocks_write;
        @(posedge clk) disable iff (rst)
        illegal |-> !write_enable;
    endproperty
    a_illegal_blocks_write: assert property (p_illegal_blocks_write)
        else $error("Illegal instruction enabled architectural writeback");

    property p_halted_blocks_write;
        @(posedge clk) disable iff (rst)
        halted |-> !write_enable;
    endproperty
    a_halted_blocks_write: assert property (p_halted_blocks_write)
        else $error("Halted CPU enabled architectural writeback");

    property p_halted_pc_stable;
        @(posedge clk) disable iff (rst)
        halted |=> $stable(pc);
    endproperty
    a_halted_pc_stable: assert property (p_halted_pc_stable)
        else $error("PC changed after CPU halted");

    property p_fault_blocks_write;
        @(posedge clk) disable iff (rst)
        mem_fault |-> !write_enable;
    endproperty
    a_fault_blocks_write: assert property (p_fault_blocks_write)
        else $error("Faulting memory operation enabled register writeback");

    property p_reset_clears_halt;
        @(posedge clk)
        rst |=> !halted && pc == 32'b0;
    endproperty
    // The implication's next-cycle sample may coincide with a new instruction;
    // the test holds reset long enough to observe reset state.
    a_reset_clears_halt: assert property (p_reset_clears_halt)
        else $error("Reset did not clear halted state and PC");
endmodule
