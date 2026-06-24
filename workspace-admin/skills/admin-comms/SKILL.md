# Skill: Gestión de comunicaciones y recordatorios (`admin-comms`)

Actúa como gestor de comunicaciones administrativas: recordatorios, seguimientos y confirmaciones hacia terceros, con **confirmación humana obligatoria** antes de cualquier envío externo.

**Workspace:** `workspace-admin`.

## Cuándo usarla

Igual que en empleado: recordatorios, seguimientos, confirmaciones y mensajes formales con validación de entidades.

El administrador puede además registrar comunicaciones críticas en `memory/YYYY-MM-DD.md` si afectan operación o despliegue.

## Tipos, entidades y estados

Ver `workspace-empleado/skills/admin-comms/SKILL.md` (misma semántica). Estados: `pendiente_confirmacion`, `confirmado`, `enviado`, `error`, `cancelado`.

## Rutas de registro (admin)

| Archivo | Ruta en contenedor admin |
|---------|--------------------------|
| `LOGS_COMMS.md` | `/app/logs_shared/LOGS_COMMS.md` (equivale a `workspace-empleado/LOGS_COMMS.md` en el repo) |
| `LOGS_EMAIL.md` | `/app/logs_shared/LOGS_EMAIL.md` |
| `HISTORY.md` | `/app/logs_shared/HISTORY.md` |
| Borradores | `~/Documentos/Comunicaciones/borradores/` |

Columna **Agente** en tablas: `Administrador`.

## Flujo resumido

1. Extraer destinatario, fecha, responsable, acción pendiente.
2. Redactar asunto y cuerpo (español profesional).
3. Guardar `COMMS-*.md` y registrar **`pendiente_confirmacion`**.
4. Presentar borrador **una vez**; **no enviar** sin confirmación.
5. Si confirma correo → `email-gmail` → actualizar estados y logs compartidos.

## Reuniones Google Meet + Calendar

**Exclusivo perfil Administrador** (Telegram y Control UI `:18791`). Calendar/Meet: `calendar-meet.md`. Zoom: `zoom-meetings.md`. Cancelar: motivo + **nombre para Atte** (preguntar si falta) + confirmación → script correspondiente (`gog-calendar-meet-cancel.sh` o `zoom-meeting-cancel.sh`).

El perfil empleado **no** ejecuta `gog calendar`; solo redacta recordatorios por correo.

## Referencias

| Recurso | Ruta |
|---------|------|
| Skill detallada (empleado, misma lógica) | `skills/admin-comms/SKILL.md` |
| Plantilla | `skills/admin-comms/draft-template.md` |
| Guía | `docs/gestion-comunicaciones.md` |
