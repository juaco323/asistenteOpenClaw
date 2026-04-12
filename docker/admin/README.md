# Docker Admin (test)

Despliegue de prueba para el agente administrador en Ubuntu LTS.

## Qué incluye

- `docker-compose.yml`
- `.env.example`
- `install.sh`
- `update.sh`

## Persistencia

Este stack guarda el estado en:

- `~/.openclaw-admin/`
- `~/.openclaw-admin/workspace/`

Ahí quedarán configuración, sesiones, memoria y archivos del workspace mientras el volumen del host se mantenga.

## Instalación rápida

Desde el repositorio clonado:

```bash
chmod +x docker/admin/install.sh docker/admin/update.sh
docker/admin/install.sh
```

Luego abre:

- `http://127.0.0.1:18789/`

El token queda guardado en:

- `docker/admin/.env`

## Actualización

```bash
docker/admin/update.sh
```

## Notas

- Esta versión es de **testeo**.
- El stack usa una imagen pública de OpenClaw por defecto.
- Si quieres una versión más cerrada o más estable, en la siguiente fase podemos fijar versión, endurecer seguridad y agregar backup.
