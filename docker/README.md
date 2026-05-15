# Docker: stack completo

Admin, empleado y bot de Telegram están en carpetas separadas con su propio `docker-compose.yml` y `.env`.

## Levantar todo (una sola vez configurados los `.env`)

Desde la raíz del repositorio:

```bash
chmod +x docker/stack-up.sh docker/stack-down.sh
./docker/stack-up.sh
```

Eso ejecuta `docker compose up` para `docker/admin`, `docker/empleado` y `docker/telegram` en ese orden.

## Bajar todo

```bash
./docker/stack-down.sh
```

## Workspaces en el repo

Los contenedores **admin** y **empleado** montan `workspace-admin/` y `workspace-empleado/`. Cada stack incluye el **panel de histórico de pruebas LLM** (puertos `LLM_TEST_PANEL_HOST_PORT` en cada `.env`; por defecto en compose suelen ser **18794** admin y **18795** empleado para no chocar con los gateways).

No hace falta copiar el workspace a `~/.openclaw-*/workspace`; el estado (sesiones, etc.) sigue en `OPENCLAW_STATE_DIR` definido en cada `.env`.

## Componentes

| Carpeta | Rol |
|---------|-----|
| `docker/admin` | Gateway OpenClaw administrador |
| `docker/empleado` | Gateway OpenClaw empleado (imagen local con Python opcional) |
| `docker/telegram` | Bot que habla con ambos gateways |

Instalación inicial por pieza: `docker/*/install.sh`. Actualizar: `docker/*/update.sh`.
