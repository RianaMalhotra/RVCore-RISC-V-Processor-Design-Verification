SIM ?= verilator
TOPLEVEL_LANG ?= verilog
export PYTHONPATH := $(abspath verification/cocotb):$(PYTHONPATH)

.PHONY: test test-alu test-register-file test-decoder test-cpu test-system lint
test: test-alu test-register-file test-decoder test-cpu test-system

test-alu:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv)" TOPLEVEL=alu COCOTB_TEST_MODULES=test_alu SIM_BUILD=sim_build/alu

test-register-file:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/register_file.sv)" TOPLEVEL=register_file COCOTB_TEST_MODULES=test_register_file SIM_BUILD=sim_build/register_file

test-decoder:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/instruction_decoder.sv)" TOPLEVEL=instruction_decoder COCOTB_TEST_MODULES=test_instruction_decoder SIM_BUILD=sim_build/decoder

test-cpu:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/cpu_datapath.sv)" TOPLEVEL=cpu_datapath COCOTB_TEST_MODULES=test_cpu_datapath SIM_BUILD=sim_build/cpu

test-system:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv) $(abspath rtl/core/register_file.sv) $(abspath rtl/core/instruction_decoder.sv) $(abspath rtl/core/cpu_datapath.sv) $(abspath rtl/core/instruction_memory.sv) $(abspath rtl/core/cpu_system.sv)" TOPLEVEL=cpu_system COCOTB_TEST_MODULES=test_cpu_system SIM_BUILD=sim_build/system

lint:
	verilator --lint-only -Wall -Wno-fatal rtl/core/alu.sv
	verilator --lint-only -Wall -Wno-fatal rtl/core/register_file.sv
	verilator --lint-only -Wall -Wno-fatal rtl/core/instruction_decoder.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_datapath rtl/core/alu.sv rtl/core/register_file.sv rtl/core/instruction_decoder.sv rtl/core/cpu_datapath.sv
	verilator --lint-only -Wall -Wno-fatal --top-module cpu_system rtl/core/alu.sv rtl/core/register_file.sv rtl/core/instruction_decoder.sv rtl/core/cpu_datapath.sv rtl/core/instruction_memory.sv rtl/core/cpu_system.sv
