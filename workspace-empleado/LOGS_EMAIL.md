# Historial unificado de auditoría de correo (operativo)

Registro **tabular** de acciones Gmail realizadas vía `gog`. Pueden escribir aquí el agente **empleado** y el **administrador** (en Docker admin: `/app/logs_shared/LOGS_EMAIL.md`). El agente **administrador** indica **`Administrador`** en la columna «Agente».

| Fecha / hora (local) | Agente | Acción | Destinatario | Cuenta (-a) | Draft / msg ID | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| _— ejemplo —_ | Empleado | `DRAFT_CREATION` | cliente@empresa.com | prueba.openclaw.fj@gmail.com | _rfc822msgid / draft id_ | Pendiente confirmación humana |

## Convenciones de `Acción`

- `DRAFT_CREATION` — se creó borrador; aún no hay envío.
- `EMAIL_SENT` — borrador enviado tras confirmación explícita.
- `AUTH_CHECK` — comprobación de conectividad (opcional; suele quedar también en `HISTORY.md`).
- `ERROR` — fallo reproducible (sin pegar secretos ni tokens).

_Cada fila nueva se añade al final de la tabla, manteniendo el encabezado._
| 2026-05-16 01:46 UTC | Administrador | Borrador creado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | Notificación de término de relación laboral - 16 de mayo de 2026 | r-44852255659138362 |
| 2026-05-16 01:48 UTC | Administrador | Correo enviado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | Notificación de término de relación laboral - 16 de mayo de 2026 | r-44852255659138362 |
