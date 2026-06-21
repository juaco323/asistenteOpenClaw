# Gestión de comunicaciones y recordatorios

Guía para probar la skill **`admin-comms`** (recordatorios, seguimientos, confirmaciones).

## Qué hace el asistente

1. Extrae **destinatario**, **fecha**, **responsable** y **acción pendiente** de tu solicitud.
2. Redacta un borrador **profesional** (asunto + cuerpo).
3. Guarda el borrador en `~/Documentos/Comunicaciones/borradores/`.
4. Registra el estado en `LOGS_COMMS.md` como **`pendiente_confirmacion`**.
5. **No envía** nada hasta que confirmes explícitamente.

## Ejemplos de solicitud

### Escenario 1 — Recordatorio de reunión

```
Redacta un recordatorio para carla.taramasco@unab.cl sobre la reunión de seguimiento del proyecto OpenClaw el viernes 27 a las 10:00. Responsable: Joaquín.
```

**Resultado esperado:** borrador formal, estado `pendiente_confirmacion`, archivo `.md` en Comunicaciones.

### Escenario 2 — Sin confirmación

Tras ver el borrador, responde «déjalo guardado» o no digas «envíalo».

**Resultado esperado:** sin `gog`, sin envío; borrador conservado para editar después.

### Envío por correo (opcional, tras OAuth Gmail)

Cuando el borrador te convenga:

```
Envíalo por correo
```

El asistente creará borrador Gmail (`gog`) y, tras tu confirmación coloquial, enviará según `email-gmail`.

## Telegram

1. `/workspace empleado` → contraseña → `/comunicaciones` (o `/chat`)
2. Envía el recordatorio en lenguaje natural
3. Confirma o deja pendiente en el mismo chat

**Meet / Calendar:** no disponible en empleado (crear ni cancelar); usa `/workspace admin` + `/comunicaciones` o Control UI `:18791`.

## Dónde revisar

| Recurso | Ubicación |
|---------|-----------|
| Borradores | `~/Documentos/Comunicaciones/borradores/` |
| Estados | `workspace-empleado/LOGS_COMMS.md` |
| Skill | `workspace-empleado/skills/admin-comms/SKILL.md` |

## Criterios de aceptación cubiertos

- Redacción desde contexto mínimo
- Extracción y validación de entidades
- Confirmación explícita antes de envío
- Estados: borrador / pendiente / confirmado / enviado / error
- Tono profesional y editable antes de procesar

## Google Meet / Calendar

**No disponible en perfil empleado.** Para agendar reuniones con Meet, usa el **perfil Administrador** (`workspace-admin`).
