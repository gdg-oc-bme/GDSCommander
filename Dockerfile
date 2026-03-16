# syntax=docker/dockerfile:1
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install dependencies only (reuse layer when app code changes)
COPY pyproject.toml uv.lock ./
ENV UV_NO_DEV=1
RUN uv sync --locked --no-install-project

# Install project
COPY . .
RUN uv sync --locked

# Runtime: no .env loaded; pass TOKEN (and optional logos) via env
ENV ENV=PROD

RUN adduser --disabled-password --gecos "" app && chown -R app:app /app
USER app

CMD ["uv", "run", "python", "setup.py"]
