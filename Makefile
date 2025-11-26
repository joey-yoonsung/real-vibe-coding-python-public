# Root Makefile with distinct exit codes

MEMBERS ?= config logger
FAIL_UNDER ?= 25
COVERAGE_HTML_DIR ?= htmlcov
PYTEST_OPTS ?=
SKIP_TESTS ?= 0

# Exit codes
# 0: Success
# 1: Test failures
# 2: Coverage threshold not met
# 3: No coverage files found

# uv-run aliases
# Note: Each member's pytest is already configured with --cov in their pyproject.toml
PYTEST            := uv run pytest $(PYTEST_OPTS)
COVERAGE_COMBINE  := uv run coverage combine --keep
COVERAGE_REPORT   := uv run coverage report --fail-under=$(FAIL_UNDER)
COVERAGE_HTML     := uv run coverage html -d $(COVERAGE_HTML_DIR)
COVERAGE_XML      := uv run coverage xml -o coverage.xml

# 0) Sync all packages with dev group once (workspace-wide)
#    --frozen: Use workspace uv.lock as-is
sync:
	@echo "===> Syncing all packages with dev group"
	@uv sync --all-packages --group dev --frozen

# 1) Test targets depend on single sync target for parallel-safe execution
define TEST_TEMPLATE
test-$(1): sync
	@echo "===> Testing $(1)"
	@cd $(1) && $(PYTEST) || exit 1
endef

$(foreach m,$(MEMBERS),$(eval $(call TEST_TEMPLATE,$(m))))

.PHONY: sync test-all $(MEMBERS:%=test-%)
test-all: $(MEMBERS:%=test-%)

# 2) Coverage combine/report
.PHONY: coverage-combine
ifeq ($(SKIP_TESTS),1)
coverage-combine:
	@echo "===> Combining coverage (skipping tests)"
else
coverage-combine: test-all
	@echo "===> Combining coverage"
endif
	@echo "===> Collecting coverage files from members"
	@rm -f .coverage .coverage.*
	@for member in $(MEMBERS); do \
		if [ -f $$member/.coverage ]; then \
			cp $$member/.coverage .coverage.$$member; \
			echo "  Found: $$member/.coverage"; \
		fi; \
	done
	@if ! ls .coverage.* >/dev/null 2>&1; then \
		echo "ERROR: No coverage files found; run tests first"; \
		exit 3; \
	fi
	@$(COVERAGE_COMBINE)

.PHONY: coverage-report
coverage-report: coverage-combine
	@$(COVERAGE_HTML)
	@$(COVERAGE_XML)
	@$(COVERAGE_REPORT) || { echo "ERROR: Coverage below threshold ($(FAIL_UNDER)%)"; exit 2; }

# 3) CI entrypoint with explicit error handling
.PHONY: ci
ci:
	@echo "===> Running CI pipeline"
	@$(MAKE) test-all || { echo "FAIL: Tests failed (exit code 1)"; exit 1; }
	@$(MAKE) coverage-combine SKIP_TESTS=1 || { echo "FAIL: Coverage combine failed (exit code 3)"; exit 3; }
	@$(MAKE) coverage-report SKIP_TESTS=1 || { echo "FAIL: Coverage below threshold (exit code 2)"; exit 2; }
	@echo "===> CI done. See $(COVERAGE_HTML_DIR)/ and coverage.xml"

# 4) Convenient target: report only (assumes tests already ran)
.PHONY: report-only
report-only:
	@$(MAKE) coverage-report SKIP_TESTS=1

# 5) New target: test-only (no coverage check)
.PHONY: test-only
test-only: test-all
	@echo "===> Tests completed successfully"

# 6) New target: check with detailed exit codes
.PHONY: check
check:
	@echo "===> Running full check with detailed error reporting"
	@TEST_RESULT=0; \
	$(MAKE) test-all || TEST_RESULT=$$?; \
	if [ $$TEST_RESULT -ne 0 ]; then \
		echo ""; \
		echo "❌ TESTS FAILED (exit code: $$TEST_RESULT)"; \
		echo "   Fix test failures before checking coverage"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "✅ All tests passed"; \
	echo ""; \
	$(MAKE) coverage-combine SKIP_TESTS=1 || exit 3; \
	COV_RESULT=0; \
	$(MAKE) coverage-report SKIP_TESTS=1 || COV_RESULT=$$?; \
	if [ $$COV_RESULT -ne 0 ]; then \
		echo ""; \
		echo "⚠️  COVERAGE BELOW THRESHOLD (exit code: 2)"; \
		echo "   Tests passed but coverage is insufficient (required: $(FAIL_UNDER)%)"; \
		exit 2; \
	fi; \
	echo ""; \
	echo "✅ All checks passed (tests + coverage)"; \
	echo "   See $(COVERAGE_HTML_DIR)/ for detailed coverage report"
