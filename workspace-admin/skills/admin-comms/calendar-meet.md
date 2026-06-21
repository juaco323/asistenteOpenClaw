# Google Calendar + Meet — exclusivo perfil **Administrador**

Crea eventos en Google Calendar con **enlace Google Meet**, **invitaciones por correo a asistentes** (Google Calendar) y recordatorios en el calendario.

**Solo workspace `workspace-admin`.** El perfil **empleado** no ejecuta `gog calendar` (ni crear ni cancelar); puede redactar recordatorios por correo con `admin-comms`.

## Canales (misma regla en ambos)

| Canal | Acceso admin Calendar/Meet |
|-------|----------------------------|
| **Control UI OpenClaw** | Gateway admin `http://127.0.0.1:18791/` |
| **Telegram** | `/workspace admin` + contraseña → `/comunicaciones` o `/chat` |

En **empleado** (`:18790` o `/workspace empleado`): rechazar crear/cancelar reuniones y derivar a administrador.

**Cuenta obligatoria:** `prueba.openclaw.fj@gmail.com` (`-a` en todos los comandos).

**Requisito OAuth:** `gog auth add … --services gmail,drive,calendar` (ver `scripts/gog-auth-setup.sh`).

## Invitaciones vs recordatorios (no confundir)

| Mecanismo | Cuándo | Flag |
|-----------|--------|------|
| **Invitación por correo** a cada asistente | **Al crear** (o al actualizar) el evento | `--send-updates all` (**obligatorio** si hay invitados) |
| Recordatorio de calendario (popup / email) | Antes del evento (p. ej. 30 min / 1 día) | `--reminder popup:30m,email:1d` |

`gog` usa **`--send-updates none` por defecto**. Sin `all`, los invitados quedan en el evento pero **no reciben correo de invitación**.

Correo adicional con texto personalizado (opcional): paso aparte con `email-gmail`; **no sustituye** la invitación de Calendar.

## Cuándo usar este complemento

- Agendar reunión con **Google Meet** para una fecha concreta.
- Crear **evento en calendario** con invitados que reciban invitación al momento.
- Recordatorios en calendario (`popup`, email Calendar).

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

### Crear reunión

1. **Propuesta** → `pendiente_confirmacion` (tipo `reunion_meet`); sin `gog calendar create`.
2. **Confirmación** («agéndala») → crear evento con **`--send-updates all`** si hay invitados → `reunion_creada` + Meet link en borrador y `LOGS_COMMS.md`. Los invitados deben recibir **invitación de Google Calendar al instante**.
3. **Correo personalizado con link** (opcional, paso aparte) → `email-gmail` → `enviado`.

### Cancelar reunión (**solo Administrador**)

Cuando el usuario pida **cancelar**, **anular** o **eliminar** una reunión ya creada en Calendar:

1. **Identificar** el evento: `LOGS_COMMS.md` (Event ID / título), o `gog calendar events list primary -a "prueba.openclaw.fj@gmail.com" --json`.
2. **Motivo obligatorio:** si el admin no indicó por qué se cancela, **preguntar** antes de cualquier acción externa. **Prohibido** cancelar sin motivo. El motivo será el **asunto del correo**.
3. **Nombre del administrador obligatorio:** si no indicó quién cancela, **preguntar** (nombre de la persona que cancela). Aparecerá en la descripción del correo (`Atte: …`).
4. **Resumen** para confirmar: título, fecha/hora, invitados, **motivo** (asunto) y **nombre del administrador**. Estado `pendiente_confirmacion` (tipo `reunion_cancelacion`) en `LOGS_COMMS.md`.
5. **Confirmación explícita** en chat («cancela la reunión», «sí, anúlala», etc.) — autoriza el envío automático del correo; no hace falta un segundo «envíalo».
6. **Ejecutar en el mismo turno**:

```bash
gog-calendar-meet-cancel.sh \
  --event-id "<ID>" \
  --reason "<motivo de cancelación>" \
  --admin-name "<nombre del administrador>"
```

(ruta en contenedor admin: `/usr/local/bin/gog-calendar-meet-cancel.sh`)

**Formato del correo enviado automáticamente:**

| Campo | Contenido |
|-------|-----------|
| **Asunto** | Motivo de cancelación (texto del admin) |
| **Cuerpo** | `La reunión ha sido cancelada.` + tab + `Atte: {nombre administrador}` |

7. **Resultado:** estado **`reunion_cancelada`** en `LOGS_COMMS.md` (incluir motivo y nombre admin en notas).

**Prohibido** `gog calendar delete` directo; **prohibido** borrador Gmail manual para este correo.

```bash
./scripts/gog-calendar-meet-cancel.sh \
  --event-id "qva7nm51inj395jnl0j85opds0" \
  --reason "Por fuerza mayor se posterga la reunión" \
  --admin-name "Joaquín Fuenzalida"
```

Si el evento ya no aparece en el listado pero debes notificar:

```bash
./scripts/gog-calendar-meet-cancel.sh \
  --event-id "…" \
  --reason "…" \
  --admin-name "…" \
  --attendees "uno@ejemplo.com,dos@ejemplo.com"
```

## Rutas admin (Docker)

| Recurso | Ruta |
|---------|------|
| `LOGS_COMMS.md` | `/app/logs_shared/LOGS_COMMS.md` |
| Borradores | `~/Documentos/Comunicaciones/borradores/` |

Columna **Agente:** `Administrador`. Puede `gog calendar update` / `delete` tras confirmación verbal (ver flujo **Cancelar reunión** arriba).

## Errores

| Error | Acción |
|-------|--------|
| `No auth for calendar` | OAuth con scope `calendar` |
| `No tokens stored` | `./scripts/gog-auth-setup.sh` |
| `403 accessNotConfigured` / API disabled | Habilitar **Google Calendar API** en Google Cloud: ver `docs/habilitar-google-calendar-api.md` (proyecto `august-victor-496423-e8`) |
| Invitados no reciben correo al crear | Falta `--send-updates all` (default de `gog` es `none`). Reenviar: `gog calendar update primary <eventId> -a "…" --send-updates all` |
| `gog calendar delete` bloqueado | Usar `gog-calendar-meet-cancel.sh --event-id … --reason … --admin-name …` |
| Cancelar sin motivo o sin nombre admin | **Prohibido.** Preguntar motivo (asunto) y nombre del administrador antes de cancelar |
