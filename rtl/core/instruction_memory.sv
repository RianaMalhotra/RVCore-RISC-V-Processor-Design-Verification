// Read-only 32-bit instruction memory, 64 words, initialized from a hex file.
// PC is a byte address; word alignment and range are checked by the wrapper.
// Out-of-range or unaligned reads return an illegal instruction (all zeros).
module instruction_memory #(
    parameter int DEPTH = 64,
    parameter INIT_FILE = "programs/arithmetic.hex"
) (
    input  logic [31:0] address,
    output logic [31:0] instruction
);
    logic [31:0] memory [0:DEPTH-1];
    initial begin
        for (int i = 0; i < DEPTH; i++)
            memory[i] = 32'h00000000;
        $readmemh(INIT_FILE, memory);
    end
    always_comb begin
        instruction = 32'h00000000;
        if (address[1:0] == 2'b00 && (address >> 2) < DEPTH)
            instruction = memory[address >> 2];
    end
endmodule
