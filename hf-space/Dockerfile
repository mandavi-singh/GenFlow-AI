FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN pip install --no-cache-dir -e . && mkdir -p /data

ENV GENFLOW_DATA_DIR=/data \
    GENFLOW_MODEL=qwen3:1.7b \
    GENFLOW_BASE_URL=http://127.0.0.1:11434 \
    GENFLOW_NUM_PREDICT=300 \
    HOME=/root \
    PYTHONUNBUFFERED=1

RUN printf '#!/bin/sh\nollama serve > /tmp/ollama.log 2>&1 &\nsleep 2\nuntil curl -s http://127.0.0.1:11434 >/dev/null; do sleep 1; done\necho "Pulling qwen3:1.7b ..."\nollama pull qwen3:1.7b\necho "Model ready. Starting GenFlow-AI..."\nexec python -m genflow.cli serve 0.0.0.0 7860\n' > /start.sh \
    && chmod +x /start.sh

EXPOSE 7860
CMD ["/start.sh"]
