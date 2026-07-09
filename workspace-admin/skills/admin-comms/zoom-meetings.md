# Reuniones Zoom — exclusivo perfil **Administrador**

Crea reuniones **Zoom** programadas, envía **invitación por correo Gmail** a los asistentes y permite **cancelar** notificando por correo a cada invitado.

**Solo workspace `workspace-admin`.** El perfil **empleado** no ejecuta scripts Zoom; puede redactar recordatorios por correo con `admin-comms`.

## Canales (misma regla en ambos)

| Canal | Acceso admin Zoom |
|-------|-------------------|
| **Control UI OpenClaw** | Gateway admin `http://127.0.0.1:18791/` |
| **Telegram** | `/workspace admin` + contraseña → `/comunicaciones` o `/chat` |

En **empleado** (`:18790` o `/workspace empleado`): rechazar crear/cancelar Zoom y derivar a administrador.

## Requisitos

1. App **Server-to-Server OAuth** en [Zoom Marketplace](https://marketplace.zoom.us/) con scopes granulares `meeting:write:meeting:admin` y `meeting:delete:meeting:admin` (o clásicos `meeting:write:admin` / `meeting:delete:admin` en apps antiguas).
2. Variables en `docker/admin/.env`: `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`.
3. Guía: `docs/configurar-zoom-api.md`.
4. Correo de invitación/cancelación: cuenta **`prueba.openclaw.fj@gmail.com`** vía `gog` (mismo OAuth Gmail del proyecto).

## Cuándo usar (vs Google Meet)

| Plataforma | Skill / script |
|------------|----------------|
| **Google Calendar + Meet** | `calendar-meet.md`, `gog-calendar-meet-*.sh` |
| **Zoom** | este archivo, `zoom-meeting-*.sh` |

Si el usuario pide explícitamente **Zoom**, usa este flujo. Si pide **Meet** o **Calendar**, usa `calendar-meet.md`.

## Datos mínimos

| Campo | Obligatorio |
|-------|-------------|
| Título | sí |
| Fecha/hora inicio | sí |
| Duración o hora fin | sí (o 60 min por defecto) |
| Invitados (correos) | recomendado (sin ellos no hay invitación por Gmail) |
| Nombre para firma (`Atte:`) | sí en cancelación; recomendado al crear |
| Zona horaria | `America/Santiago` si falta |

## Crear reunión Zoom

```bash
zoom-meeting-create.sh \
  --summary "Reunión de seguimiento — Proyecto OpenClaw" \
  --from "2026-06-27T10:00:00-04:00" \
  --duration 60 \
  --attendees "invitado@empresa.com,otro@empresa.com" \
  --admin-name "María González"
```

En contenedor admin: `/usr/local/bin/zoom-meeting-create.sh`.

**Efecto:** crea reunión en Zoom API → si hay `--attendees`, envía **automáticamente** correo Gmail con título, fecha, enlace Zoom y `Atte:` (**no** hace falta un segundo «envíalo»).

## Flujo integrado `admin-comms`

### Crear reunión Zoom

1. **Propuesta** → `pendiente_confirmacion` (tipo `reunion_zoom`); **sin** llamar a Zoom aún.
2. Extraer título, fecha/hora, duración, **correos** y nombre para firma si aplica.
3. **Confirmación** («agéndala», «créala en Zoom», «vale», etc.) → ejecutar `zoom-meeting-create.sh` en el **mismo turno**.
4. Estado **`reunion_zoom_creada`** en `LOGS_COMMS.md` (notas: `MEETING_ID`, enlace Zoom, invitados).

### Cancelar reunión Zoom

1. **Identificar** reunión: `LOGS_COMMS.md` → tabla de reuniones (tipo `reunion_zoom`, columna «Enlace / ID» = `MEETING_ID` Zoom), o ID que indique el usuario.
2. **Motivo obligatorio** (asunto del correo). Si falta, **preguntar**.
3. **Nombre para firma obligatorio** (`Atte:`). Si falta, **preguntar explícitamente**.
4. **Resumen** con título, **correos**, motivo y Atte → `pendiente_confirmacion` (tipo `reunion_zoom_cancelacion`).
5. Tras confirmación explícita («confirma cancelación», etc.):

```bash
zoom-meeting-cancel.sh \
  --meeting-id "<ID>" \
  --reason "<motivo>" \
  --admin-name "<nombre Atte>" \
  --attendees "correo1@empresa.com,correo2@empresa.com"
```

6. Estado **`reunion_zoom_cancelada`** en `LOGS_COMMS.md`.

**Formato del correo de cancelación:**

| Campo | Contenido |
|-------|-----------|
| **Asunto** | Motivo de cancelación |
| **Cuerpo** | `La reunión por Zoom ha sido cancelada.` + tab + `Atte: {nombre}` |

**Prohibido** borrador Gmail manual para cancelación Zoom; usar siempre el script.

## Rutas admin (Docker)

| Recurso | Ruta |
|---------|------|
| `LOGS_COMMS.md` | `/app/logs_shared/LOGS_COMMS.md` |
| Borradores | `~/Documentos/Comunicaciones/borradores/` |

Columna **Agente:** `Administrador`.

## Errores

| Error | Acción |
|-------|--------|
| Faltan `ZOOM_*` en `.env` | Completar `docker/admin/.env` y **recrear** contenedor: `docker compose --env-file docker/admin/.env -f docker/admin/docker-compose.yml up -d --build` (`restart` no recarga variables). Ver `docs/configurar-zoom-api.md` |
| `Invalid access token` | Revisar Client ID/Secret y scopes S2S |
| Sin destinatarios al cancelar | Pasar `--attendees` del resumen |
| Invitación no enviada al crear | Incluir `--attendees`; revisar OAuth Gmail (`gog auth list`) |
