.PHONY: help build-bootstrap compile check-bootstrap smoke smoke-check stale-report release-check clean

TMP_DIR ?= /tmp/ai-docs-smoke

help:
	@echo "Available targets:"
	@echo "  make build-bootstrap  - Regenerate bootstrap (Auto OS profile)"
	@echo "  make compile          - Compile-check setup and bootstrap scripts"
	@echo "  make check-bootstrap  - Run bootstrap freshness check against TMP_DIR"
	@echo "  make smoke            - Generate docs in TMP_DIR (existing mode)"
	@echo "  make smoke-check      - Run smoke + freshness check"
	@echo "  make stale-report     - Produce stale report in TMP_DIR"
	@echo "  make release-check    - Full pre-release validation flow"
	@echo "  make clean            - Remove local temporary artifacts"
	@echo ""
	@echo "Override temp dir: make smoke TMP_DIR=/tmp/my-ai-docs"

build-bootstrap:
	printf "4\n" | python3 setup-ai-docs.py

compile:
	python3 -m py_compile setup-ai-docs.py
	python3 -m py_compile ai-docs-bootstrap

smoke:
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing

check-bootstrap:
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check

smoke-check: smoke check-bootstrap

stale-report:
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check --report-path .ai-docs-check-report.md || true
	@echo "If stale, report is at: $(TMP_DIR)/.ai-docs-check-report.md"

release-check:
	python3 -m py_compile setup-ai-docs.py
	printf "4\n" | python3 setup-ai-docs.py
	python3 -m py_compile ai-docs-bootstrap
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check --report-path .ai-docs-check-report.md || true
	@echo "Release checks completed."

clean:
	rm -rf __pycache__
