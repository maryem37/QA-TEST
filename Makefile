ifeq ($(OS),Windows_NT)
  SHELL := cmd.exe
endif

BACKEND ?= file

.PHONY: up down lint cases sync tests run run-all push report all

up:
	docker compose up -d --build
	uv run python scripts/wait_for_app.py

down:
	docker compose down -v

lint:
	uv run ruff check .

cases:
	uv run python -m pipeline.gen_cases
	uv run python -m pipeline.check_cases

sync:
	uv run python -m pipeline.export --backend $(BACKEND)

tests:
	uv run python -m pipeline.gen_tests
	uv run python -m pipeline.check_tests

run:
	uv run pytest tests/api --junitxml=reports/junit.xml

run-all:
	uv run pytest tests/gold tests/api

push:
	uv run python -m pipeline.push_results --backend $(BACKEND)

report:
	uv run python -m pipeline.report

all: up cases sync tests run push report