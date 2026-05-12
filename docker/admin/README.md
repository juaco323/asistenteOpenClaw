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

- `http://127.0.0.1:18789/`
- Si el panel pide token: ejecuta `./docker/admin/open-dashboard.sh` (abre el navegador con `?token=…` leyendo `docker/admin/.env`). Alternativa manual: copia `OPENCLAW_GATEWAY_TOKEN` del `.env` al campo **Token**, o abre `http://127.0.0.1:18789/?token=TU_TOKEN` (solo localhost). Sin token, verás `401` en `/_openclaw/control-ui-config.json`.

## Archivos importantes

- token y variables: `docker/admin/.env`
- estado persistente: `~/.openclaw-admin/`
- **Fuente del workspace en el repo:** `workspace-admin/`. Lo que edites ahí no entra solo al contenedor: hay que copiarlo al directorio montado con `docker/admin/update.sh` (o reinstalar con `install.sh`). Si no, el gateway seguirá leyendo copias antiguas o plantillas genéricas en `~/.openclaw-admin/workspace/`.

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
