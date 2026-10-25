// Simulation integration wrapper for the RV32I integer stored program.
module cpu_system_rv32i (
    input logic clk, rst,
    output logic [31:0] pc, instruction, write_data,
    output logic illegal, halted
);
    logic [31:0] alu_result;
    cpu_system_memory #(.IMEM_FILE("programs/rv32i_integer.hex")) core (
        .clk(clk), .rst(rst), .pc(pc), .instruction(instruction),
        .alu_result(alu_result), .illegal(illegal), .halted(halted)
    );
    assign write_data = core.write_data;
endmodule
