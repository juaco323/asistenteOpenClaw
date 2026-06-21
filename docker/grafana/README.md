# Grafana (contenedor dedicado)

Contenedor **Grafana** separado de Prometheus. Se conecta al Prometheus del host vía `host.docker.internal:9090`.

## Instalación

```bash
# Primero Prometheus
docker/prometheus/install.sh

# Luego Grafana
chmod +x docker/grafana/install.sh
cp docker/grafana/.env.example docker/grafana/.env
docker/grafana/install.sh
```

Abre http://127.0.0.1:3000 (usuario/contraseña en `.env`).

## Dashboard provisionado

**OpenClaw — Monitoreo completo** incluye solo métricas de **recursos del sistema** (tokens/latencia LLM se consultan en el Control UI de OpenClaw, apartado «Uso»):

1. **Host Ubuntu** — CPU/RAM actual + series temporales (inactividad vs carga)
2. **Contenedores Docker** — CPU/RAM por contenedor OpenClaw/Telegram

Archivo: `dashboards/openclaw-monitoreo-completo.json`

## Variables

| Variable | Default |
|----------|---------|
| `GRAFANA_HOST_PORT` | 3000 |
| `GRAFANA_ADMIN_USER` | admin |
| `GRAFANA_ADMIN_PASSWORD` | openclaw |
| `PROMETHEUS_URL` | http://host.docker.internal:9090 |
