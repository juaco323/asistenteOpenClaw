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

Para tareas ofimáticas (PPTX, imágenes, descargas HTTP) ya están disponibles:

- `python3` / `pip3`
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

## Auditoría de código (`code-audit`)

- Skill y plantillas: `skills/code-audit/` en este workspace.
- Guía: `docs/auditoria-codigo.md`.
- Reportes alternativos: `~/Documentos/Reportes/auditoria-codigo/` (crear con `mkdir -p` si no existe).
