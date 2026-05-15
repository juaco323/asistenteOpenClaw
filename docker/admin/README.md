# Docker Admin (test)

Despliegue de prueba para el agente administrador en Ubuntu LTS.

## Qué incluye

- `docker-compose.yml`
- `.env.example`
- `install.sh`
- `update.sh`
- `backup.sh`
- `restore.sh`

## Instalación (host, sin entrar en `docker/`)

Define la ruta del clon **openClaw** (donde están `README.md` y `workspace-admin/`). Puedes ejecutar todo desde cualquier directorio actual; no hace falta `cd` a `docker/admin` ni abrir la carpeta `docker` en el explorador.

```bash
# Sustituye por la ruta real de tu máquina, por ejemplo: ~/Documentos/openClaw
export OPENCLAW_REPO="$HOME/Documentos/openClaw"

chmod +x "$OPENCLAW_REPO"/docker/admin/*.sh
"$OPENCLAW_REPO"/docker/admin/install.sh
```

Si prefieres usar solo rutas relativas, entonces **sí** debes situarte antes en la raíz del repo: `cd "$OPENCLAW_REPO"` y después `chmod +x docker/admin/*.sh` y `./docker/admin/install.sh`.

## URL

- Control UI OpenClaw (gateway): `http://127.0.0.1:<OPENCLAW_HOST_PORT>/` (valor en `docker/admin/.env`, típico `18789`).
- **Histórico de pruebas LLM (admin):** `http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/` (por defecto en compose `18794`; define `LLM_TEST_PANEL_HOST_PORT` en `docker/admin/.env` para evitar choque con **empleado**, que a menudo usa `18793` en el host). Lee el JSONL `workspace-admin/.llm-test-runs.jsonl` generado por `docker/admin/llm-test-logger/logger.py` (`oc.Tracker`).
- Si el Control UI pide token: ejecuta `./docker/admin/open-dashboard.sh` (abre el navegador con `?token=…` leyendo `docker/admin/.env`). Alternativa manual: copia `OPENCLAW_GATEWAY_TOKEN` del `.env` al campo **Token**, o abre `http://127.0.0.1:<puerto>/?token=TU_TOKEN` (solo localhost). Sin token, verás `401` en `/_openclaw/control-ui-config.json`.

## Pruebas LLM con `oc.Tracker` (solo admin)

1. En `docker/admin/.env` deben estar al menos **`OPENCLAW_GATEWAY_TOKEN`** (mismo token del gateway admin) y **`OPENCLAW_HOST_PORT`** si no usas el puerto por defecto `18789`. El logger usa por defecto `http://127.0.0.1:<OPENCLAW_HOST_PORT>`. Si prefieres, puedes definir `OPENCLAW_ADMIN_BASE_URL` y `OPENCLAW_ADMIN_GATEWAY_TOKEN` en su lugar.
2. Ejecuta el logger con el **venv local** del directorio `llm-test-logger` (recomendado en Ubuntu/Debian con PEP 668; evita `pip install --user` al Python del sistema):

```bash
chmod +x "$OPENCLAW_REPO"/docker/admin/llm-test-logger/run.sh
"$OPENCLAW_REPO"/docker/admin/llm-test-logger/run.sh "Tu prompt de prueba"
# Perfil empleado (usa docker/empleado/.env y workspace-empleado/.llm-test-runs.jsonl):
chmod +x "$OPENCLAW_REPO"/docker/empleado/llm-test-logger/run.sh
"$OPENCLAW_REPO"/docker/empleado/llm-test-logger/run.sh "Tu prompt de prueba"
```

La primera ejecución crea `docker/admin/llm-test-logger/.venv/` e instala `httpx` y `python-dotenv` ahí dentro.

Si `python3 -m venv` falla, instala el paquete de tu versión de Python, por ejemplo: `sudo apt install python3.14-venv`.

El script escribe en `workspace-admin/.llm-test-runs.jsonl`, imprime `Registro completado. Revisa el panel de OpenClaw.` y el panel Docker lee ese mismo archivo (`openclaw-admin-llm-panel`).

## Archivos importantes

- token y variables: `docker/admin/.env`
- estado persistente: `~/.openclaw-admin/` (sin el árbol `workspace/` como copia: el contenedor monta `workspace-admin/` del repo en `/home/node/.openclaw/workspace`).
- **Workspace en el repo:** `workspace-admin/` es la fuente que ve el gateway (bind mount en `docker-compose.yml`).

## Mantenimiento

### Actualizar
```bash
"$OPENCLAW_REPO"/docker/admin/update.sh
```
(o `./docker/admin/update.sh` desde la raíz del clon)

### Backup
```bash
"$OPENCLAW_REPO"/docker/admin/backup.sh
```

### Restore
```bash
"$OPENCLAW_REPO"/docker/admin/restore.sh "$OPENCLAW_REPO"/docker/admin/backups/ARCHIVO.tgz
```

## Observación

Esta es una base de test con imagen fijada a `2026.5.7` (requerida por plugins tipo IRC/Matrix/Mattermost ≥ 2026.4.10).
