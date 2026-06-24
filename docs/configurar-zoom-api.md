# Configurar Zoom API (OpenClaw — perfil Administrador)

Las reuniones Zoom usan **Server-to-Server OAuth** de Zoom Marketplace y envían invitaciones/cancelaciones por **Gmail** (`gog`).

## 1. Crear app en Zoom

1. Entra en [Zoom Marketplace](https://marketplace.zoom.us/) → **Develop** → **Build App**.
2. Tipo: **Server-to-Server OAuth**.
3. Anota **Account ID**, **Client ID** y **Client Secret**.
4. En **Scopes** → **Add Scopes**, busca en el producto **Meeting** (reuniones). Zoom usa **scopes granulares** (apps nuevas); los nombres clásicos `meeting:write:admin` pueden no aparecer. Añade al menos:

   | Acción | Scope granular (buscar en la UI) |
   |--------|----------------------------------|
   | Crear reunión | `meeting:write:meeting:admin` (o descripción «Create a meeting») |
   | Eliminar reunión | `meeting:delete:meeting:admin` (o «Delete a meeting») |

   Alternativa clásica (apps antiguas): `meeting:write:admin` + `meeting:delete:admin`.

   En el buscador de scopes escribe **meeting** y filtra por **Meeting**; marca las filas de **create** y **delete** con sufijo **:admin**.
5. Activa la app.

## 2. Variables en el host

Edita `docker/admin/.env`:

```bash
ZOOM_ACCOUNT_ID=tu_account_id
ZOOM_CLIENT_ID=tu_client_id
ZOOM_CLIENT_SECRET=tu_client_secret
```

**No** commitear secretos. Reinicia el contenedor admin tras guardar:

```bash
docker compose --env-file docker/admin/.env -f docker/admin/docker-compose.yml up -d openclaw-admin
```

## 3. Probar token (host o contenedor)

```bash
set -a && source docker/admin/.env && set +a

curl -s -X POST "https://zoom.us/oauth/token" \
  -u "${ZOOM_CLIENT_ID}:${ZOOM_CLIENT_SECRET}" \
  -d "grant_type=account_credentials&account_id=${ZOOM_ACCOUNT_ID}" | python3 -m json.tool
```

Debe devolver `access_token`.

## 4. Probar scripts

```bash
./scripts/zoom-meeting-create.sh --dry-run \
  --summary "Prueba OpenClaw" \
  --from "2026-12-01T10:00:00-03:00" \
  --duration 30 \
  --attendees "prueba@ejemplo.com" \
  --admin-name "Admin Prueba"
```

Creación real (Gmail OAuth OK):

```bash
docker exec openclaw-admin zoom-meeting-create.sh \
  --summary "…" --from "…" --attendees "…" --admin-name "…"
```

## 5. Canales de uso

- **Telegram:** `/workspace admin` → `/comunicaciones` o `/chat`
- **Control UI:** `http://127.0.0.1:18791/`

Protocolo del agente: `workspace-admin/skills/admin-comms/zoom-meetings.md` y `AGENTS.md` § Reuniones Zoom.
