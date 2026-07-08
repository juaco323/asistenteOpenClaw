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
| 2026-06-24 UTC | Administrador | Borrador creado | prueba.openclaw.fj@gmail.com | joaquin.fuenzalida51@gmail.com | Vamos que se puede | r7653804893984176126 |
2026-06-24	Administrador	email_enviado	Hola -> fernycalderonsolis@gmail.com | draft_id: r5461441974832606174
2026-06-24	Administrador	email_enviado	Buenas noches -> f.calderonsolis@uandresbello.edu | draft_id: r-5371035708263308204
2026-06-24	Administrador	email_enviado	Hola -> fernycalderonsolis@gmail.com | draft_id: r572148225652539337
2026-06-24	Administrador	email_enviado	Hola -> f.calderonsolis@uandresbello.edu | draft_id: r-2243685304970419567
| 2026-07-07 21:31 UTC | Administrador | BORRADOR | r-9012243869463104014 | prueba.openclaw.fj@gmail.com | Reunión de proyecto | 11 destinatarios |
| 2026-07-07 21:32 UTC | Administrador | BORRADOR_ACTUALIZADO | r-5383792107160604727 | prueba.openclaw.fj@gmail.com | Reunión de proyecto | Se eliminó la frase solicitada |
| 2026-07-07 21:32 UTC | Administrador | ENVIADO | r-5383792107160604727 | prueba.openclaw.fj@gmail.com | Reunión de proyecto | Enviado a 11 destinatarios |
| 2026-07-07 21:47 UTC | Administrador | BORRADOR | r1406016027663772295 | prueba.openclaw.fj@gmail.com | Notificación formal de término de relación laboral | 11 destinatarios |
| 2026-07-07 21:50 UTC | Administrador | ENVIADO | r1406016027663772295 | prueba.openclaw.fj@gmail.com | Notificación formal de término de relación laboral | Enviado a 11 destinatarios |
| 2026-07-07 22:01 UTC | Administrador | ENVIADO | r7691786344413449212 | prueba.openclaw.fj@gmail.com | URGENTE: hotfix crítico de login — deadline lunes 08:00 | Enviado a frontend |
| 2026-07-07 22:01 UTC | Administrador | ENVIADO | r3578114410091408335 | prueba.openclaw.fj@gmail.com | Confirmación de autorización — 3 licencias de desarrollo | Enviado a papelería |
| 2026-07-07 22:01 UTC | Administrador | ENVIADO | r8694997719982013376 | prueba.openclaw.fj@gmail.com | URGENTE: backup de staging obligatorio antes de deploys de esta semana | Enviado a Bak |
| 2026-07-07 22:01 UTC | Administrador | ENVIADO | r-4675467863972188212 | prueba.openclaw.fj@gmail.com | Actualización de proyecto: ajuste de 3 días en entrega de MVP | Enviado a Pablo |
| 2026-07-07 22:12 UTC | Administrador | BORRADOR | r-7328647213700831645 | prueba.openclaw.fj@gmail.com | Proyecto Semana del Deporte - Desglose Operativo | 11 destinatarios |
| 2026-07-07 22:13 UTC | Administrador | ENVIADO | r-7328647213700831645 | prueba.openclaw.fj@gmail.com | Proyecto Semana del Deporte - Desglose Operativo | Enviado a 11 destinatarios |
| 2026-07-07 22:44 UTC | Administrador | ENVIADO | r-1319900459358766300 | prueba.openclaw.fj@gmail.com | 🔥 10 - La cuenta regresiva comienza | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:45 UTC | Administrador | ENVIADO | r4222400666438345218 | prueba.openclaw.fj@gmail.com | ⏰ 9 - Nos acercamos | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:46 UTC | Administrador | ENVIADO | r-2247797157907043078 | prueba.openclaw.fj@gmail.com | ⏳ 8 - Energía sube | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:47 UTC | Administrador | ENVIADO | r-4468134208318550501 | prueba.openclaw.fj@gmail.com | 🚀 7 - Casi aquí | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:48 UTC | Administrador | ENVIADO | r-6339058179599186528 | prueba.openclaw.fj@gmail.com | 💪 6 - La tensión aumenta | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:49 UTC | Administrador | ENVIADO | r2257416488717711954 | prueba.openclaw.fj@gmail.com | 🎯 5 - Punto medio | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:50 UTC | Administrador | ENVIADO | r-1539237796140815273 | prueba.openclaw.fj@gmail.com | ⚡ 4 - Ya casi | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:51 UTC | Administrador | ENVIADO | r-6886680962303149482 | prueba.openclaw.fj@gmail.com | 🏁 3 - En posición de salida | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:52 UTC | Administrador | ENVIADO | r-1700652037512594764 | prueba.openclaw.fj@gmail.com | 🔥 2 - No hay vuelta atrás | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:53 UTC | Administrador | ENVIADO | r-777129434531743141 | prueba.openclaw.fj@gmail.com | ⚠️ 1 - AQUÍ VAMOS | Countdown masivo a 11 destinatarios |
| 2026-07-07 22:54 UTC | Administrador | ENVIADO | r-4724670271138797009 | prueba.openclaw.fj@gmail.com | ✅ ¡Bienvenido al equipo! Semana del Deporte 2026 | Countdown masivo a 11 destinatarios |
