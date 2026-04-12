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

- `http://127.0.0.1:18790/`

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

Esta es una base de test con imagen fijada a `2026.4.9`.
