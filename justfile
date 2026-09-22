up:
    docker compose up -d --wait db s3
    uv run alembic upgrade head
    uv run uvicorn app.main:app --reload --proxy-headers --forwarded-allow-ips='*'

migrate:
    uv run alembic upgrade head

makemigration message:
    uv run alembic revision --autogenerate -m "{{message}}"
