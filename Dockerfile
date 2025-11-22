# syntax=docker/dockerfile:1.7-labs

ARG PYTHON_BASE=python:3.12.7-slim

##############################
# Builder stage
##############################
FROM ${PYTHON_BASE} AS build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip wheel --wheel-dir=/tmp/wheels -r requirements.txt

COPY app ./app

##############################
# Runtime stage
##############################
FROM ${PYTHON_BASE} AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --create-home --gid app app \
    && mkdir -p /data \
    && chown -R app:app /app /data

COPY --from=build /tmp/wheels /tmp/wheels
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --find-links=/tmp/wheels --requirement requirements.txt \
    && rm -rf /tmp/wheels

COPY --from=build --chown=app:app /app/app ./app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

USER app

ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]
