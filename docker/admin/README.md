# Docker Admin (test)

Despliegue de prueba para el agente administrador en Ubuntu LTS.

## Qué incluye

- `docker-compose.yml`
- `.env.example`
- `install.sh`
- `update.sh`
- `backup.sh`
- `restore.sh`

## Instalación

```bash
chmod +x docker/admin/*.sh
docker/admin/install.sh
```

## URL

- Panel: `http://127.0.0.1:<OPENCLAW_HOST_PORT>/` (por defecto en `.env.example` suele ser `18789`; el valor real está en `docker/admin/.env`).
- Si el panel pide token: ejecuta `./docker/admin/open-dashboard.sh` (abre el navegador con `?token=…` leyendo `docker/admin/.env`). Alternativa manual: copia `OPENCLAW_GATEWAY_TOKEN` del `.env` al campo **Token**, o abre `http://127.0.0.1:<puerto>/?token=TU_TOKEN` (solo localhost). Sin token, verás `401` en `/_openclaw/control-ui-config.json`.

## Archivos importantes

- token y variables: `docker/admin/.env`
- estado persistente: `~/.openclaw-admin/` (sin el árbol `workspace/` como copia: el contenedor monta `workspace-admin/` del repo en `/home/node/.openclaw/workspace`).
- **Workspace en el repo:** `workspace-admin/` es la fuente que ve el gateway (bind mount en `docker-compose.yml`).

## Mantenimiento

### Actualizar
```bash
docker/admin/update.sh
```

### Backup
```bash
docker/admin/backup.sh
```

### Restore
```bash
docker/admin/restore.sh docker/admin/backups/ARCHIVO.tgz
```

## Observación

Esta es una base de test con imagen fijada a `2026.5.7` (requerida por plugins tipo IRC/Matrix/Mattermost ≥ 2026.4.10).
