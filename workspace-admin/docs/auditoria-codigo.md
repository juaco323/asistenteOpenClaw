# Auditoría de código — perfil administrador

Guía operativa para solicitar auditorías de código desde el workspace **administrador**.

## Qué hace el asistente

1. Lee el archivo o módulo indicado (soporta **más de 500 líneas** leyendo por segmentos).
2. Genera un **reporte detallado** con errores, sugerencias, código refactorizado y explicación técnica del porqué.
3. Crea o actualiza un **`README.md`** con documentación técnica del módulo.
4. En perfil admin, prioriza hallazgos de **seguridad** y cumplimiento cuando el código toque credenciales, red o datos sensibles.

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

Ubicación por defecto: **junto al código**. Alternativa: `~/Documentos/Reportes/auditoria-codigo/`.

## Criterios de aceptación

- Archivos de **cualquier lenguaje** y **>500 líneas**.
- Errores, sugerencias, código refactorizado y **justificación técnica**.
- Refactor (simplificar algoritmos, eliminar redundancia, renombrar) + README con funciones, parámetros y resultados.

## Definición del protocolo

- Skill: [`skills/code-audit/SKILL.md`](skills/code-audit/SKILL.md)
- Reglas operativas: [`AGENTS.md`](AGENTS.md) (sección «Protocolo de Auditoría de código»)
