.PHONY: type-check install-types test clean

# Type checking with mypy
type-check:
	@echo "Running mypy type checking..."
	python3 -m mypy data-ingestion/bo3-api/ --config-file pyproject.toml

# Install type stubs
install-types:
	@echo "Installing type stubs..."
	python3 -m pip install -r data-ingestion/requirements.txt
	python3 -m mypy --install-types --non-interactive

# Run all checks
check: type-check
	@echo "All checks passed!"

# Install pre-commit hooks
install-hooks:
	@echo "Installing pre-commit hooks..."
	python3 -m pip install pre-commit
	pre-commit install

