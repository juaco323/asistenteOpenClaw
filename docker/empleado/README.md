# Docker Empleado (test)

Despliegue de prueba para el agente empleado en Ubuntu LTS.

## Qué incluye

- `docker-compose.yml`
- `.env.example`
- `install.sh`
- `update.sh`
- `backup.sh`
- `restore.sh`

## Instalación

```bash
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

## URL

- Control UI OpenClaw (gateway): `http://127.0.0.1:<OPENCLAW_HOST_PORT>/` (valor en `docker/empleado/.env`; el ejemplo usa `18790`).
- **Histórico de pruebas LLM (empleado):** `http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/` (por defecto en compose `18795`; configurable en `.env`).

## Archivos importantes

- token y variables: `docker/empleado/.env`
- estado persistente: `~/.openclaw-empleado/`

## Mantenimiento

### Actualizar
```bash
docker/empleado/update.sh
```

### Backup
```bash
docker/empleado/backup.sh
```

### Restore
```bash
docker/empleado/restore.sh docker/empleado/backups/ARCHIVO.tgz
```

## Observación

Esta es una base de test con imagen fijada a `2026.5.7` (requerida por plugins tipo IRC/Matrix/Mattermost ≥ 2026.4.10).
