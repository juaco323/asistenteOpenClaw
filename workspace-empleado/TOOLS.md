# TOOLS.md - Notas locales (empleado)

## Rutas de archivos (Docker → host)

El gateway empleado corre en contenedor. Para crear documentos del usuario en Ubuntu:

| Carpeta | Ruta en herramientas | En el PC del usuario |
|---|---|---|
| Documentos | `/home/joaquin/Documentos` | `~/Documentos` |
| Escritorio | `/home/joaquin/Escritorio` | `~/Escritorio` |
| Descargas | `/home/joaquin/Descargas` | `~/Descargas` |
| Imágenes | `/home/joaquin/Imágenes` | `~/Imágenes` |

Estado interno del agente (memoria, sesiones): `/home/node/.openclaw/` — no usar para documentos de oficina.

Usuario Linux del empleado: `joaquin` (uid 1000).

## Python preinstalado en el contenedor empleado

Para tareas ofimáticas (DOCX, PPTX, imágenes, descargas HTTP) ya están disponibles:

- `python3` / `pip3`
- `python-docx`
- `python-pptx`
- `requests`
- `Pillow`

No hace falta pedir autorización para instalar estos paquetes base; si falta otra librería específica, aplicar el protocolo de `SOUL.md` § *Dependencias y librerías del entorno*.

## Google Drive (`drive`)

- Skill: `skills/drive/` en este workspace.
- Cuenta: `prueba.openclaw.fj@gmail.com` (siempre `-a` en cada comando).
- Permisos: **solo lectura y creación de archivos nuevos**. Prohibido modificar o eliminar.
- Para enviar un archivo de Drive por Telegram: descargar a `/home/joaquin/Documentos/` y usar `[[TELEGRAM_FILE:ruta]]`.
- Para subir archivos recibidos por Telegram: origen en `/home/joaquin/Documentos/telegram-openclaw-incoming/`.

## Transcripción de audio (`transcribe-audio`)

- Skill: `skills/transcribe-audio/` en este workspace.
- Usa la API Whisper de OpenAI vía `curl` (`OPENAI_API_KEY` en `docker/empleado/.env`).
- Audios de Telegram: `~/Documentos/telegram-openclaw-incoming/`.
- Guardar transcripciones/actas en `~/Documentos/Reportes/`.

## Auditoría de código (`code-audit`)

- Skill y plantillas: `skills/code-audit/` en este workspace.
- Guía: `docs/auditoria-codigo.md`.
- Reportes alternativos: `~/Documentos/Reportes/auditoria-codigo/` (crear con `mkdir -p` si no existe).

## Comunicaciones administrativas (`admin-comms`)

- Skill: `skills/admin-comms/`; guía `docs/gestion-comunicaciones.md`.
- Borradores: `~/Documentos/Comunicaciones/borradores/`.
- Estados: `LOGS_COMMS.md` (compartido con admin vía `/app/logs_shared/`).
- Envío correo: confirmación explícita + protocolo `email-gmail`.

## Documentos formales (`formal-documents`)

- Skill: `skills/formal-documents/` (montada desde el monorepo).
- Estructura fija §1–§7 (informe técnico); tercera persona; títulos en negrita; archivos en `~/Documentos/Reportes/` con `python-docx`.
