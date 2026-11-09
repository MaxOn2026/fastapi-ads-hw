FROM python:3.12-slim

# uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) зависимости
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 2) код и сам пакет
COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

# 3) директория под sqlite (root, значит точно доступна на запись)
RUN mkdir -p /app/data

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn fastapi_ads.main:app --host 0.0.0.0 --port 8000"]