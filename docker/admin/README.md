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

## Archivos importantes

- token y variables: `docker/admin/.env`
- estado persistente: `~/.openclaw-admin/`

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

Esta es una base de test con imagen fijada a `2026.4.9`.
