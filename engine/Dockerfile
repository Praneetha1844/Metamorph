FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . pytest==8.3.3 \
    && useradd --create-home --uid 10001 app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

# The container is the isolation boundary for the default subprocess sandbox.
CMD ["uvicorn", "metamorph_engine.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
