FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 1. Copiar manifiestos e instalar dependencias (capa cacheada)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# 2. Copiar código fuente, migraciones y configuración
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

# 3. Sincronizar el paquete raíz
RUN uv sync --frozen --no-dev

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn patients.main:app --host 0.0.0.0 --port 8000"]