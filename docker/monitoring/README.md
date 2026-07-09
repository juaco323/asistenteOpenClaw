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

**Alcance actual (estrategia definitiva, ver `docs/monitoreo-metricas-rendimiento.md`):**

- CPU y RAM del host Ubuntu (inactividad y bajo carga) — único contenido del dashboard.
- CPU/RAM **por contenedor** requiere Docker Engine nativo (cAdvisor no resuelve nombres de contenedor en Docker Desktop); mientras tanto usa `docker stats`.
- **Tokens, costo y latencia de GPT-5.4 se consultan en el Control UI de OpenClaw** (`:18790`/`:18791`), pestaña **«Uso»** — no en Grafana.

## Documentación

- `docker/prometheus/README.md`
- `docker/grafana/README.md`
- `docs/monitoreo-metricas-rendimiento.md`
