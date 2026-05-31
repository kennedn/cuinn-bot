FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

COPY cuinn-bot.py ./

RUN uv sync --frozen --no-dev

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/cuinn-bot.py /app/cuinn-bot.py

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "cuinn-bot.py"]