.PHONY: install lint typecheck test check run eval

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy

test:
	pytest

check: lint typecheck test

run:
	uvicorn metamorph_engine.api:create_app --factory --host 127.0.0.1 --port 8000

# Usage: make eval CASES=eval/cases OUT=results.csv
eval:
	python eval/run_eval.py --cases $(or $(CASES),eval/cases) --out $(or $(OUT),results.csv)
