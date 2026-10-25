SIM ?= verilator
TOPLEVEL_LANG ?= verilog
export PYTHONPATH := $(abspath verification/cocotb):$(PYTHONPATH)

.PHONY: test-bist-faults test-bist test-scan-stuck-at test-scan-chain test-cpu-random-stream test-cpu-jalr test-cpu-store-fault test-cpu-branch-fault test-cpu-fault-assertions test-data-memory-fault-invariants test-cpu-control-scoreboard test-cpu-arch-scoreboard test-rv32i-differential trace test test-rv32i-system test-rv32i-integer test-alu test-register-file test-decoder test-cpu test-system test-control-flow test-control-system test-data-memory test-memory-system lint
test: test-bist-faults test-bist test-scan-stuck-at test-scan-chain test-cpu-random-stream test-cpu-jalr test-cpu-store-fault test-cpu-branch-fault test-cpu-fault-assertions test-data-memory-fault-invariants test-cpu-control-scoreboard test-cpu-arch-scoreboard test-rv32i-differential test-rv32i-system test-rv32i-integer test-alu test-register-file test-decoder test-cpu test-system test-control-flow test-control-system test-data-memory test-memory-system

trace:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath rtl/core/cpu_system_rv32i.sv)" TOPLEVEL=cpu_system_rv32i COCOTB_TEST_MODULES=test_trace_export MODULE=test_trace_export TRACE_OUTPUT=$(abspath visualizer/public/trace.json) SIM_BUILD=sim_build/rv32i_trace

test-rv32i-differential:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/rv32i_integer.sv)" TOPLEVEL=rv32i_integer COCOTB_TEST_MODULES=test_rv32i_differential MODULE=test_rv32i_differential SIM_BUILD=sim_build/rv32i_differential

test-rv32i-system:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath rtl/core/cpu_system_rv32i.sv)" TOPLEVEL=cpu_system_rv32i COCOTB_TEST_MODULES=test_cpu_system_rv32i MODULE=test_cpu_system_rv32i SIM_BUILD=sim_build/rv32i_system

test-rv32i-integer:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/rv32i_integer.sv)" TOPLEVEL=rv32i_integer COCOTB_TEST_MODULES=test_rv32i_integer MODULE=test_rv32i_integer SIM_BUILD=sim_build/rv32i_integer

test-alu:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv)" TOPLEVEL=alu COCOTB_TEST_MODULES=test_alu MODULE=test_alu SIM_BUILD=sim_build/alu

test-register-file:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/register_file.sv)" TOPLEVEL=register_file COCOTB_TEST_MODULES=test_register_file MODULE=test_register_file SIM_BUILD=sim_build/register_file

test-decoder:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/instruction_decoder.sv)" TOPLEVEL=instruction_decoder COCOTB_TEST_MODULES=test_instruction_decoder MODULE=test_instruction_decoder SIM_BUILD=sim_build/decoder

test-cpu:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/cpu_datapath.sv)" TOPLEVEL=cpu_datapath COCOTB_TEST_MODULES=test_cpu_datapath MODULE=test_cpu_datapath SIM_BUILD=sim_build/cpu

test-system:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/cpu_datapath.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_system.sv)" TOPLEVEL=cpu_system COCOTB_TEST_MODULES=test_cpu_system MODULE=test_cpu_system SIM_BUILD=sim_build/system

test-control-flow:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/cpu_control_flow.sv)" TOPLEVEL=cpu_control_flow COCOTB_TEST_MODULES=test_cpu_control_flow MODULE=test_cpu_control_flow SIM_BUILD=sim_build/control_flow

test-control-system:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/cpu_system_control.sv)" TOPLEVEL=cpu_system_control COCOTB_TEST_MODULES=test_cpu_system_control MODULE=test_cpu_system_control SIM_BUILD=sim_build/control_system

test-cpu-control-scoreboard:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/cpu_system_control.sv)" TOPLEVEL=cpu_system_control COCOTB_TEST_MODULES=test_cpu_control_scoreboard MODULE=test_cpu_control_scoreboard SIM_BUILD=sim_build/control_scoreboard

test-data-memory:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/data_memory.sv)" TOPLEVEL=data_memory COCOTB_TEST_MODULES=test_data_memory MODULE=test_data_memory SIM_BUILD=sim_build/data_memory

test-data-memory-fault-invariants:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/data_memory.sv)" TOPLEVEL=data_memory COCOTB_TEST_MODULES=test_data_memory_fault_invariants MODULE=test_data_memory_fault_invariants SIM_BUILD=sim_build/data_memory_fault_invariants

test-memory-system:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv)" TOPLEVEL=cpu_system_memory COCOTB_TEST_MODULES=test_cpu_system_memory MODULE=test_cpu_system_memory SIM_BUILD=sim_build/memory_system

test-cpu-arch-scoreboard:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv)" TOPLEVEL=cpu_system_memory COCOTB_TEST_MODULES=test_cpu_arch_scoreboard MODULE=test_cpu_arch_scoreboard SIM_BUILD=sim_build/cpu_arch_scoreboard

test-cpu-fault-assertions:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath verification/rtl/cpu_fault_harness.sv)" TOPLEVEL=cpu_fault_harness COCOTB_TEST_MODULES=test_cpu_fault_assertions MODULE=test_cpu_fault_assertions EXTRA_ARGS=--assert SIM_BUILD=sim_build/cpu_fault_assertions

test-cpu-branch-fault:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath verification/rtl/cpu_branch_fault_harness.sv)" TOPLEVEL=cpu_branch_fault_harness COCOTB_TEST_MODULES=test_cpu_branch_fault MODULE=test_cpu_branch_fault EXTRA_ARGS=--assert SIM_BUILD=sim_build/cpu_branch_fault

test-cpu-store-fault:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath verification/rtl/cpu_store_fault_harness.sv)" TOPLEVEL=cpu_store_fault_harness COCOTB_TEST_MODULES=test_cpu_store_fault MODULE=test_cpu_store_fault EXTRA_ARGS=--assert SIM_BUILD=sim_build/cpu_store_fault

test-cpu-jalr:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath verification/rtl/cpu_jalr_harness.sv)" TOPLEVEL=cpu_jalr_harness COCOTB_TEST_MODULES=test_cpu_jalr_end_to_end MODULE=test_cpu_jalr_end_to_end EXTRA_ARGS=--assert SIM_BUILD=sim_build/cpu_jalr

test-cpu-random-stream:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_control_flow.sv) $(abspath rtl/core/data_memory.sv) $(abspath rtl/core/rv32i_integer.sv) $(abspath rtl/core/cpu_system_memory.sv) $(abspath verification/rtl/cpu_random_stream_harness.sv)" TOPLEVEL=cpu_random_stream_harness COCOTB_TEST_MODULES=test_cpu_random_stream MODULE=test_cpu_random_stream EXTRA_ARGS=--assert SIM_BUILD=sim_build/cpu_random_stream

test-scan-chain:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/dft/scan_chain.sv)" TOPLEVEL=scan_chain COCOTB_TEST_MODULES=test_scan_chain MODULE=test_scan_chain SIM_BUILD=sim_build/scan_chain

test-scan-stuck-at:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/dft/scan_chain.sv) $(abspath rtl/dft/scan_fault_harness.sv)" TOPLEVEL=scan_fault_harness COCOTB_TEST_MODULES=test_scan_stuck_at MODULE=test_scan_stuck_at SIM_BUILD=sim_build/scan_stuck_at

test-bist:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/dft/bist_engine.sv)" TOPLEVEL=bist_engine COCOTB_TEST_MODULES=test_bist_engine MODULE=test_bist_engine SIM_BUILD=sim_build/bist_engine

test-bist-faults:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/dft/bist_fault_engine.sv)" TOPLEVEL=bist_fault_engine COCOTB_TEST_MODULES=test_bist_fault_detection MODULE=test_bist_fault_detection SIM_BUILD=sim_build/bist_faults

lint:
	verilator --lint-only -Wall -Wno-fatal rtl/core/rv32i_integer.sv
	verilator --lint-only -Wall -Wno-fatal rtl/core/alu.sv
	verilator --lint-only -Wall -Wno-fatal rtl/core/register_file.sv
	verilator --lint-only -Wall -Wno-fatal rtl/core/instruction_decoder.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_datapath rtl/core/alu.sv rtl/core/register_file.sv rtl/core/instruction_decoder.sv rtl/core/cpu_datapath.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_system rtl/core/alu.sv rtl/core/register_file.sv rtl/core/instruction_decoder.sv rtl/core/cpu_datapath.sv rtl/core/instruction_memory.sv rtl/core/cpu_system.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_control_flow rtl/core/cpu_control_flow.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_system_control rtl/core/alu.sv rtl/core/register_file.sv rtl/core/instruction_decoder.sv rtl/core/instruction_memory.sv rtl/core/cpu_control_flow.sv rtl/core/cpu_system_control.sv
	verilator --lint-only -Wall -Wno-fatal --top-module data_memory rtl/core/data_memory.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_system_memory rtl/core/alu.sv rtl/core/register_file.sv rtl/core/instruction_decoder.sv rtl/core/instruction_memory.sv rtl/core/cpu_control_flow.sv rtl/core/data_memory.sv rtl/core/rv32i_integer.sv rtl/core/cpu_system_memory.sv
