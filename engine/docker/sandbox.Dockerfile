# Image used by the optional Docker sandbox. Build: docker build -f docker/sandbox.Dockerfile -t metamorph-sandbox .
FROM python:3.12-slim

RUN pip install --no-cache-dir pytest==8.3.3 \
    && useradd --create-home --uid 10001 runner

USER runner
WORKDIR /work
