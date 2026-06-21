# Gestión de comunicaciones — perfil administrador

Incluye **`admin-comms`** + **Google Calendar / Meet** (exclusivo de este perfil).

## Recordatorios (igual que empleado)

Ver ejemplos en `workspace-empleado/docs/gestion-comunicaciones.md`.

## Google Calendar + Meet (solo admin)

### Prueba A — Propuesta

```
Agenda reunión de seguimiento OpenClaw el viernes 27/06/2026 a las 10:00, 
1 hora, con Meet. Invitados: carla.taramasco@unab.cl
```

Estado `pendiente_confirmacion`, **sin** `gog calendar create`.

### Prueba B — Crear tras confirmar

```
Confirma y créala en el calendario
```

Estado `reunion_creada` + Meet link (requiere OAuth `calendar`). Con invitados, el comando debe incluir **`--send-updates all`** para que llegue la invitación por correo al crear (el default de `gog` es `none`).

### Prueba C — Enviar link por correo

```
Envía por correo el link de la reunión
```

Flujo `email-gmail` separado.

### Prueba D — Cancelar reunión

```
Cancela la reunión MundoPokeDs del 21 de junio
```

1. El asistente **pregunta el motivo** (asunto del correo) y el **nombre del administrador** si no los diste.
2. Resumen (título, invitados, motivo, nombre admin) → confirmación («sí, cancela»).
3. Ejecuta `gog-calendar-meet-cancel.sh --event-id … --reason … --admin-name …`.
4. Correo: **asunto** = motivo; **cuerpo** = «La reunión ha sido cancelada.» + `Atte: {nombre}`.

```bash
./scripts/gog-auth-setup.sh
./scripts/gog-calendar-meet-create.sh --dry-run --summary "…" --from "…" --to "…"
./scripts/gog-calendar-meet-cancel.sh --dry-run --event-id "…" --reason "Motivo de prueba" --admin-name "Nombre Admin"
```

Skill Meet: [`skills/admin-comms/calendar-meet.md`](skills/admin-comms/calendar-meet.md)

## Telegram

1. `/workspace admin` → contraseña → `/comunicaciones`
2. Pedir recordatorio, **crear** reunión con Meet o **cancelar** reunión (ejemplos de arriba)
3. Confirmar en chat: «agéndala», «cancela la reunión», «envíalo», etc.

## Control UI (gateway web)

Mismo protocolo en `http://127.0.0.1:18791/` (admin). Empleado (`:18790`) **no** crea ni cancela reuniones.
