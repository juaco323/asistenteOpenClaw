# Docker Telegram

Despliegue del bot de Telegram que conversa con las instancias `admin` y `empleado` de OpenClaw.

## Archivos importantes

- variables: `docker/telegram/.env`
- ejemplo final de oficina: `docker/telegram/.env.pc-oficina.example`
- compose: `docker/telegram/docker-compose.yml`
- codigo del bot: `integrations/telegram-bot`

## Instalacion

```bash
chmod +x docker/telegram/*.sh
docker/telegram/install.sh
```
