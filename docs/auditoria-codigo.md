# Auditoría de código (OpenClaw)

Guía operativa para colaboradores y empleadores que usan el asistente para revisar código antes de despliegue.

## Qué hace el asistente

1. Lee el archivo o módulo indicado (soporta **más de 500 líneas** leyendo por segmentos).
2. Genera un **reporte detallado** con errores, sugerencias, código refactorizado y explicación técnica del porqué.
3. Crea o actualiza un **`README.md`** con documentación técnica del módulo.

## Cómo solicitarlo (ejemplos)

- «Audita `/ruta/al/archivo.py` antes del despliegue»
- «Optimiza la estructura de `src/services/payments.ts` y genera documentación técnica»
- «Revisa deuda técnica en el módulo `backend/auth/` y propón refactor»

Indica siempre la **ruta** al código. Opcional: prioridad (rendimiento, seguridad, legibilidad).

## Entregables

| Archivo | Descripción |
|---------|-------------|
| `AUDITORIA_<nombre>_<fecha>.md` | Reporte completo |
| `README.md` | Documentación en la carpeta del módulo |
| `*.refactored.*` | Solo si pides aplicar cambios al disco |

Por defecto los reportes se guardan **junto al código**. También puedes pedir que vayan a:

`~/Documentos/Reportes/auditoria-codigo/`

## Criterios de aceptación (historia de usuario)

- Procesa archivos de **cualquier lenguaje** y **>500 líneas**.
- Incluye: errores, sugerencias, código refactorizado y **justificación técnica**.
- Escenario de despliegue: refactor (simplificar algoritmos, eliminar redundancia, renombrar) + README con funciones, parámetros y resultados esperados.

## Perfiles

- **Empleado:** `workspace-empleado/skills/code-audit/` y `workspace-empleado/docs/auditoria-codigo.md`
- **Administrador:** `workspace-admin/skills/code-audit/` y `workspace-admin/docs/auditoria-codigo.md`

Copia de referencia en el monorepo: [`skills/code-audit/SKILL.md`](../skills/code-audit/SKILL.md).
