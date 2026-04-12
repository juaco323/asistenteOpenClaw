# Docker Empleado (test)

Despliegue de prueba para el agente empleado en Ubuntu LTS.

## Qué incluye

- `docker-compose.yml`
- `.env.example`
- `install.sh`
- `update.sh`

## Persistencia

Este stack guarda el estado en:

- `~/.openclaw-empleado/`
- `~/.openclaw-empleado/workspace/`

Ahí quedarán configuración, sesiones, memoria y archivos del workspace mientras el volumen del host se mantenga.

## Instalación rápida

Desde el repositorio clonado:

```bash
chmod +x docker/empleado/install.sh docker/empleado/update.sh
docker/empleado/install.sh
```

Luego abre:

- `http://127.0.0.1:18790/`

El token queda guardado en:

- `docker/empleado/.env`

## Actualización

```bash
docker/empleado/update.sh
```

## Notas

- Esta versión es de **testeo**.
- El stack usa una imagen pública de OpenClaw por defecto.
- Si quieres una versión más cerrada o más estable, en la siguiente fase podemos fijar versión, endurecer seguridad y agregar backup.
