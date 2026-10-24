SIM ?= verilator
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES := $(abspath rtl/core/alu.sv)
TOPLEVEL := alu
COCOTB_TEST_MODULES := test_alu
export PYTHONPATH := $(abspath verification/cocotb):$(PYTHONPATH)

.PHONY: test lint
test:
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim SIM=$(SIM) TOPLEVEL_LANG=$(TOPLEVEL_LANG) VERILOG_SOURCES="$(VERILOG_SOURCES)" TOPLEVEL=$(TOPLEVEL) COCOTB_TEST_MODULES=$(COCOTB_TEST_MODULES)

lint:
	verilator --lint-only -Wall -Wno-fatal rtl/core/alu.sv
