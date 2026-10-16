# Nordwind support agent API.
#   docker build -t support-agent .
#   docker run -p 8000:8000 --env-file .env support-agent
# API keys are passed at runtime (--env-file / -e) and are never part of the image.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYDANTIC_AI_NO_BANNER=1 \
    SUPPORT_AGENT_ROOT=/app

WORKDIR /app

# The package is installed together with its dependencies (simple, small project; a code change
# rebuilds this layer).
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install ".[mistral,api,tracing]"

COPY data/policies ./data/policies

# Run as an unprivileged user; .cache holds the corpus embeddings.
RUN useradd --create-home --uid 1000 app && mkdir -p /app/.cache && chown app /app/.cache
USER app

# Hosting platforms (e.g. Render) pass the port in $PORT; 8000 otherwise.
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health', timeout=4)"

# exec: uvicorn replaces the shell, so it receives stop signals directly and shuts down cleanly.
CMD ["sh", "-c", "exec uvicorn support_agent.api:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
