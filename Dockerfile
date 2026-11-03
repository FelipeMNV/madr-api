FROM python:3.14-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn madr_api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]