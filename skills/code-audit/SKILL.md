# Skill: Auditoría de código

Analiza archivos de código completos (cualquier lenguaje), identifica deuda técnica, sugiere optimizaciones de rendimiento, entrega código refactorizado con justificación técnica y genera documentación en Markdown.

## Cuándo usarla

Activa esta skill cuando el usuario (o un protocolo de workspace) pida, de forma explícita o implícita:

- auditoría de código, revisión de calidad o deuda técnica;
- optimización de estructura, refactor o simplificación de algoritmos;
- documentación técnica antes de un despliegue;
- análisis de un archivo, módulo o repositorio concreto;
- escenario «refactorización y documentación automática».

**Perfiles:** administrador y empleado (mismo flujo; el administrador puede añadir comentarios de seguridad y cumplimiento si aplica).

## Entrada esperada

- Ruta al archivo o directorio (absoluta o relativa al workspace).
- Objetivo opcional: rendimiento, legibilidad, despliegue, seguridad.
- Si falta la ruta, **pregunta una sola vez**; si no responde, usa el archivo más reciente mencionado en el hilo.

## Archivos grandes (>500 líneas) — obligatorio

1. Obtén el conteo de líneas (`wc -l` o metadatos del `read`).
2. Si **>500 líneas**, **no** intentes inferir el archivo entero de memoria:
   - Lee en **segmentos de 250–400 líneas** con solapamiento de ~20 líneas entre bloques.
   - Mantén un mapa mental: imports, tipos globales, funciones públicas, dependencias cruzadas.
   - Tras leer todos los segmentos, **sintetiza** antes de redactar el reporte.
3. Si el archivo supera **2000 líneas**, prioriza en el reporte: errores críticos, hotspots de rendimiento y funciones públicas; documenta en README solo la API expuesta y enlaza al reporte para el detalle.

## Flujo de trabajo (orden fijo)

1. **Leer** `skills/code-audit/report-template.md` y `skills/code-audit/readme-module-template.md`.
2. **Inspeccionar** el código fuente (completo, por segmentos si aplica).
3. **Analizar** en estas categorías:
   - **Errores:** bugs lógicos, manejo incorrecto de nulos/excepciones, condiciones de carrera, fugas de recursos, APIs mal usadas.
   - **Deuda técnica:** duplicación, nombres opacos, funciones demasiado largas, acoplamiento, magic numbers, falta de tests.
   - **Rendimiento:** complejidad algorítmica, I/O innecesario, allocations en bucles calientes, consultas N+1, etc.
   - **Seguridad** (si aplica): inyección, secretos en código, validación de entrada insuficiente.
4. **Refactorizar** mentalmente y plasmar en el reporte bloques **Antes / Después** solo donde el cambio aporte valor claro (no reescribir por estilo).
5. **Escribir archivos de salida** (ver sección siguiente).
6. **Responder en chat** con resumen ejecutivo y rutas de los archivos generados; no pegues el reporte completo si supera ~150 líneas.

## Archivos de salida (obligatorios)

### 1. Reporte de auditoría

- **Nombre:** `AUDITORIA_<nombre-base>_<YYYY-MM-DD>.md`
- **Ubicación preferida:** junto al código analizado (misma carpeta que el archivo o raíz del módulo).
- **Alternativa acordada en monorepo:** `~/Documentos/Reportes/auditoria-codigo/` (crear directorio si no existe).
- **Contenido mínimo** (usa la plantilla):
  - Errores detectados (tabla con severidad y ubicación).
  - Sugerencias de mejora.
  - Código refactorizado (fragmentos Antes/Después).
  - **Justificación técnica** por sugerencia: por qué el cambio supera el estándar o patrón actual (complejidad, mantenibilidad, rendimiento, principios SOLID/DRY, convenciones del lenguaje).

### 2. Documentación técnica — `README.md`

- **Ubicación:** carpeta del módulo analizado (directorio del archivo o raíz del paquete).
- Si ya existe `README.md`, **actualiza** la sección de documentación técnica y añade fila en «Historial de auditorías»; no borres contenido útil del usuario sin avisar.
- **Contenido obligatorio:**
  - Descripción general y propósito del entregable.
  - Propósito de **cada función / método / componente** relevante.
  - **Parámetros de entrada** y **resultados esperados**.
  - Flujo de ejecución y notas de despliegue/mantenimiento.

### 3. Código refactorizado (opcional en disco)

- Solo escribe un archivo `.refactored.<ext>` o sustituye el original si el usuario lo pide **explícitamente**.
- Por defecto, el código refactorizado vive en el **reporte**; menciona en chat que puede aplicarse bajo confirmación.

## Formato de respuesta en chat

```text
## Auditoría completada — <nombre>

**Archivo:** `ruta` (<N> líneas)
**Reporte:** `ruta/AUDITORIA_....md`
**README:** `ruta/README.md`

### Resumen
- Errores: N (X altos, Y medios, Z bajos)
- Sugerencias: N
- Refactorizaciones propuestas: N

### Hallazgos críticos (máx. 3)
1. …

¿Quieres que aplique las refactorizaciones al archivo fuente?
```

## Reglas de calidad

- **Idioma:** español profesional en reportes y README.
- **Precisión:** cita siempre `archivo:línea` o rango cuando sea posible.
- **Sin alucinaciones:** no inventes funciones ni dependencias que no hayas leído.
- **Alcance:** no modifiques otros archivos del repo salvo los entregables de esta skill y el código fuente si el usuario confirma.
- **web / APA:** esta skill no exige búsqueda web salvo que compares con documentación externa del framework; en ese caso aplica el protocolo APA del workspace.

## Integración con workspaces

- Protocolo detallado en `workspace-admin/AGENTS.md` y `workspace-empleado/AGENTS.md` (sección «Auditoría de código»).
- Capacidad listada en `IDENTITY.md` de cada workspace.

## Referencia rápida de plantillas

| Plantilla | Ruta |
|-----------|------|
| Reporte | `skills/code-audit/report-template.md` |
| README módulo | `skills/code-audit/readme-module-template.md` |
