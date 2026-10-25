// Byte-addressed, little-endian data memory with RV32I load/store semantics.
// Unaligned and out-of-range accesses are rejected; writes commit on clock edge.
module data_memory #(
    parameter int BYTES = 256
) (
    input logic clk, rst,
    input logic read_en, write_en,
    input logic [2:0] funct3,
    input logic [31:0] address, write_data,
    output logic [31:0] read_data,
    output logic fault
);
    logic [7:0] mem [0:BYTES-1];
    logic [2:0] size_bytes;
    logic valid_kind;
    always_comb begin
        size_bytes = 3'd1;
        valid_kind = 1'b1;
        if (write_en) begin
            case (funct3)
                3'b000: size_bytes = 3'd1; // SB
                3'b001: size_bytes = 3'd2; // SH
                3'b010: size_bytes = 3'd4; // SW
                default: valid_kind = 1'b0;
            endcase
        end else begin
            case (funct3)
                3'b000, 3'b100: size_bytes = 3'd1; // LB/LBU
                3'b001, 3'b101: size_bytes = 3'd2; // LH/LHU
                3'b010: size_bytes = 3'd4; // LW
                default: valid_kind = 1'b0;
            endcase
        end
        fault = 1'b0;
        if (read_en || write_en)
            fault = !valid_kind ||
                ((size_bytes == 3'd2) && address[0]) ||
                ((size_bytes == 3'd4) && (address[1:0] != 2'b00)) ||
                (address >= BYTES) || (address > (BYTES - int'(size_bytes)));
        read_data = 32'b0;
        if (read_en && !fault) begin
            case (size_bytes)
                3'd1: begin
                    if (funct3 == 3'b000)
                        read_data = {{24{mem[address][7]}}, mem[address]};
                    else
                        read_data = {24'b0, mem[address]};
                end
                3'd2: begin
                    if (funct3 == 3'b001)
                        read_data = {{16{mem[address+1][7]}}, mem[address+1], mem[address]};
                    else
                        read_data = {16'b0, mem[address+1], mem[address]};
                end
                3'd4: read_data = {mem[address+3],mem[address+2],mem[address+1],mem[address]};
                default: ;
            endcase
        end
    end
    always_ff @(posedge clk) begin
        if (rst) begin
            for (int i = 0; i < BYTES; i++) mem[i] = 8'b0;
        end else if (write_en && !fault) begin
            mem[address] <= write_data[7:0];
            if (size_bytes >= 2) mem[address+1] <= write_data[15:8];
            if (size_bytes == 4) begin
                mem[address+2] <= write_data[23:16];
                mem[address+3] <= write_data[31:24];
            end
        end
    end
endmodule
