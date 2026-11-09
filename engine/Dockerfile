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

# The container is the isolation boundary for the default subprocess sandbox.
CMD ["uvicorn", "metamorph_engine.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
