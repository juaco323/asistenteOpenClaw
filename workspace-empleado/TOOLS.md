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
