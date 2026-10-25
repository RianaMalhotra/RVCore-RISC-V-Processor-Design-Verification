// Expose existing CPU architectural signals without modifying execution behavior.
module cpu_system_load_store_trace (
    input logic clk, rst,
    output logic [31:0] pc, instruction, write_data, alu_result,
    output logic [31:0] rs1_value, rs2_value, memory_address, memory_read, memory_write_data,
    output logic [4:0] rd_index,
    output logic register_write, memory_load, memory_store, memory_fault,
    output logic illegal, halted
);
    cpu_system_memory #(.IMEM_FILE("programs/load_store.hex")) core (
        .clk(clk), .rst(rst), .pc(pc), .instruction(instruction),
        .alu_result(alu_result), .illegal(illegal), .halted(halted)
    );
    assign write_data = core.write_data;
    assign rs1_value = core.rd1;
    assign rs2_value = core.rd2;
    assign rd_index = core.rd;
    assign register_write = core.effective_write;
    assign memory_address = core.mem_address;
    assign memory_read = core.mem_read;
    assign memory_write_data = core.rd2;
    assign memory_load = core.mem_load;
    assign memory_store = core.mem_store;
    assign memory_fault = core.mem_fault;
endmodule
