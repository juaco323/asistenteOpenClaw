# Skill: Transcripción de audio (Whisper via OpenAI API) — perfil empleado

Transcribe archivos de audio a texto usando el modelo **Whisper** de OpenAI mediante `curl`.
La variable `OPENAI_API_KEY` ya está disponible en el entorno del contenedor (`docker/empleado/.env`).

**Workspace:** `workspace-empleado`.

## Cuándo usarla

- El usuario pide transcribir, leer o extraer texto de un archivo de audio o voz.
- El usuario comparte un audio para generar actas, informes o resúmenes de reuniones.
- Se recibe un audio por Telegram (mensaje `[Audio recibido por Telegram — transcribir con skill transcribe-audio]`; archivo en `~/Documentos/telegram-openclaw-incoming/`).

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

echo "$TRANSCRIPT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('text',''))"
```

## Flujo completo con acta de reunión

```bash
AUDIO_FILE="/home/joaquin/Documentos/reunion.m4a"
SIZE=$(stat -c%s "$AUDIO_FILE" 2>/dev/null || echo 0)
[ "$SIZE" -gt 26214400 ] && echo "AVISO: archivo supera 25 MB" && exit 1

TRANSCRIPT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F model=whisper-1 \
  -F language=es \
  -F response_format=json \
  -F "file=@${AUDIO_FILE}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))")

# Guardar transcripción y acta en Reportes
mkdir -p /home/joaquin/Documentos/Reportes
echo "$TRANSCRIPT" > "/home/joaquin/Documentos/Reportes/$(date +%Y-%m-%d)_transcripcion_$(basename "${AUDIO_FILE%.*}").txt"
```

Tras transcribir, puedes redactar acta o resumen en `~/Documentos/Reportes/` (mismo criterio que minutas de imágenes).

## Diagnóstico de errores

| Error | Causa | Solución |
|---|---|---|
| `401 Unauthorized` | `OPENAI_API_KEY` vacía o inválida | Verificar `docker/empleado/.env` y recrear contenedor |
| `400 Invalid file format` | Formato no soportado | Pedir `.mp3`, `.wav`, `.m4a` u otro formato válido |
| `413 File too large` | Archivo supera 25 MB | Pedir recorte o compresión |
| Respuesta vacía | Audio sin habla | Confirmar con el usuario |

## Verificar API key

```bash
[ -z "$OPENAI_API_KEY" ] && echo "ERROR: OPENAI_API_KEY no definida" || echo "API key presente"
```

## Notas de seguridad

- **No** mostrar `OPENAI_API_KEY` en el chat.
- El audio se envía a OpenAI; avisar si el contenido es confidencial.
- Guardar transcripciones solo bajo `~/Documentos/` salvo confirmación explícita.

## Referencia

| Recurso | Ruta |
|---------|------|
| Protocolo operativo | `AGENTS.md` § Transcripción de audio |
| Notas locales | `TOOLS.md` |
