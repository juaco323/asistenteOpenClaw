# Monitoreo OpenClaw (Prometheus + Grafana)

Stack opcional para métricas de **CPU/RAM** (host Ubuntu + contenedores Docker) y **latencia/tokens LLM** (GPT-5.4 vía gateway).

## Componentes

| Servicio | Puerto | Función |
|----------|--------|---------|
| **Prometheus** | 9090 | Recolección de series temporales |
| **Grafana** | 3000 | Dashboards (usuario `admin` por defecto) |
| **node-exporter** | — | CPU/RAM del host Ubuntu |
| **cAdvisor** | — | CPU/RAM por contenedor (`openclaw-*`, `telegram-*`) |
| **llm-metrics-exporter** | 9092 | Latencia y tokens desde JSONL + POST en tiempo real |

## Instalación

```bash
chmod +x docker/monitoring/install.sh
cp docker/monitoring/.env.example docker/monitoring/.env
docker/monitoring/install.sh
```

Abre Grafana: `http://127.0.0.1:3000` → dashboard **OpenClaw — Recursos y LLM**.

## Métricas LLM (latencia y tokens)

Fuentes de datos:

1. `workspace-admin/.llm-test-runs.jsonl` y `workspace-empleado/.llm-test-runs.jsonl` (script `logger.py`, comando `/prueba_llm` en Telegram).
2. `integrations/telegram-bot/data/llm-metrics.jsonl` (cada llamada al gateway desde Telegram).

Variables opcionales en `docker/telegram/.env`:

```bash
LLM_METRICS_EXPORTER_URL=http://host.docker.internal:9092/v1/record
```

## Escenarios de prueba

### Inactividad (baseline CPU/RAM)

1. Levanta el stack OpenClaw sin cargar chats.
2. Espera 10–15 min.
3. En Grafana, revisa paneles de CPU/RAM host y contenedores en reposo.

### Ejecución activa

1. Ejecuta varias pruebas LLM:

   ```bash
   docker/admin/llm-test-logger/run.sh "Responde OK."
   docker/empleado/llm-test-logger/run.sh "Resume en tres frases qué es Prometheus."
   ```

2. Desde Telegram: `/prueba_llm` (admin) o varias consultas en `/chat`.
3. Observa picos en CPU contenedores y latencia p95 en Grafana.

## Langfuse / LiteLLM (extensión futura)

Este stack usa **Prometheus + JSONL** integrado al repo. Para trazas detalladas por prompt, puede añadirse **Langfuse** o un proxy **LiteLLM** delante de la API OpenAI; ver `docs/monitoreo-metricas-rendimiento.md`.

## Referencias

- `docs/monitoreo-metricas-rendimiento.md`
- `docs/pruebas-latencia-ejemplos.md`
