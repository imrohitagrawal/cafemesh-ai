.PHONY: setup dev build serve verify backend frontend demo-smoke
setup:
	UV_CACHE_DIR=.uv-cache uv sync
	npm --prefix frontend install

dev:
	UV_CACHE_DIR=.uv-cache uv run uvicorn cafemesh.main:app --app-dir backend --reload --port 8000 & npm --prefix frontend run dev -- --host 0.0.0.0

build:
	npm --prefix frontend run build

serve:
	UV_CACHE_DIR=.uv-cache uv run uvicorn cafemesh.main:app --app-dir backend --host 0.0.0.0 --port 8000

backend:
	UV_CACHE_DIR=.uv-cache uv run pytest -q

frontend:
	npm --prefix frontend run typecheck && npm --prefix frontend run build

demo-smoke:
	UV_CACHE_DIR=.uv-cache uv run python scripts/judge_demo_smoke.py

verify: backend frontend
