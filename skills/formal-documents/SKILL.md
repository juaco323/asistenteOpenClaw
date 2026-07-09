# Skill: Documentos e informes formales (`formal-documents`)

Actúa como **Ingeniero de Software Sénior y Redactor Técnico Experto**. Aplica este estándar **fijo y obligatorio** cuando el usuario pida un **informe**, **informe técnico**, **documento formal**, **`.docx`**, o use «de manera formal», «informe ejecutivo», «redacta un informe», etc.

**Canales:** Control UI (OpenClaw) y **Telegram** (mismo protocolo, sin excepciones).

**No sustituye** `AGENTS.md` § *Entregables Office* (tiempo estimado, destino del archivo, aviso de finalización).

---

## 1. Tono y lenguaje (obligatorio)

- Lenguaje **técnico, formal, objetivo** y en **tercera persona** (p. ej. «se analizó», «se implementó», «se observó»).
- **Prohibido:** adjetivos informales, primera persona del agente («yo creo»), explicaciones vagas.
- Sé **preciso** con métricas, tecnologías, versiones y metodologías.

---

## 2. Formato y estilo (obligatorio)

- **Todos** los títulos y subtítulos en **negrita** sin excepción.
- **Numeración multinivel** clara:
  - `**1. Resumen Ejecutivo**`
  - `**2.1. Objetivos del Informe**`
  - `**4.1.1. Detalle**` (si aplica)
- Listas con viñeta **•** para requisitos, hallazgos o pasos complejos.
- **Bloques de código** cuando muestres scripts, comandos, Docker, Nginx, SQL o configuraciones.
- Si usaste `web` / datos externos: sección **7. Referencias Bibliográficas** en **APA 7** con URL completa por fuente.

---

## 3. Estructura fija del informe (obligatoria)

Adapta el **contenido** al tema solicitado por el usuario; **no omitas** secciones. Si un apartado no aplica, inclúyelo con una frase explícita de no aplicabilidad (p. ej. «No se ejecutaron pruebas de carga en este entregable»).

| # | Sección | Contenido esperado |
|---|---------|-------------------|
| **1** | **Resumen Ejecutivo** | Síntesis breve: problema, solución aplicada, resultado principal. |
| **2** | **Introducción** | Contexto general del proyecto o tema. |
| **2.1** | **Objetivos del Informe** | Objetivo general y objetivos específicos detallados. |
| **2.2** | **Alcance y Limitaciones** | Qué cubre y qué excluye el entregable. |
| **3** | **Marco Conceptual** | Tecnologías base, patrones (microservicios, JWT, Outbox, etc.) o metodologías (Agile/Scrum). |
| **4** | **Desarrollo del Proyecto / Metodología** | Núcleo técnico del informe. |
| **4.1** | **Arquitectura y Componentes** | Diseño lógico, base de datos, red o módulos. |
| **4.2** | **Implementación Técnica** | Código relevante, configuraciones, simulaciones o despliegue. |
| **5** | **Análisis de Resultados y Discusión** | Datos, pruebas ejecutadas, evaluación de rendimiento o hallazgos. |
| **6** | **Conclusiones y Recomendaciones** | |
| **6.1** | **Conclusiones** | Estrictamente basadas en resultados demostrados en §5. |
| **6.2** | **Recomendaciones y Trabajo Futuro** | Escalabilidad, mejoras pendientes, riesgos residuales. |
| **7** | **Referencias Bibliográficas** | Fuentes técnicas oficiales, documentación y bibliografía usada. |

El **tema** del informe es el que indique el usuario en su mensaje (sustituye mentalmente `[INSERTAR TEMA AQUÍ]` por ese tema).

---

## 4. Entrega en chat (Telegram y Control UI)

Cuando el informe se muestre **en el mensaje**:

1. Aplica la **estructura §3** completa con títulos en **negrita** y numeración multinivel.
2. **Prohibido** muro de texto plano, secciones genéricas fuera de la plantilla o omitir apartados 1–7.
3. Si el usuario pide **solo** el `.docx`, el chat puede resumir en 2–3 líneas + ruta + `[[TELEGRAM_FILE:…]]`.

---

## 5. Archivos `.docx` (obligatorio: Word con formato real)

**Genera siempre con el script `skills/formal-documents/build_report.py`** (no escribas `python-docx` a mano turno a turno: ese script aplica de forma **mecánica** la tipografía, la negrita de encabezados y la validación de las 13 claves de la estructura §3, evitando informes con secciones vacías o formato inconsistente entre generaciones). **Prohibido** `.txt` renombrado o Markdown pegado como Word.

### Flujo obligatorio

1. Redacta el contenido de **cada** apartado de la tabla §3 (incluida una frase explícita de no aplicabilidad si un apartado no aplica).
2. Vuelca ese contenido a un JSON temporal con `title` y `sections` (una clave por cada fila de §3: `1`, `2`, `2.1`, `2.2`, `3`, `4`, `4.1`, `4.2`, `5`, `6`, `6.1`, `6.2`, `7`). Cada sección lleva `body` (párrafos separados por línea en blanco; líneas que empiecen con `• ` se convierten en viñeta) y, si aplica, `code` (lista de bloques monoespaciados) o, solo en `7`, `references` (lista de referencias APA 7).
3. Ejecuta:
   ```bash
   python3 skills/formal-documents/build_report.py --input /tmp/informe.json --output ~/Documentos/Reportes/<nombre>.docx
   ```
4. Si el script falla, **lee el error**: indica exactamente qué sección falta o quedó vacía. Corrige el JSON y vuelve a ejecutar — **no** generes el `.docx` por otra vía para saltarte la validación.

### Tipografía en Word (aplicada automáticamente por `build_report.py`)

| Elemento | Fuente | Tamaño | Estilo |
|----------|--------|--------|--------|
| Título del documento | Calibri | 17 pt | Negrita, centrado |
| Encabezados §1–§7 y subsecciones | Calibri | 12–14 pt | **Negrita** (aplicada por el script) |
| Cuerpo | Calibri | 11 pt | Normal, interlineado 1,15 |
| Código / comandos | Consolas | 10 pt | Bloque monoespaciado |

### Ruta por defecto

`~/Documentos/Reportes/` (crear con `mkdir -p` si no existe). Respeta el directorio confirmado en § *Entregables Office*.

### Telegram

Tras guardar:

`[[TELEGRAM_FILE:/ruta/absoluta/al/informe.docx]]`

---

## 6. Preferencias del proyecto

- Informes formales: entregar **solo `.docx`** (sin `.md` paralelo) salvo petición explícita en ese turno.
- Si el usuario da plantilla corporativa distinta, **priorízala** solo si no contradice la estructura §3; en caso de conflicto, **prevalece esta skill**.

---

## Referencias cruzadas

| Recurso | Ruta |
|---------|------|
| Generador estable del `.docx` | `skills/formal-documents/build_report.py` |
| Flujo Office (destino, tiempo) | `AGENTS.md` § *Entregables Office* |
| Herramientas Python | `TOOLS.md` |
| Transcripción → informe | `skills/transcribe-audio/SKILL.md` |
