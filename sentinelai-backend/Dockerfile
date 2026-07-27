FROM python:3.12-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

FROM base AS development
COPY . .
RUN poetry install --no-interaction --no-ansi
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]

FROM base AS production
COPY . .
RUN pip install --no-cache-dir gunicorn
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser --ingroup appgroup && \
    chown -R appuser:appgroup /app
USER appuser
CMD ["gunicorn", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--keep-alive", "5", "--max-requests", "10000", "--max-requests-jitter", "500"]
