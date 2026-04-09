.PHONY: install test lint typecheck demo all clean

PACKAGE := packages/techtide-swarm

install:
	pip install -e "$(PACKAGE)[dev]"

test:
	python -m pytest $(PACKAGE)/tests -v

lint:
	ruff check $(PACKAGE)/src

typecheck:
	cd $(PACKAGE) && mypy src

demo:
	python -m techtide_swarm.cli demo

eval:
	python -m techtide_swarm.cli eval

roster:
	python scripts/generate_roster.py

all: install lint typecheck test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
