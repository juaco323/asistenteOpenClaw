# Pruebas de ejemplo para medición de latencia (LLM)

Este documento sirve **solo** como batería de prompts y comandos repetibles para comparar **latencias de extremo a extremo** (llamada HTTP al gateway hasta respuesta completa). Los resultados quedan en `workspace-<perfil>/.llm-test-runs.jsonl` y en el panel Docker del mismo perfil.

## Requisitos previos

- Gateway **admin** y/o **empleado** en marcha (`docker/admin`, `docker/empleado`).
- `docker/<perfil>/.env` con `OPENCLAW_GATEWAY_TOKEN` y `OPENCLAW_HOST_PORT` correctos.
- Primera vez: `chmod +x docker/admin/llm-test-logger/run.sh` (crea el venv en `docker/admin/llm-test-logger/.venv`).

## Variables útiles

```bash
export OPENCLAW_REPO="$HOME/Documentos/openClaw"
RUN_ADMIN="$OPENCLAW_REPO/docker/admin/llm-test-logger/run.sh"
RUN_EMP="$OPENCLAW_REPO/docker/empleado/llm-test-logger/run.sh"
```

## Conjunto mínimo (comparar frío vs caliente)

Ejecuta cada línea **varias veces** y anota la latencia en el panel (columna **Latencia (s)**).

### Respuesta mínima (suele ser rápida)

```bash
"$RUN_ADMIN" "Responde únicamente con la palabra: OK."
"$RUN_EMP" "Responde únicamente con la palabra: OK."
```

### Respuesta media (párrafo)

```bash
"$RUN_ADMIN" "Explica en cuatro oraciones qué es la latencia en una API HTTP."
"$RUN_EMP" "Explica en cuatro oraciones qué es la latencia en una API HTTP."
```

### Respuesta larga (listas / estructura)

```bash
"$RUN_ADMIN" "Enumera diez buenas prácticas para medir rendimiento de un LLM en producción, cada una en una línea numerada."
"$RUN_EMP" "Enumera diez buenas prácticas para medir rendimiento de un LLM en producción, cada una en una línea numerada."
```

## Casos para detectar variabilidad

### Mismo prompt repetido (5 veces)

Útil para ver dispersión sin cambiar el texto.

```bash
for i in 1 2 3 4 5; do
  "$RUN_ADMIN" "Iteración $i: responde solo con el número $i."
done
```

### Instrucción con formato estricto (más tokens de salida)

```bash
"$RUN_ADMIN" "Devuelve un JSON con las claves latencia_ms, notas y escenario, con valores inventados de ejemplo. Sin markdown."
```

### Razonamiento breve (si el modelo lo permite)

```bash
"$RUN_ADMIN" "Un tren sale a las 10:00 a 60 km/h. Otro sale a las 10:15 a 90 km/h en la misma vía. ¿A qué hora alcanza el segundo al primero? Muestra solo el resultado final en una frase."
```

## Dónde ver los números

- **Admin:** `http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/` (valor en `docker/admin/.env`, por defecto compose `18794`).
- **Empleado:** `http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/` (valor en `docker/empleado/.env`, por defecto compose `18795`).

Tras cada tanda, **recarga** la página del panel.

## Telegram (solo admin)

Con perfil Administrador autenticado:

```text
/prueba_llm Responde solo con la palabra LISTO.
```

## Nota metodológica

La latencia registrada **no** separa red, cola del gateway y tiempo del proveedor; es el tiempo total de la petición. Para comparaciones justas, mantén el mismo modelo, la misma carga del host y repite en ventanas similares (por ejemplo todas por la mañana).
