# Shortcuts for the commands of CONTRIBUTING.md, for a POSIX shell with make. Each
# target runs the uv command it names; on Windows run those commands directly.

.PHONY: help sync rebuild test coverage lint format types stub check build docs bench \
	clean clean-all

# Directories whose ignored files are not this project's to delete: the environments
# uv manages and the libphash submodule.
FIND_PRUNE = \( -path ./.git -o -path './.venv*' -o -path ./native \) -prune -o

help:
	@echo "sync       install the dependencies and build the extension (editable)"
	@echo "rebuild    rebuild the extension after a change to the C side or to tools/"
	@echo "test       run the tests"
	@echo "coverage   run the tests under coverage and report"
	@echo "lint       ruff check, ruff format --check, typos"
	@echo "format     ruff format and ruff check --fix"
	@echo "types      mypy and basedpyright"
	@echo "stub       regenerate src/libphash/_native.pyi"
	@echo "check      lint, types, the stub check and the tests, as CI runs them"
	@echo "build      sdist and wheel into dist/"
	@echo "docs       build the documentation site into build/site/"
	@echo "bench      run the benchmarks into benchmarks/results/"
	@echo "clean      delete caches, reports, dist/ and mutmut's mutants/"
	@echo "clean-all  clean, and delete the C build and the built extension"

sync:
	uv sync --all-extras --inexact

rebuild:
	uv sync --all-extras --inexact --reinstall-package python-libphash

test:
	uv run pytest

coverage:
	uv run coverage run -m pytest
	uv run coverage combine
	uv run coverage report

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run typos

format:
	uv run ruff format .
	uv run ruff check --fix .

types:
	uv run mypy
	uv run basedpyright

stub:
	uv run python tools/stub.py

check: lint types
	uv run python tools/stub.py --check
	uv run pytest

build:
	uv build

docs:
	uv run --group docs zensical build --strict

bench:
	uv run python -m benchmarks

# What the tools write and rebuild on their own; the environment keeps working.
clean:
	rm -rf mutants .mypy_cache .ruff_cache .pytest_cache .hypothesis .cache \
		.coverage .coverage.* htmlcov dist build/site tests/output_*.jpeg
	find . $(FIND_PRUNE) -type d -name __pycache__ -prune -exec rm -rf {} +
	find . $(FIND_PRUNE) -type f -name .DS_Store -exec rm -f {} +

# The C build of libphash and the extension built from it are made again by `make
# rebuild`; until then the editable install cannot import libphash.
clean-all: clean
	rm -rf build src/*.egg-info src/libphash/_native.c src/libphash/_native.*.so \
		src/libphash/_native.*.pyd
