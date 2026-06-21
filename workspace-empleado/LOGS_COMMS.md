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
2026-06-20	Administrador	reunion_meet	pendiente_confirmacion	MundoPokeDs | 2026-06-21 19:00-20:00 America/Santiago | invitados: joaquin.fuenzalida51@gmail.com, javiera.fuenzalidacor@gmail.com
2026-06-21	Administrador	reunion_meet	pendiente_confirmacion	MundoPokeDs | 2026-06-21 19:00-20:00 America/Santiago | invitados: joaquin.fuenzalida51@gmail.com, javiera.fuenzalidacor@gmail.com, fernycalderonsolis@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_creada	MundoPokeDs | 2026-06-21 19:00-20:00 America/Santiago | Meet: https://meet.google.com/nfh-qddm-sua | invitados: joaquin.fuenzalida51@gmail.com, javiera.fuenzalidacor@gmail.com, fernycalderonsolis@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_cancelada	MundoPokeDs | 2026-06-21 19:00-20:00 America/Santiago | motivo: Se suspende por motivos de fuerza mayor, saludos
2026-06-21	Administrador	reunion_meet	pendiente_confirmacion	Reunion importante | 2026-06-21 12:30-13:30 America/Santiago | invitados: joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com, javiera.fuenzalidacor@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_cancelada	Reunion importante | 2026-06-21 12:23-13:23 America/Santiago | motivo: Por motivos de fuerza mayor, tendre que cancelar la reunion.
2026-06-21	Administrador	reunion_meet	pendiente_confirmacion	Reunion importante? | 2026-06-21 13:00-14:00 America/Santiago | invitados: joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com, javiera.fuenzalidacor@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_creada	Reunion importante? | 2026-06-21 13:00-14:00 America/Santiago | Meet: https://meet.google.com/twk-rijf-gng | invitados: joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com, javiera.fuenzalidacor@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_cancelada	Reunion importante? | 2026-06-21 13:00-14:00 America/Santiago | motivo: Por motivos de fuerza mayor se posterga la reunion, gracias.
2026-06-21	Administrador	reunion_meet	pendiente_confirmacion	reunion | 2026-06-21 13:00-14:00 America/Santiago | invitados: joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com, javiera.fuenzalidacor@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_creada	reunion | 2026-06-21 13:00-14:00 America/Santiago | Meet: https://meet.google.com/cnq-sjmr-rdo | invitados: joaquin.fuenzalida51@gmail.com, fernycalderonsolis@gmail.com, javiera.fuenzalidacor@gmail.com
2026-06-21	Administrador	reunion_meet	reunion_cancelada	reunion | 2026-06-21 13:00-14:00 America/Santiago | motivo: Por fuerza mayor debo de cancelar la reunion, saludos
