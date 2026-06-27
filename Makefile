.PHONY: help build-bootstrap compile test check-bootstrap smoke smoke-check stale-report ci-freshness release-check doctor demo-intent clean

TMP_DIR ?= /tmp/ai-docs-smoke
INTENT ?= ride booking ecommerce payments
COMPLIANCE ?= soc2,gdpr

help:
	@echo "Available targets:"
	@echo "  make build-bootstrap  - Regenerate bootstrap (Auto OS profile)"
	@echo "  make compile          - Compile-check setup and bootstrap scripts"
	@echo "  make test             - Run Python unit tests"
	@echo "  make check-bootstrap  - Run bootstrap freshness check against TMP_DIR"
	@echo "  make smoke            - Generate docs in TMP_DIR (existing mode)"
	@echo "  make smoke-check      - Run smoke + freshness check"
	@echo "  make stale-report     - Produce stale report in TMP_DIR"
	@echo "  make ci-freshness     - Validate bootstrap freshness for release"
	@echo "  make release-check    - Full pre-release validation flow"
	@echo "  make doctor           - Quick health check (build + compile + smoke-check)"
	@echo "  make demo-intent      - Non-interactive demo using INTENT/COMPLIANCE vars"
	@echo "  make clean            - Remove local temporary artifacts"
	@echo ""
	@echo "Override temp dir: make smoke TMP_DIR=/tmp/my-ai-docs"
	@echo "Override demo intent: make demo-intent INTENT='health payments saas' COMPLIANCE='soc2,hipaa'"

build-bootstrap:
	printf "4\n" | python3 setup-ai-docs.py

compile:
	python3 -m py_compile setup-ai-docs.py
	python3 -m py_compile ai-docs-bootstrap

test:
	python3 -m unittest discover -s tests -p 'test_*.py' -v

smoke:
	rm -rf "$(TMP_DIR)"
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing

check-bootstrap:
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check

smoke-check: smoke check-bootstrap

stale-report:
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check --report-path .ai-docs-check-report.md || true
	@echo "If stale, report is at: $(TMP_DIR)/.ai-docs-check-report.md"

ci-freshness: smoke-check
	@echo "✓ Bootstrap freshness validated for release"

release-check:
	python3 -m py_compile setup-ai-docs.py
	printf "4\n" | python3 setup-ai-docs.py
	python3 -m py_compile ai-docs-bootstrap
	rm -rf "$(TMP_DIR)"
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode existing --check --report-path .ai-docs-check-report.md || true
	@echo "Release checks completed."

doctor: build-bootstrap compile smoke-check
	@echo "✓ Doctor check completed successfully."

demo-intent: build-bootstrap
	mkdir -p "$(TMP_DIR)"
	./ai-docs-bootstrap --project "$(TMP_DIR)" --mode new --non-interactive --intent "$(INTENT)" --compliance "$(COMPLIANCE)"
	@echo "Demo generated in: $(TMP_DIR)"

clean:
	rm -rf __pycache__
