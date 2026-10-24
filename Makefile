SIM ?= verilator
TOPLEVEL_LANG ?= verilog
export PYTHONPATH := $(abspath verification/cocotb):$(PYTHONPATH)

.PHONY: test test-alu test-register-file lint
test: test-alu test-register-file

test-alu:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/alu.sv)" TOPLEVEL=alu COCOTB_TEST_MODULES=test_alu SIM_BUILD=sim_build/alu

test-register-file:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(abspath rtl/core/register_file.sv)" TOPLEVEL=register_file COCOTB_TEST_MODULES=test_register_file SIM_BUILD=sim_build/register_file

lint:
	verilator --lint-only -Wall -Wno-fatal rtl/core/alu.sv
	verilator --lint-only -Wall -Wno-fatal rtl/core/register_file.sv
