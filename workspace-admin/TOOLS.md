# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Google Drive (`drive`)

- Skill: `skills/drive/` en este workspace.
- Cuenta: `prueba.openclaw.fj@gmail.com` (siempre `-a` en cada comando).
- Permisos: lectura, creación, modificación y eliminación completa.
- Para enviar un archivo de Drive por Telegram: descargar a `~/Documentos/` y usar `[[TELEGRAM_FILE:ruta]]`.
- Para subir archivos recibidos por Telegram: origen en `~/Documentos/telegram-openclaw-incoming/`.

## Transcripción de audio (`transcribe-audio`)

- Skill: `skills/transcribe-audio/` en este workspace.
- Usa la API Whisper de OpenAI via `curl` (variable `OPENAI_API_KEY` disponible en el contenedor).
- Formatos soportados: `mp3`, `mp4`, `m4a`, `wav`, `webm`, `ogg`, `flac` (máx. 25 MB).
- Archivos recibidos por Telegram: `~/Documentos/telegram-openclaw-incoming/`.
- Idioma por defecto: `es` (español). Omitir si el idioma es desconocido.

## Auditoría de código (`code-audit`)

- Skill y plantillas: `skills/code-audit/` en este workspace.
- Guía: `docs/auditoria-codigo.md`.
- Reportes alternativos: `~/Documentos/Reportes/auditoria-codigo/` (crear con `mkdir -p` si no existe).
- Perfil admin: priorizar seguridad; registrar en `memory/YYYY-MM-DD.md` si afecta despliegue.

## Comunicaciones administrativas (`admin-comms`)

- Skill: `skills/admin-comms/`; guía `docs/gestion-comunicaciones.md`.
- Borradores: `~/Documentos/Comunicaciones/borradores/`.
- Estados: `/app/logs_shared/LOGS_COMMS.md` (repo: `workspace-empleado/LOGS_COMMS.md`).
- Envío correo: confirmación explícita + `email-gmail` + logs compartidos.
- **Calendar + Meet (solo admin):** `skills/admin-comms/calendar-meet.md`; `scripts/gog-calendar-meet-create.sh`; cancelar: `scripts/gog-calendar-meet-cancel.sh`.
