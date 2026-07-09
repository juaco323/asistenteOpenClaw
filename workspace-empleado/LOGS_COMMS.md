# Registro de comunicaciones administrativas

Trazabilidad de recordatorios, seguimientos, confirmaciones y reuniones gestionados con la skill **`admin-comms`**.

Pueden escribir aquí **empleado** y **administrador** (en Docker admin: `/app/logs_shared/LOGS_COMMS.md`).

## Estados

| Estado | Descripción |
|--------|-------------|
| `pendiente_confirmacion` | Borrador o propuesta lista; sin despacho externo |
| `confirmado` | Usuario autorizó envío o acción |
| `reunion_creada` | Evento Calendar + Meet creado (**solo Administrador**) |
| `reunion_cancelada` | Reunión eliminada en Calendar; invitados notificados (**solo Administrador**) |
| `reunion_zoom_creada` | Reunión Zoom creada; invitados notificados por correo (**solo Administrador**) |
| `reunion_zoom_cancelada` | Reunión Zoom eliminada; invitados notificados (**solo Administrador**) |
| `enviado` | Comunicación despachada (p. ej. correo enviado) |
| `error` | Fallo o datos insuficientes |
| `cancelado` | Usuario canceló o pospuso |

## Tipos

| Tipo | Uso |
|------|-----|
| `recordatorio` / `seguimiento` / `confirmación` | Comunicación por correo (empleado y administrador) |
| `reunion_meet` | Reunión con Google Calendar + Meet (**solo administrador**; ver `calendar-meet.md`) |
| `reunion_zoom` | Reunión Zoom (**solo administrador**; ver `zoom-meetings.md`) |
| `reunion_dual` | Propuesta única para agendar en **Meet y Zoom a la vez**; al confirmar se registran dos filas (`reunion_meet` + `reunion_zoom`), ver `SKILL.md` § *Reunión en ambas plataformas* |
| `reunion_cancelacion` / `reunion_zoom_cancelacion` | Propuesta de cancelación pendiente de confirmar |

## Tabla de comunicaciones (recordatorio / seguimiento / confirmación)

| Fecha / hora | ID | Agente | Tipo | Destinatario | Fecha ref. | Estado | Archivo borrador | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _ejemplo_ | COMMS-2026-06-20-001 | Empleado | recordatorio | ana@… | 2026-06-27 10:00 | pendiente_confirmacion | ~/Documentos/Comunicaciones/borradores/COMMS_2026-06-20_informe-ventas.md | — |

_Cada fila nueva se añade al final, manteniendo el encabezado. Si el canal es Gmail, tras envío exitoso añadir también fila en `LOGS_EMAIL.md` y entrada en `HISTORY.md` según protocolo `email-gmail`._

## Tabla de reuniones (Meet / Zoom / dual — solo Administrador)

| Fecha | Agente | Tipo | Estado | Título / Tema | Horario | Invitados | Enlace / ID | Motivo cancelación | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-24 | Administrador | reunion_meet | reunion_creada | Reunión con Ferny | 2026-06-24 16:00–17:00 America/Santiago | fernycalderonsolis@gmail.com | Meet: https://meet.google.com/odv-wioj-fow | — | — |
| 2026-06-24 | Administrador | reunion_meet | reunion_cancelada | Reunión con Ferny | 2026-06-24 16:00–17:00 America/Santiago | fernycalderonsolis@gmail.com | Meet: https://meet.google.com/odv-wioj-fow | Por fuerza mayor se cancela la reunión | Atte: Joaquín |
| 2026-06-24 | Administrador | reunion_meet | pendiente_confirmacion | Presentación | 2026-06-24 17:00–18:00 America/Santiago | fernycalderonsolis@gmail.com | — | — | — |
| 2026-06-24 | Administrador | reunion_meet | reunion_creada | Presentación | 2026-06-24 17:00–18:00 America/Santiago | fernycalderonsolis@gmail.com | Meet: https://meet.google.com/erz-pzzc-tmn | — | — |
| 2026-06-24 | Administrador | reunion_meet | reunion_cancelada | Presentación | 2026-06-24 17:00–18:00 America/Santiago | fernycalderonsolis@gmail.com | Meet: https://meet.google.com/erz-pzzc-tmn | Fuerza mayor | Atte: Joaquín F. |
| 2026-06-24 | Administrador | reunion_zoom | pendiente_confirmacion | Reunión | 2026-06-24 17:00–18:00 America/Santiago | fernycalderonsolis@gmail.com | — | — | — |
| 2026-06-24 | Administrador | reunion_zoom | reunion_zoom_creada | Reunión | 2026-06-24 17:00–18:00 America/Santiago | fernycalderonsolis@gmail.com | Zoom ID: 85487911844 — https://us05web.zoom.us/j/85487911844?pwd=ofOSOw77bQk3cCnCooEAPgDaEc0KOb.1 | — | — |
| 2026-06-24 | Administrador | reunion_zoom | reunion_zoom_cancelada | Reunión | 2026-06-24 17:00–18:00 America/Santiago | fernycalderonsolis@gmail.com | Zoom ID: 85487911844 | Fuerza mayor | Atte: Joaquín |
| 2026-06-24 | Administrador | reunion_meet | pendiente_confirmacion | Reunión Importante | 2026-06-24 19:00–20:00 America/Santiago | carla.taramasco@unab.cl, david.araya@unab.cl, joaquin.fuenzalida51@gmail.com | — | — | — |
| 2026-06-24 | Administrador | reunion_meet | reunion_creada | Reunión Importante | 2026-06-24 19:00–20:00 America/Santiago | carla.taramasco@unab.cl, david.araya@unab.cl, joaquin.fuenzalida51@gmail.com | Meet: https://meet.google.com/xqt-yokq-kse | — | — |
| 2026-06-24 | Administrador | reunion_meet | reunion_cancelada | Reunión Importante | 2026-06-24 19:00–20:00 America/Santiago | carla.taramasco@unab.cl, david.araya@unab.cl, joaquin.fuenzalida51@gmail.com | Meet: https://meet.google.com/xqt-yokq-kse | Fuerza mayor | Atte: Joaquín |
| 2026-06-25 | Administrador | reunion_dual | pendiente_confirmacion | Daily 25 de junio | 2026-06-25 20:00–21:00 America/Santiago | joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com | — | — | plataformas: Meet y Zoom; tema: entrega de landing page de esta semana |
| 2026-06-25 | Administrador | reunion_meet | reunion_creada | Daily 25 de junio | 2026-06-25 20:00–21:00 America/Santiago | joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com | Meet: https://meet.google.com/bgq-uxfa-xuj | — | tema: entrega de landing page de esta semana |
| 2026-06-25 | Administrador | reunion_zoom | reunion_zoom_creada | Daily 25 de junio | 2026-06-25 20:00–21:00 America/Santiago | joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com | Zoom ID: 82801204172 — https://us05web.zoom.us/j/82801204172?pwd=3jBbaz2W5i53R3ZvszY034CG0d5Zt3.1 | — | tema: entrega de landing page de esta semana |

_Cada fila nueva se añade al final de la tabla que corresponda, manteniendo el encabezado. No agregar filas sueltas fuera de una tabla: rompe la trazabilidad y el renderizado Markdown._
