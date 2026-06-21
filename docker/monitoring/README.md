# Monitoreo OpenClaw

Prometheus y Grafana corren en **contenedores Docker independientes**, siguiendo el mismo criterio que `docker/admin`, `docker/empleado` y `docker/telegram`.

| Stack | Ruta | Contenedor principal |
|-------|------|----------------------|
| **Prometheus** | `docker/prometheus/` | `openclaw-prometheus` |
| **Grafana** | `docker/grafana/` | `openclaw-grafana` |

## Instalación rápida (ambos stacks)

```bash
chmod +x docker/monitoring/install.sh docker/prometheus/install.sh docker/grafana/install.sh
docker/monitoring/install.sh
```

O por separado:

```bash
docker/prometheus/install.sh   # primero
docker/grafana/install.sh      # después
```

## Dashboard Grafana

Tras iniciar sesión en http://127.0.0.1:3000, abre la carpeta **OpenClaw** → **OpenClaw — Monitoreo completo**.

Cubre todos los criterios de la HU de monitoreo:

- CPU y RAM del host Ubuntu (inactividad y bajo carga)
- CPU y RAM de contenedores OpenClaw/Telegram
- Latencia de respuesta GPT-5.4 (p50, p95, media)
- Consumo de tokens (prompt / completion)
- Peticiones LLM OK vs error

## Documentación

- `docker/prometheus/README.md`
- `docker/grafana/README.md`
- `docs/monitoreo-metricas-rendimiento.md`
