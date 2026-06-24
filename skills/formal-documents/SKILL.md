# Skill: Documentos e informes formales (`formal-documents`)

Aplica **presentación profesional** cuando el usuario pida un **informe**, **memorándum**, **acta**, **documento formal** o un archivo **`.docx`**, o use formulaciones como «de manera formal», «documento oficial», «informe ejecutivo», etc.

**Canales:** Control UI (OpenClaw) y **Telegram** (mismo protocolo).

## Cuándo activarla

- Crear o redactar **`.docx`** (informes, actas, memorandos).
- Redactar en el **chat** un informe o síntesis que deba leerse como documento formal (aunque no pida archivo todavía).
- Tras **transcribe-audio** si piden acta o informe formal a partir del audio.

**No sustituye** el flujo de `AGENTS.md` § *Entregables Office* (tiempo estimado, destino, aviso de finalización).

## Respuesta en chat (OpenClaw y Telegram)

Cuando el contenido se entrega **en el mensaje** (sin archivo o además del archivo):

1. **Título principal** en línea propia (en Telegram: texto en mayúsculas o primera línea destacada; en webchat: `## Título del informe`).
2. **Metadatos breves** bajo el título: fecha, destinatario o ámbito si aplica (una línea cada uno).
3. **Secciones numeradas** con encabezados claros (`### 1. Introducción`, `### 2. Hallazgos`, etc.).
4. **Negritas** en conceptos clave, cifras importantes y conclusiones (`**texto**`).
5. **Listas con viñetas** para hallazgos, recomendaciones o pasos.
6. **Cierre formal** (Conclusiones / Recomendaciones) antes de referencias, si hubo investigación web.
7. **Prohibido** muro de texto sin estructura cuando la petición es formal.

Si el usuario pide **solo** el archivo `.docx`, el chat puede limitarse a un resumen breve + ruta + `[[TELEGRAM_FILE:…]]` en Telegram.

## Archivos `.docx` (obligatorio: formato real en Word)

Genera el documento con **`python-docx`** (disponible en el contenedor). **Prohibido** entregar un `.txt` renombrado o Markdown sin formato cuando pidieron Word.

### Estilo por defecto (ajústalo al contenido, mantén criterio formal)

| Elemento | Fuente | Tamaño | Estilo |
|----------|--------|--------|--------|
| Título del documento | Calibri o Arial | 16–18 pt | Negrita, centrado |
| Subtítulo / fecha | Calibri o Arial | 11–12 pt | Normal, centrado o alineado derecha |
| Encabezado de sección (1., 2., …) | Calibri o Arial | 14 pt | Negrita |
| Subsección | Calibri o Arial | 12 pt | Negrita |
| Cuerpo | Calibri o Arial | 11–12 pt | Normal, interlineado 1,15–1,5 |
| Pie de página (opcional) | Calibri o Arial | 9 pt | Gris, número de página si aplica |

### Estructura mínima de un informe

1. **Portada / título** (título + subtítulo opcional + fecha).
2. **Introducción** o **Objetivo**.
3. **Desarrollo** (secciones según el tema).
4. **Conclusiones** y/o **Recomendaciones**.
5. **Referencias** (APA 7 si hubo fuentes web), solo si corresponde.

Usa **negrita** en párrafos para términos clave (`run.bold = True`). Usa estilos de párrafo `Heading 1` / `Heading 2` cuando encajen.

### Ejemplo mínimo (Python)

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
section = doc.sections[0]
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("Informe de actividades")
run.bold = True
run.font.name = "Calibri"
run.font.size = Pt(16)

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
m = meta.add_run("Junio 2026")
m.font.name = "Calibri"
m.font.size = Pt(11)

doc.add_heading("1. Introducción", level=1)
p = doc.add_paragraph()
p.add_run("Resumen ejecutivo: ").bold = True
p.add_run("texto del informe…")

doc.save("/home/joaquin/Documentos/Reportes/informe.docx")
```

(Ajusta la ruta al directorio confirmado por el usuario; en admin puede ser `~/Documentos/Reportes/` o ruta acordada.)

### Entrega por Telegram

Tras guardar el `.docx`, incluye en la respuesta:

`[[TELEGRAM_FILE:/ruta/absoluta/al/informe.docx]]`

## Preferencias

- Entregar **solo `.docx`** para informes formales (no `.md` paralelo) salvo petición explícita en ese turno.
- Si el usuario indica plantilla, tipografía o estilo corporativo, **priorízalo** sobre la tabla por defecto.
- Guardar informes recurrentes en `~/Documentos/Reportes/` (crear con `mkdir -p` si no existe).

## Referencias cruzadas

| Recurso | Ruta |
|---------|------|
| Flujo Office (destino, tiempo) | `AGENTS.md` § *Entregables Office* |
| Herramientas Python | `TOOLS.md` |
| Transcripción → acta | `skills/transcribe-audio/SKILL.md` |
