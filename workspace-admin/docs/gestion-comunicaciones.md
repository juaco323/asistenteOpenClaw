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

Estado `reunion_creada` + Meet link (requiere OAuth `calendar`).

### Prueba C — Enviar link por correo

```
Envía por correo el link de la reunión
```

Flujo `email-gmail` separado.

```bash
./scripts/gog-auth-setup.sh
./scripts/gog-calendar-meet-create.sh --dry-run --summary "…" --from "…" --to "…"
```

Skill Meet: [`skills/admin-comms/calendar-meet.md`](skills/admin-comms/calendar-meet.md)

## Telegram

1. `/workspace admin` → contraseña → `/comunicaciones`
2. Pedir recordatorio o reunión con Meet (ejemplos de arriba)
3. Confirmar en chat: «agéndala», «envíalo», etc.

También funciona en `/chat` (el bot inyecta el protocolo `admin-comms` en cada mensaje).
