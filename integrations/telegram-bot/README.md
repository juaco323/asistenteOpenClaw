# Telegram Bot

Bot de Telegram integrado al repo `asistenteOpenClaw`.

Se conecta a las dos instancias locales de OpenClaw:

- `admin` por `18789`
- `empleado` por `18790`

Usa `long polling` y el gateway real de OpenClaw mediante `POST /v1/chat/completions`.

## Funcionalidades

- `/workspace` — selección de perfil con **contraseña** (Admin / Empleado)
- `/chat` — conversación con el agente del perfil autenticado (texto, documentos y fotos para tareas o correo con adjunto)
- `/correo` — mismo flujo que `/chat` con recordatorio del protocolo Gmail
- `/comunicaciones` — recordatorios, seguimientos y confirmaciones (`admin-comms`); en perfil **Administrador** también reuniones Google Meet + Calendar
- `/get` y lenguaje natural — entrega de archivos del equipo (`entrégame el archivo…`, etc.)
- Archivos **entrantes** por Telegram en `/chat`: se guardan en `Documentos/telegram-openclaw-incoming/` bajo `TELEGRAM_HOST_HOME`; el agente puede usar `gog … --attach` con esa ruta
- `/recordatorios` — listar o crear recordatorios
- `/estado` — salud de ambos gateways
- `/salir` — cierra el chat **y la sesión del perfil** (requiere volver a autenticarse)

## Seguridad de sesión

- Contraseña por perfil (configurable en `docker/telegram/.env`)
- El mensaje con la contraseña se **borra automáticamente** del chat
- Límite de intentos fallidos por cambio de perfil (**5** por defecto)
- Bloqueo temporal persistente tras agotar intentos (**15 min** por defecto; `TELEGRAM_AUTH_LOCKOUT_SECONDS`)
- Tras `/salir`, `/chat` exige nuevo `/workspace` + contraseña

## Política de archivos

Manifiesto: `config/workspace-file-policy.yaml`

Por perfil define:

- `read_roots` — lectura y entrega por Telegram
- `write_roots` — creación/modificación
- `deny_roots` — acceso denegado
- `delete_allowed: false` — **ningún perfil puede eliminar archivos** vía asistente

Auditoría de entregas: `data/file-delivery-audit.jsonl`

## Código principal

- `app/bot.py` — handlers Telegram
- `app/telegram_incoming.py` — recepción y guardado de documentos/fotos desde Telegram
- `app/workspace_policy.py` — carga de política YAML
- `app/telegram_context.py` — contexto de canal inyectado al agente
- `app/openclaw/http_client.py` — cliente gateway

## Despliegue

Ver `docker/telegram/README.md` y `docs/conexion-telegram-openclaw.md`.
