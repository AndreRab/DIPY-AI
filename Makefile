.DEFAULT_GOAL := dev

.PHONY: setup dev

setup:
	uv sync
	npm --prefix frontend ci

dev:
	uv run python scripts/dev.py
