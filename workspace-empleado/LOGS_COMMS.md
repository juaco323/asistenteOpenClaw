# Registro de comunicaciones administrativas

Trazabilidad de recordatorios, seguimientos y confirmaciones gestionados con la skill **`admin-comms`**.

Pueden escribir aquí **empleado** y **administrador** (en Docker admin: `/app/logs_shared/LOGS_COMMS.md`).

## Estados

| Estado | Descripción |
|--------|-------------|
| `pendiente_confirmacion` | Borrador listo; sin despacho externo |
| `confirmado` | Usuario autorizó envío o acción |
| `reunion_creada` | Evento Calendar + Meet creado (**solo Administrador**) |
| `reunion_cancelada` | Reunión eliminada en Calendar; invitados notificados (**solo Administrador**) |
| `reunion_zoom_creada` | Reunión Zoom creada; invitados notificados por correo (**solo Administrador**) |
| `reunion_zoom_cancelada` | Reunión Zoom eliminada; invitados notificados (**solo Administrador**) |
| `enviado` | Comunicación despachada (p. ej. correo enviado) |
| `error` | Fallo o datos insuficientes |
| `cancelado` | Usuario canceló o pospuso |

## Tabla operativa

| Fecha / hora | ID | Agente | Tipo | Destinatario | Fecha ref. | Estado | Meet / Event ID | Archivo borrador | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _ejemplo admin_ | COMMS-2026-06-20-001 | Administrador | reunion_meet | a@… | 2026-06-27 10:00 | reunion_creada | meet.google.com/… | ~/Documentos/Comunicaciones/… | Solo perfil admin crea Meet |

_Cada fila nueva se añade al final, manteniendo el encabezado._

## Relación con correo

Si el canal es Gmail, tras envío exitoso añadir también fila en `LOGS_EMAIL.md` y entrada en `HISTORY.md` según protocolo `email-gmail`.
2026-06-24	Administrador	reunion_meet	reunion_creada	Reunión con Ferny | 2026-06-24 16:00-17:00 America/Santiago | Meet: https://meet.google.com/odv-wioj-fow | invitados: fernycalderonsolis@gmail.com
2026-06-24	Administrador	reunion_meet	reunion_cancelada	Reunión con Ferny | 2026-06-24 16:00-17:00 America/Santiago | motivo: Por fuerza mayor se cancela la reunion, gracias | Atte: Joaquin
2026-06-24	Administrador	reunion_meet	pendiente_confirmacion	Presentacion | 2026-06-24 17:00-18:00 America/Santiago | invitados: fernycalderonsolis@gmail.com
2026-06-24	Administrador	reunion_meet	reunion_creada	Presentacion | 2026-06-24 17:00-18:00 America/Santiago | Meet: https://meet.google.com/erz-pzzc-tmn | invitados: fernycalderonsolis@gmail.com
2026-06-24	Administrador	reunion_meet	reunion_cancelada	Presentacion | 2026-06-24 17:00-18:00 America/Santiago | motivo: Fuerza mayor | Atte: Joaquin f
2026-06-24	Administrador	reunion_zoom	pendiente_confirmacion	Reunion | 2026-06-24 17:00-18:00 America/Santiago | invitados: fernycalderonsolis@gmail.com
2026-06-24	Administrador	reunion_zoom	reunion_zoom_creada	Reunion | 2026-06-24 17:00-18:00 America/Santiago | Zoom ID: 85487911844 | Link: https://us05web.zoom.us/j/85487911844?pwd=ofOSOw77bQk3cCnCooEAPgDaEc0KOb.1 | invitados: fernycalderonsolis@gmail.com
2026-06-24	Administrador	reunion_zoom	reunion_zoom_cancelada	Reunion | 2026-06-24 17:00-18:00 America/Santiago | motivo: fuerza mayor | Atte: joaquin
2026-06-24	Administrador	reunion_meet	pendiente_confirmacion	Reunión Importante | 2026-06-24 19:00-20:00 America/Santiago | invitados: carla.taramasco@unab.cl, david.araya@unab.cl, joaquin.fuenzalida51@gmail.com
2026-06-24	Administrador	reunion_meet	reunion_creada	Reunión Importante | 2026-06-24 19:00-20:00 America/Santiago | Meet: https://meet.google.com/xqt-yokq-kse | invitados: carla.taramasco@unab.cl, david.araya@unab.cl, joaquin.fuenzalida51@gmail.com
2026-06-24	Administrador	reunion_meet	reunion_cancelada	Reunión Importante | 2026-06-24 19:00-20:00 America/Santiago | motivo: Fuerza mayor | Atte: joaquin
