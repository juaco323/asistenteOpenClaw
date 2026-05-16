# Conexion de Telegram con OpenClaw

Guia paso a paso para conectar el bot de Telegram con las instancias `admin` y `empleado` del repositorio `asistenteOpenClaw`.

## Resultado esperado

Al finalizar:

- `admin` respondera por `http://127.0.0.1:18789`
- `empleado` respondera por `http://127.0.0.1:18790`
- el bot de Telegram correra en `docker/telegram`
- podras cambiar entre workspaces con `/workspace`
- `/chat` y `/recordatorios` quedaran operativos desde Telegram

## Checklist rapido

- [ ] Tener Docker y Docker Compose v2 instalados en el PC de oficina
- [ ] Clonar este repositorio en el PC de oficina
- [ ] Crear `docker/admin/.env` a partir de `docker/admin/.env.example`
- [ ] Crear `docker/empleado/.env` a partir de `docker/empleado/.env.example`
- [ ] Verificar que `OPENCLAW_GATEWAY_TOKEN` tenga valor en ambos `.env`
- [ ] Levantar `admin`
- [ ] Levantar `empleado`
- [ ] Verificar que `docker/admin/openclaw.json` y `docker/empleado/openclaw.json` queden montados en sus contenedores
- [ ] Crear `docker/telegram/.env` a partir de `docker/telegram/.env.pc-oficina.example`
- [ ] Pegar el token nuevo de Telegram
- [ ] Pegar `TELEGRAM_ALLOWED_USER_IDS` (un ID o varios separados por coma, sin espacios)
- [ ] Pegar los tokens de gateway de `admin` y `empleado`
- [ ] Levantar `docker/telegram`
- [ ] Probar `/estado`
- [ ] Probar `/workspace`
- [ ] Probar `/chat`
- [ ] Probar `/recordatorios`
- [ ] (Opcional) En `/chat`, enviar un documento o foto y pedir borrador de correo con ese adjunto

## Paso 1. Rotar el token de Telegram

Como el token anterior fue compartido en el chat, primero rotalo en `@BotFather`.

1. Abre `@BotFather`
2. Usa `/revoke` o genera un token nuevo para tu bot
3. Guarda el token nuevo

## Paso 2. Obtener tu Telegram user ID

Esto sirve para restringir el acceso al bot.

Opciones simples:

1. habla con un bot como `@userinfobot`
2. copia tu `user id`
3. guardalo para `TELEGRAM_ALLOWED_USER_IDS`

## Paso 3. Preparar OpenClaw admin

```bash
cp docker/admin/.env.example docker/admin/.env
```

Edita `docker/admin/.env` y asegurate de definir:

- `OPENCLAW_GATEWAY_TOKEN`
- `OPENAI_API_KEY` si corresponde

Luego:

```bash
chmod +x docker/admin/*.sh
docker/admin/install.sh
```

## Paso 4. Preparar OpenClaw empleado

```bash
cp docker/empleado/.env.example docker/empleado/.env
```

Edita `docker/empleado/.env` y asegurate de definir:

- `OPENCLAW_GATEWAY_TOKEN`
- `OPENAI_API_KEY` si corresponde

Luego:

```bash
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

## Paso 5. Verificar la habilitacion del endpoint para Telegram

El bot usa el endpoint:

- `POST /v1/chat/completions`

Este repo ya deja preparados:

- `docker/admin/openclaw.json`
- `docker/empleado/openclaw.json`

Ambos habilitan:

```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  }
}
```

Si modificaste compose o configuracion, verifica que el archivo quede montado como:

- `/etc/openclaw/openclaw.json` (solo lectura; fuera del volumen `~/.openclaw` del contenedor para que la persistencia del gateway no rompa el bind)

## Paso 6. Preparar el bot de Telegram

Copia el ejemplo exacto para oficina:

```bash
cp docker/telegram/.env.pc-oficina.example docker/telegram/.env
```

Edita `docker/telegram/.env` y reemplaza:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ALLOWED_USER_IDS`
- `OPENCLAW_ADMIN_GATEWAY_TOKEN`
- `OPENCLAW_EMPLEADO_GATEWAY_TOKEN`

Valores esperados:

- `OPENCLAW_ADMIN_BASE_URL=http://host.docker.internal:18789`
- `OPENCLAW_EMPLEADO_BASE_URL=http://host.docker.internal:18790`
- `OPENCLAW_DEFAULT_WORKSPACE=empleado`

## Paso 7. Levantar el bot

```bash
chmod +x docker/telegram/*.sh
docker/telegram/install.sh
```

## Paso 8. Pruebas funcionales en Telegram

Habla con tu bot y prueba:

### 1. Estado

```text
/estado
```

Debes ver algo como:

- `Administrador: OK`
- `Empleado: OK`

### 2. Cambio de workspace

```text
/workspace
```

Selecciona `Administrador` o `Empleado`.

### 3. Chat

```text
/chat
```

Luego envia un mensaje normal.

### 4. Recordatorios

```text
/recordatorios
```

Desde ahi podras listar o crear recordatorios en el workspace activo.

## Paso 9. Mantenimiento

Cuando actualices el repo:

```bash
git pull
docker/admin/update.sh
docker/empleado/update.sh
docker/telegram/update.sh
```

## Correo con adjunto desde Telegram

1. Autentica perfil con `/workspace` y entra en `/chat` o `/correo`.
2. Envía un **documento** o **foto** (puedes añadir pie de mensaje con destinatario, asunto e instrucciones).
3. El bot guarda el archivo bajo `Documentos/telegram-openclaw-incoming/` en `TELEGRAM_HOST_HOME` y reenvía la ruta al gateway; el agente debe crear el borrador con `gog gmail drafts create … --attach /ruta/…`.
4. Confirma el envío en el chat como siempre («envíalo», «mándalo», etc.). Usa el mismo home en `OPENCLAW_HOST_HOME` y `TELEGRAM_HOST_HOME` para que la ruta sea válida en el contenedor del gateway.

## Problemas comunes

### El bot no responde a /start ni a mensajes

- Confirma que el contenedor esta arriba: `docker ps | grep telegram-openclaw-bot`
- Si no existe, ejecuta `docker/telegram/install.sh` (requiere `docker/telegram/.env` configurado).
- Levanta **admin** y **empleado**; el bot usa `host.docker.internal:18789` y `:18790`. Sin empleado, `/estado` falla en esa linea aunque el bot deba responder a `/start` (orden de handlers corregido en el codigo del bot).

### `openclaw-empleado` no arranca por montaje de `openclaw.json`

Si en `~/.openclaw-empleado/` existe un `openclaw.json` vacio (0 bytes), puede chocar con el bind mount del repo. Borralo y vuelve a ejecutar `docker/empleado/install.sh` (el script ahora elimina ese archivo vacio antes del `up`).

### `/estado` falla con 401 o 403

El `OPENCLAW_*_GATEWAY_TOKEN` del bot no coincide con el token del gateway.

### `/chat` falla con 404

- Confirma `gateway.http.endpoints.chatCompletions.enabled` en `docker/admin/openclaw.json` y `docker/empleado/openclaw.json`.
- Si el JSON del repo esta bien pero sigue 404: el gateway pudo **sustituir** `openclaw.json` bajo el volumen de estado y **romper** el bind de un archivo sobre un directorio (se pierde `gateway.port` u otras claves). Con el compose actual la plantilla va en `/etc/openclaw/openclaw.json`; recrea el contenedor (`docker compose up -d --force-recreate` en `docker/admin` y `docker/empleado`).

### El perfil Empleado (o Admin) habla de estar "en blanco" y pide definir nombre, vibe, emoji

Eso ocurre si en el workspace del gateway (`~/.openclaw-empleado/workspace/` o `~/.openclaw-admin/workspace/`) existe **`BOOTSTRAP.md`**: OpenClaw lo usa como arranque y pide co-crear identidad en lugar de seguir `SOUL.md` / `IDENTITY.md`. Borra `BOOTSTRAP.md` en ese directorio (o vuelve a ejecutar `docker/empleado/install.sh` / `docker/admin/install.sh`: el script ya lo elimina despues de copiar `workspace-*`).

### El bot responde pero cualquiera puede usarlo

Falta configurar `TELEGRAM_ALLOWED_USER_IDS` o `TELEGRAM_ALLOWED_USERNAMES`.

### El bot no alcanza `18789` o `18790`

Verifica que `admin` y `empleado` esten levantados en el host y que el contenedor del bot use:

- `host.docker.internal:18789`
- `host.docker.internal:18790`
