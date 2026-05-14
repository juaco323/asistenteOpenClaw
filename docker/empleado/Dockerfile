ARG OPENCLAW_BASE_IMAGE=ghcr.io/openclaw/openclaw:2026.5.7
FROM ${OPENCLAW_BASE_IMAGE}

USER root
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip \
    python3-venv \
  && pip3 install --break-system-packages --no-cache-dir \
    python-pptx \
    requests \
    Pillow \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER node
