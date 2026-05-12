# Telegram Bot

Bot de Telegram integrado al repo `asistenteOpenClaw`.

Se conecta a las dos instancias locales de OpenClaw:

- `admin` por `18789`
- `empleado` por `18790`

Usa `long polling` y el gateway real de OpenClaw mediante `POST /v1/chat/completions`.
