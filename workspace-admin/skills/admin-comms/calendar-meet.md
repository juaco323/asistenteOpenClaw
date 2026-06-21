# Google Calendar + Meet — exclusivo perfil **Administrador**

Crea eventos en Google Calendar con **enlace Google Meet**, recordatorios en el calendario y opción de enviar el link por correo (vía `email-gmail`).

**Solo workspace `workspace-admin`.** El perfil **empleado** no ejecuta `gog calendar`; puede redactar recordatorios por correo con `admin-comms`.

**Cuenta obligatoria:** `prueba.openclaw.fj@gmail.com` (`-a` en todos los comandos).

**Requisito OAuth:** `gog auth add … --services gmail,drive,calendar` (ver `scripts/gog-auth-setup.sh`).

## Cuándo usar este complemento

- Agendar reunión con **Google Meet** para una fecha concreta.
- Crear **evento en calendario** con recordatorios (`popup`, email Calendar).
- Tras crear, enviar el **link de Meet por correo** (confirmación aparte, `email-gmail`).

## Datos mínimos

| Campo | Obligatorio |
|-------|-------------|
| Título | sí |
| Fecha/hora inicio | sí |
| Duración o fin | sí (o 1 h por defecto) |
| Invitados | recomendado |
| Zona horaria | `America/Santiago` si falta |

## Crear evento con Meet

```bash
gog calendar create primary \
  -a "prueba.openclaw.fj@gmail.com" \
  --summary "Reunión de seguimiento — Proyecto OpenClaw" \
  --from "2026-06-27T10:00:00-04:00" \
  --to "2026-06-27T11:00:00-04:00" \
  --with-meet \
  --attendees "invitado@empresa.com" \
  --reminder "popup:30m,email:1d" \
  --send-updates all \
  --json
```

Script auxiliar: `scripts/gog-calendar-meet-create.sh` (solo admin).

## Flujo integrado `admin-comms`

1. **Propuesta** → `pendiente_confirmacion` (tipo `reunion_meet`); sin `gog calendar create`.
2. **Confirmación** («agéndala») → crear evento → `reunion_creada` + Meet link en borrador y `LOGS_COMMS.md`.
3. **Correo con link** (opcional, paso aparte) → `email-gmail` → `enviado`.

## Rutas admin (Docker)

| Recurso | Ruta |
|---------|------|
| `LOGS_COMMS.md` | `/app/logs_shared/LOGS_COMMS.md` |
| Borradores | `~/Documentos/Comunicaciones/borradores/` |

Columna **Agente:** `Administrador`. Puede `gog calendar update` / `delete` tras confirmación verbal.

## Errores

| Error | Acción |
|-------|--------|
| `No auth for calendar` | OAuth con scope `calendar` |
| `No tokens stored` | `./scripts/gog-auth-setup.sh` |
