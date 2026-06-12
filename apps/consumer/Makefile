check:
	@ruff check . --fix

format:
	@ruff format .

run:
	@uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 10000

mypy-check:
	@mypy --config-file=pyproject.toml .

unit-tests:
	@uv run pytest -vvv --cov=src --cov-report=term-missing

all:
	@ruff format . && isort . && mypy --config-file=pyproject.toml . && uv run pytest -vvv --cov=src --cov-report=term-missing