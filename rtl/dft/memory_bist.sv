// Educational March-style memory BIST: W0 up, R0/W1 up, R1/W0 down, R0 down.
// Fault model forces a selected bit of one memory word on writes and reads.
// This is a standalone test memory, not the RV32I CPU data memory.
module memory_bist #(
    parameter int DEPTH = 8,
    parameter int WIDTH = 8,
    parameter int ADDR_W = $clog2(DEPTH)
)(
    input logic clk, rst, start,
    input logic fault_enable, fault_value,
    input logic [ADDR_W-1:0] fault_address,
    input logic [$clog2(WIDTH)-1:0] fault_bit,
    output logic busy, done, pass,
    output logic [15:0] comparisons,
    output logic [15:0] errors
);
    typedef enum logic [2:0] {IDLE, W0, R0W1, R1W0, R0, FINISH} phase_t;
    phase_t phase;
    logic [ADDR_W-1:0] address;
    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [WIDTH-1:0] observed;
    integer i;
    always_comb begin
        observed = mem[address];
        if (fault_enable && address == fault_address)
            observed[fault_bit] = fault_value;
    end
    always_ff @(posedge clk) begin
        if (rst) begin
            phase <= IDLE;
            address <= '0;
            busy <= 1'b0;
            done <= 1'b0;
            pass <= 1'b0;
            comparisons <= '0;
            errors <= '0;
            for (i = 0; i < DEPTH; i = i + 1) mem[i] <= '0;
        end else begin
            case (phase)
                IDLE: if (start) begin
                    phase <= W0;
                    address <= '0;
                    busy <= 1'b1;
                    done <= 1'b0;
                    pass <= 1'b0;
                    comparisons <= '0;
                    errors <= '0;
                end
                W0: begin
                    mem[address] <= '0;
                    if (address == ADDR_W'(DEPTH - 1)) begin
                        address <= '0;
                        phase <= R0W1;
                    end else address <= address + 1'b1;
                end
                R0W1: begin
                    comparisons <= comparisons + 1'b1;
                    if (observed != '0) errors <= errors + 1'b1;
                    mem[address] <= '1;
                    if (address == ADDR_W'(DEPTH - 1)) begin
                        phase <= R1W0;
                    end else address <= address + 1'b1;
                end
                R1W0: begin
                    comparisons <= comparisons + 1'b1;
                    if (observed != {WIDTH{1'b1}}) errors <= errors + 1'b1;
                    mem[address] <= '0;
                    if (address == 0) begin
                        phase <= R0;
                        address <= '0;
                    end else address <= address - 1'b1;
                end
                R0: begin
                    comparisons <= comparisons + 1'b1;
                    if (observed != '0) errors <= errors + 1'b1;
                    if (address == ADDR_W'(DEPTH - 1)) phase <= FINISH;
                    else address <= address + 1'b1;
                end
                FINISH: begin
                    busy <= 1'b0;
                    done <= 1'b1;
                    pass <= (errors == 0);
                    phase <= IDLE;
                end
                default: phase <= IDLE;
            endcase
        end
    end
endmodule
