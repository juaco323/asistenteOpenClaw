# Prometheus (contenedor dedicado)

Stack **independiente** de Grafana. Levanta:

| Contenedor | Rol |
|------------|-----|
| `openclaw-prometheus` | Servidor Prometheus `:9090` |
| `openclaw-node-exporter` | CPU/RAM del host Ubuntu |
| `openclaw-cadvisor` | CPU/RAM por contenedor Docker (requiere Docker Engine nativo; en Docker Desktop no resuelve nombres de contenedor — ver `docs/monitoreo-metricas-rendimiento.md` § *Limitación conocida*) |
| `openclaw-llm-metrics-exporter` | Latencia y tokens GPT `:9092/metrics` |

## Instalación

```bash
chmod +x docker/prometheus/install.sh
cp docker/prometheus/.env.example docker/prometheus/.env
docker/prometheus/install.sh
```

Grafana se instala por separado: `docker/grafana/install.sh`

## Verificación

- Prometheus targets: http://127.0.0.1:9090/targets (todos UP)
- Métricas LLM: http://127.0.0.1:9092/metrics
