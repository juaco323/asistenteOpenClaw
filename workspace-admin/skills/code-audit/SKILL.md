# Skill: Auditoría de código (workspace administrador)

Analiza archivos de código completos (cualquier lenguaje), identifica deuda técnica, sugiere optimizaciones de rendimiento, entrega código refactorizado con justificación técnica y genera documentación en Markdown.

**Workspace:** `workspace-admin` — rutas relativas desde `/home/node/.openclaw/workspace`.

## Cuándo usarla

Activa esta skill cuando el usuario (o `AGENTS.md`) pida:

- auditoría de código, revisión de calidad o deuda técnica;
- optimización de estructura, refactor o simplificación de algoritmos;
- documentación técnica antes de un despliegue;
- análisis de un archivo, módulo o repositorio concreto;
- escenario «refactorización y documentación automática».

## Entrada esperada

- Ruta al archivo o directorio (absoluta o relativa al workspace / home del host).
- Objetivo opcional: rendimiento, legibilidad, despliegue, **seguridad** (prioridad en perfil admin).
- Si falta la ruta, **pregunta una sola vez**; si no responde, usa el archivo más reciente mencionado en el hilo.

## Archivos grandes (>500 líneas) — obligatorio

1. Obtén el conteo de líneas (`wc -l` o metadatos del `read`).
2. Si **>500 líneas**, lee en **segmentos de 250–400 líneas** con solapamiento de ~20 líneas.
3. Tras leer todos los segmentos, **sintetiza** antes de redactar el reporte.
4. Si supera **2000 líneas**, prioriza errores críticos, hotspots y API pública.

## Flujo de trabajo (orden fijo)

1. **Leer** `skills/code-audit/report-template.md` y `skills/code-audit/readme-module-template.md` **en este workspace**.
2. **Inspeccionar** el código fuente (completo o por segmentos).
3. **Analizar:** errores, deuda técnica, rendimiento y **seguridad** (credenciales, red, datos sensibles, inyección).
4. **Refactorizar** y plasmar bloques **Antes / Después** donde aporte valor.
5. **Escribir** reporte y `README.md` del módulo.
6. **Registrar** en `memory/YYYY-MM-DD.md` si la auditoría afecta despliegue o infraestructura.
7. **Responder en chat** con resumen y rutas.

## Archivos de salida (obligatorios)

### Reporte `AUDITORIA_<nombre>_<YYYY-MM-DD>.md`

- Junto al código analizado o en `~/Documentos/Reportes/auditoria-codigo/`.
- Debe incluir: errores, sugerencias, código refactorizado y **justificación técnica** por mejora.

### `README.md` del módulo

- Descripción, propósito de cada función, parámetros, resultados esperados, flujo y despliegue.

### Código en disco

- Solo con confirmación explícita del usuario (`.refactored.<ext>` o sustitución del fuente).

## Formato de respuesta en chat

Ver plantilla en `docs/auditoria-codigo.md` de este workspace.

## Reglas de calidad

- Español profesional; citar `archivo:línea`; no inventar código no leído.
- No modificar fuentes ajenos a la solicitud sin confirmación.

## Referencia

| Recurso | Ruta en workspace admin |
|---------|-------------------------|
| Protocolo | `AGENTS.md` § Auditoría de código |
| Guía usuario | `docs/auditoria-codigo.md` |
| Plantilla reporte | `skills/code-audit/report-template.md` |
| Plantilla README | `skills/code-audit/readme-module-template.md` |
