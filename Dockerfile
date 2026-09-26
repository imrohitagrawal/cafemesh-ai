FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
ENV UV_CACHE_DIR=/tmp/uv-cache
RUN pip install --no-cache-dir uv==0.12.19 && uv sync --no-dev --no-install-project && uv cache clean
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
ENV CAFEMESH_DATABASE=/tmp/cafemesh.db PYTHONPATH=/app/backend PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uv run --no-sync uvicorn cafemesh.main:app --app-dir backend --host 0.0.0.0 --port ${PORT}"]
