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
endmodule
