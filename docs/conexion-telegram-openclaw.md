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
- [ ] Pegar tu `TELEGRAM_ALLOWED_USER_IDS`
- [ ] Pegar los tokens de gateway de `admin` y `empleado`
- [ ] Levantar `docker/telegram`
- [ ] Probar `/estado`
- [ ] Probar `/workspace`
- [ ] Probar `/chat`
- [ ] Probar `/recordatorios`

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

- `/home/node/.openclaw/openclaw.json`

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

## Problemas comunes

### `/estado` falla con 401 o 403

El `OPENCLAW_*_GATEWAY_TOKEN` del bot no coincide con el token del gateway.

### `/chat` falla con 404

No esta habilitado `chatCompletions` en OpenClaw o no quedo montado `openclaw.json`.

### El bot responde pero cualquiera puede usarlo

Falta configurar `TELEGRAM_ALLOWED_USER_IDS` o `TELEGRAM_ALLOWED_USERNAMES`.

### El bot no alcanza `18789` o `18790`

Verifica que `admin` y `empleado` esten levantados en el host y que el contenedor del bot use:

- `host.docker.internal:18789`
- `host.docker.internal:18790`
