# Auditoría de código — {{NOMBRE_MODULO}}

- **Fecha:** {{YYYY-MM-DD}}
- **Archivo(s) analizado(s):** `{{RUTA_ARCHIVO}}`
- **Lenguaje:** {{LENGUAJE}}
- **Líneas totales:** {{LINEAS}}
- **Agente:** {{PERFIL}} (admin | empleado)
- **Solicitud:** {{RESUMEN_SOLICITUD}}

## Resumen ejecutivo

{{2-4 frases: estado general, severidad principal, recomendación de despliegue}}

## Errores detectados

| ID | Severidad | Ubicación | Descripción | Impacto |
|----|-----------|-----------|-------------|---------|
| E-01 | alta/media/baja | `archivo:Línea` | … | … |

## Deuda técnica y riesgos

- …

## Sugerencias de mejora

| ID | Categoría | Ubicación | Sugerencia | Por qué es mejor que el enfoque actual |
|----|-----------|-----------|------------|----------------------------------------|
| S-01 | rendimiento/legibilidad/mantenibilidad/seguridad | `archivo:Línea` | … | … |

## Código refactorizado

### Fragmento 1 — {{nombre_función o sección}}

**Antes** (`archivo`, líneas X–Y):

```{{lang}}
// código original relevante
```

**Después** (propuesta):

```{{lang}}
// código refactorizado
```

**Justificación técnica:** …

(repetir por cada fragmento significativo)

## Plan de acción recomendado

1. …
2. …

## Archivos generados

| Archivo | Ruta |
|---------|------|
| Reporte de auditoría | `{{RUTA_REPORTE}}` |
| Documentación técnica | `{{RUTA_README}}` |
| Código refactorizado (opcional) | `{{RUTA_REFACTOR}}` |
