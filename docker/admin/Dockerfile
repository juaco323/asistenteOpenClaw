ARG OPENCLAW_BASE_IMAGE=ghcr.io/openclaw/openclaw:2026.5.7
FROM ${OPENCLAW_BASE_IMAGE}

USER root

ARG TARGETARCH=amd64
ARG GOGCLI_VERSION=0.16.0

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    python3-pip \
    python3-venv \
  && curl -fsSL "https://github.com/openclaw/gogcli/releases/download/v${GOGCLI_VERSION}/gogcli_${GOGCLI_VERSION}_linux_${TARGETARCH}.tar.gz" \
    | tar -xzf - -C /usr/local/bin gog \
  && chmod +x /usr/local/bin/gog \
  && pip3 install --break-system-packages --no-cache-dir \
    python-pptx \
    python-docx \
    requests \
    Pillow \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /home/node/.config \
  && chown -R node:node /home/node/.config

COPY docker/common/gog-policy-check.sh docker/admin/gog-wrapper.sh docker/admin/gog-gmail-draft-wrap.py docker/admin/entrypoint-gateway.sh /tmp/oc-bin/
COPY scripts/gog-calendar-meet-cancel.sh /tmp/oc-bin/gog-calendar-meet-cancel.sh
COPY scripts/zoom-api-common.sh scripts/zoom-meeting-create.sh scripts/zoom-meeting-cancel.sh /tmp/oc-bin/
RUN set -eu \
  && mv /usr/local/bin/gog /usr/local/bin/gog.real \
  && install -m 0755 /tmp/oc-bin/gog-policy-check.sh /usr/local/bin/gog-policy-check.sh \
  && install -m 0755 /tmp/oc-bin/gog-wrapper.sh /usr/local/bin/gog \
  && install -m 0755 /tmp/oc-bin/gog-gmail-draft-wrap.py /usr/local/bin/gog-gmail-draft-wrap.py \
  && install -m 0755 /tmp/oc-bin/entrypoint-gateway.sh /usr/local/bin/entrypoint-gateway.sh \
  && install -m 0755 /tmp/oc-bin/gog-calendar-meet-cancel.sh /usr/local/bin/gog-calendar-meet-cancel.sh \
  && install -m 0755 /tmp/oc-bin/zoom-api-common.sh /usr/local/bin/zoom-api-common.sh \
  && install -m 0755 /tmp/oc-bin/zoom-meeting-create.sh /usr/local/bin/zoom-meeting-create.sh \
  && install -m 0755 /tmp/oc-bin/zoom-meeting-cancel.sh /usr/local/bin/zoom-meeting-cancel.sh \
  && rm -rf /tmp/oc-bin

USER node
ENTRYPOINT ["/usr/local/bin/entrypoint-gateway.sh"]
