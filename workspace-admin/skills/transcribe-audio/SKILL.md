# Skill: Transcripción de audio (Whisper via OpenAI API)

Transcribe archivos de audio a texto usando el modelo **Whisper** de OpenAI mediante `curl`.
La variable `OPENAI_API_KEY` ya está disponible en el entorno del contenedor.

## Cuándo usarla

- El usuario pide transcribir, leer o extraer texto de un archivo de audio o voz.
- El usuario comparte un audio para generar actas, informes o resúmenes de reuniones.
- Se recibe un archivo de audio por Telegram (guardado en `~/Documentos/telegram-openclaw-incoming/`).

## Formatos de audio soportados

`mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`, `ogg`, `flac`
Tamaño máximo: **25 MB**. Si el archivo supera ese límite, avisar al usuario.

## Comando de transcripción

```bash
AUDIO_FILE="/ruta/absoluta/al/archivo.mp3"
TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F model=whisper-1 \
  -F language=es \
  -F response_format=json \
  -F "file=@${AUDIO_FILE}")

# Extraer solo el texto
echo "$TRANSCRIPT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('text',''))"
```

### Parámetros clave

| Parámetro | Valor | Notas |
|---|---|---|
| `model` | `whisper-1` | Único modelo disponible para este endpoint |
| `language` | `es` | Español. Omitir si el idioma es desconocido (Whisper lo detecta) |
| `response_format` | `json` | Devuelve `{ "text": "..." }` |
| `file` | `@/ruta/absoluta` | La `@` es obligatoria para `curl -F` |

## Flujo completo con acta de reunión

```bash
# 1. Verificar que el archivo existe y pesa menos de 25 MB
AUDIO_FILE="/home/node/Documentos/reunion.m4a"
SIZE=$(stat -c%s "$AUDIO_FILE" 2>/dev/null || echo 0)
[ "$SIZE" -gt 26214400 ] && echo "AVISO: archivo supera 25 MB" && exit 1

# 2. Transcribir
TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F model=whisper-1 \
  -F language=es \
  -F response_format=json \
  -F "file=@${AUDIO_FILE}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))")

# 3. Guardar la transcripción en texto plano
echo "$TRANSCRIPT" > "${AUDIO_FILE%.*}_transcripcion.txt"
echo "Transcripción guardada en: ${AUDIO_FILE%.*}_transcripcion.txt"
```

## Diagnóstico de errores

| Error | Causa | Solución |
|---|---|---|
| `401 Unauthorized` | `OPENAI_API_KEY` vacía o inválida | Verificar variable de entorno en el contenedor |
| `400 Invalid file format` | Formato no soportado | Pedir al usuario un archivo `.mp3`, `.wav`, `.m4a` u otro formato válido |
| `413 File too large` | Archivo supera 25 MB | Informar al usuario; pedir que recorte o comprima el audio |
| `curl: (6) Could not resolve host` | Sin conexión a internet | Verificar red del contenedor |
| Respuesta vacía (`text: ""`) | Audio sin habla o muy corto | Confirmar con el usuario que el archivo tiene voz audible |

## Verificar que la API key está disponible

```bash
[ -z "$OPENAI_API_KEY" ] && echo "ERROR: OPENAI_API_KEY no definida" || echo "API key presente"
```

## Notas de seguridad

- **No** mostrar el valor de `OPENAI_API_KEY` en el chat bajo ninguna circunstancia.
- El audio se envía a los servidores de OpenAI; informar al usuario si el contenido es confidencial.
- No guardar transcripciones en rutas fuera del home del usuario sin confirmación explícita.
