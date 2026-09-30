# Single-command entry points for the native instance map toolchain.
#
#   make            reports + packages + tests
#   make check      everything, including the mod-content-manager harness
#   make verify     assert the generated artifacts are up to date (CI gate)
#
# Every recipe is a thin wrapper over tools/ and tests/; nothing here holds
# logic that a Python entry point does not.

PYTHON ?= python3
CXX    ?= g++

.PHONY: all reports packages epf test validate check verify clean help

all: reports packages test

help:
	@sed -n '1,8p' $(MAKEFILE_LIST)

reports:
	$(PYTHON) tools/report.py
	$(PYTHON) tools/transform.py

packages:
	$(PYTHON) tools/package.py

epf: packages

test:
	$(PYTHON) tests/run_tests.py

# Compiles a throwaway harness against the mod-content-manager checkout and runs
# every generated EPF through the real pipeline: ContentPackage::Validate,
# StageInto, WorldMapDbcComposer::AppendRequests/Compose/Stage against the
# verified stock DBC baseline, and ContentServerBundle::VerifyParity. Skipped
# when that checkout is absent.
validate:
	$(PYTHON) tests/validate_epfs.py

check: all validate

# CI gate: regenerate everything in memory and fail if any tracked artifact
# would change. Nothing is written.
verify:
	$(PYTHON) tools/report.py --check
	$(PYTHON) tools/transform.py --check
	$(PYTHON) tools/package.py --check
	$(PYTHON) tests/run_tests.py

clean:
	rm -rf dist/*.epf
	find . -name '__pycache__' -type d -not -path './upstream/*' -exec rm -rf {} +
