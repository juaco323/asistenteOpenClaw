# Docker Telegram

Despliegue del bot de Telegram que conversa con las instancias `admin` y `empleado` de OpenClaw.

## Archivos importantes

- variables: `docker/telegram/.env`
- ejemplo de oficina: `docker/telegram/.env.pc-oficina.example`
- compose: `docker/telegram/docker-compose.yml`
- código del bot: `integrations/telegram-bot`
- política de archivos: `integrations/telegram-bot/config/workspace-file-policy.yaml`

## Instalación

```bash
chmod +x docker/telegram/*.sh
cp docker/telegram/.env.pc-oficina.example docker/telegram/.env
# Editar .env: token, user IDs, gateway tokens, contraseñas de perfil
docker/telegram/install.sh
```

## Variables relevantes (.env)

| Variable | Descripción |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token de BotFather |
| `TELEGRAM_ALLOWED_USER_IDS` | IDs autorizados (coma) |
| `OPENCLAW_ADMIN_*` / `OPENCLAW_EMPLEADO_*` | URL y token de cada gateway |
| `TELEGRAM_HOST_HOME` | Home del host montado para leer archivos (p. ej. `/home/joaquin`) |
| `TELEGRAM_ADMIN_PASSWORD` | Contraseña perfil Admin (default `Admin1234*`) |
| `TELEGRAM_EMPLEADO_PASSWORD` | Contraseña perfil Empleado (default `Empleado1234*`) |
| `OPENCLAW_REQUEST_TIMEOUT_SECONDS` | Timeout HTTP al gateway (recomendado `600`) |

Opcional: `TELEGRAM_*_READ_ROOTS`, `TELEGRAM_*_WRITE_ROOTS`, `TELEGRAM_*_DENY_ROOTS` sobrescriben el YAML.

## Comandos del bot

- `/workspace` — elegir perfil (pide contraseña)
- `/chat` — hablar con OpenClaw (requiere perfil autenticado)
- `/get` o lenguaje natural — recibir archivos como adjunto
- `/salir` — cierra chat y sesión de perfil
- `/estado`, `/recordatorios`, `/start`, `/help`

## Actualización

```bash
docker/telegram/update.sh
```

## Volúmenes

- `integrations/telegram-bot/data` — datos locales y auditoría
- `${TELEGRAM_HOST_HOME}` montado en solo lectura para entrega de archivos del host
