FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-cache

COPY alembic.ini ./
COPY alembic ./alembic
COPY app/ app/

EXPOSE 8000

CMD uv run --no-sync alembic upgrade head && uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers --forwarded-allow-ips='*'
