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
| 2026-05-16 04:40 UTC | Empleado | Borrador creado | prueba.openclaw.fj@gmail.com | javiera.fuenzalidacor@gmail.com | Anda a acostarse | r-7019018653990607968 |
| 2026-05-16 04:41 UTC | Empleado | Correo enviado | prueba.openclaw.fj@gmail.com | javiera.fuenzalidacor@gmail.com | Anda a acostarse | r-7019018653990607968 |
| 2026-05-16 04:45 UTC | Empleado | Borrador creado | prueba.openclaw.fj@gmail.com | acv1324@gmail.com | Anda a acostarte doria | r1173223262428002199 |
| 2026-05-16 04:46 UTC | Empleado | Borrador creado | prueba.openclaw.fj@gmail.com | acv1324@gmail.com | Anda a acostarte, Doria | r8363244273495347858 |
| 2026-05-16 04:46 UTC | Empleado | Correo enviado | prueba.openclaw.fj@gmail.com | acv1324@gmail.com | Anda a acostarte, Doria | r8363244273495347858 |
| 2026-05-16 04:50 UTC | Empleado | Borrador creado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | test | r627174621781871500 |
| 2026-05-16 04:51 UTC | Empleado | Correo enviado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | test | r627174621781871500 |
| 2026-05-25 17:28 UTC | Administrador | Borrador creado | prueba.openclaw.fj@gmail.com | fernycalderonsolis@gmail.com | Recordatorio: jugar hoy Valorant a las 10 PM | r-6480057617700128976 |
| 2026-05-25 17:28 UTC | Administrador | Correo enviado | prueba.openclaw.fj@gmail.com | fernycalderonsolis@gmail.com | Recordatorio: jugar hoy Valorant a las 10 PM | r-6480057617700128976 |
| 2026-05-25 17:33 UTC | Administrador | Borrador creado | prueba.openclaw.fj@gmail.com | fernycalderonsolis@gmail.com | Recordatorio: jugar hoy Valorant a las 10 PM | r-4183869581734308442 |
| 2026-05-25 17:33 UTC | Administrador | Correo enviado | prueba.openclaw.fj@gmail.com | fernycalderonsolis@gmail.com | Recordatorio: jugar hoy Valorant a las 10 PM | r-4183869581734308442 |
| 2026-05-25 17:34 UTC | Administrador | Borrador creado | prueba.openclaw.fj@gmail.com | fernycalderonsolis@gmail.com | Recordatorio: jugar hoy Valorant a las 10 PM | r-3360170560771289710 |
| 2026-05-25 17:34 UTC | Administrador | Correo enviado | prueba.openclaw.fj@gmail.com | fernycalderonsolis@gmail.com | Recordatorio: jugar hoy Valorant a las 10 PM | r-3360170560771289710 |
| 2026-05-25 18:00 UTC | Administrador | Borrador creado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | Recordatorio: reunión mañana a las 4 PM | r5412524415607206701 |
| 2026-05-25 18:02 UTC | Administrador | Correo enviado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | Recordatorio: reunión mañana a las 4 PM | r5412524415607206701 |
| 2026-05-25 | Administrador | BORRADOR | joaquin.fuenzalida51@gmail.com | Recordatorio reunión mañana | r4912418844213010512 |
| 2026-05-25 | Administrador | ENVIADO | joaquin.fuenzalida51@gmail.com | Recordatorio reunión mañana | 19e60543145d4788 |
| 2026-05-25 | Administrador | BORRADOR | joaquin.fuenzalida51@gmail.com | Recordatorio reunión mañana | r5738080128564405249 |
| 2026-05-25 | Administrador | ENVIADO | joaquin.fuenzalida51@gmail.com | Recordatorio reunión mañana | 19e606b364b17f8c |
| 2026-05-25 | Administrador | BORRADOR | carla.taramasco@unab.cl | Recordatorio reunión mañana | r513061347335142387 |
| 2026-05-25 | Administrador | ENVIADO | carla.taramasco@unab.cl | Recordatorio reunión mañana | 19e606d281eb787c |
- 2026-06-15 23:13 UTC | Administrador | Enviado | Draft ID: r5784576001265582332 | Para: joaquin.fuenzalida51@gmail.com | Asunto: Recordatorio: prueba de infraestructura TI el miércoles 1 a las 8:30 AM
