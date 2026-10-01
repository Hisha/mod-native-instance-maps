# Single-command entry points for the native instance map toolchain.
#
#   make check              comprehensive developer verification
#   make epf MAP=karazhan   one approved individual package
#   make epf MAP=all        every approved individual package
#   make release            one combined approved release package
#
# Every recipe is a thin wrapper over tools/ and tests/; nothing here holds
# logic that a Python entry point does not.

PYTHON ?= python3
CXX    ?= g++

.PHONY: all reports packages epf release test validate check verify clean help

all: reports packages test

help:
	@echo 'Native instance-map build commands:'
	@echo '  make check              regenerate and comprehensively verify approved content'
	@echo '  make epf MAP=<map>      build one approved individual map EPF'
	@echo '  make epf MAP=all        build all approved individual map EPFs'
	@echo '  make release            build dist/mod-native-instance-maps.epf'
	@echo '  make clean              remove generated dist/*.epf files only'

reports:
	$(PYTHON) tools/report.py
	$(PYTHON) tools/transform.py

packages:
	$(PYTHON) tools/package.py --all-approved

epf:
	@if [ -z "$(MAP)" ]; then \
		echo 'usage: make epf MAP=<approved-map-slug|all>' >&2; \
		exit 2; \
	elif [ "$(MAP)" = all ]; then \
		$(PYTHON) tools/package.py --all-approved; \
	else \
		$(PYTHON) tools/package.py --map "$(MAP)"; \
	fi

release:
	$(PYTHON) tools/package.py --release

test:
	$(PYTHON) tests/run_tests.py

# Compiles a throwaway harness against the mod-content-manager checkout and runs
# every generated EPF through the real pipeline: ContentPackage::Validate,
# StageInto, WorldMapDbcComposer::AppendRequests/Compose/Stage against the
# verified stock DBC baseline, and ContentServerBundle::VerifyParity. Skipped
# when that checkout is absent.
validate:
	$(PYTHON) tests/validate_epfs.py

check: all release validate

# CI gate: regenerate everything in memory and fail if any tracked artifact
# would change. Nothing is written.
verify:
	$(PYTHON) tools/report.py --check
	$(PYTHON) tools/transform.py --check
	$(PYTHON) tools/package.py --check
	$(PYTHON) tests/run_tests.py

clean:
	$(PYTHON) tools/package.py --clean
