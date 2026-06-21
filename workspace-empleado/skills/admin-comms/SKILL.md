# Skill: Gestión de comunicaciones y recordatorios (`admin-comms`)

Actúa como gestor de comunicaciones administrativas: recordatorios, seguimientos y confirmaciones hacia terceros, con **confirmación humana obligatoria** antes de cualquier envío externo.

**Workspace:** `workspace-empleado`.

## Cuándo usarla

Activa esta skill cuando el usuario pida, de forma explícita o implícita:

- redactar un **recordatorio**, **seguimiento** o **confirmación**;
- preparar un mensaje formal para reunión, entrega, plazo o cliente;
- gestionar comunicaciones administrativas sin olvidar validar datos clave;
- escenarios «recordatorio de reunión de seguimiento», «seguimiento a cliente», «confirmar asistencia».

**No sustituye** `email-gmail`: si el canal es correo, esta skill prepara el contenido y el estado; el envío real sigue el protocolo Gmail (borrador `gog` → confirmación → `drafts send`).

**Google Calendar / Meet:** **prohibido** en perfil empleado. Si el usuario pide agendar reunión con Meet o crear evento en calendario, indica que esa capacidad es **solo del perfil Administrador** y ofrece redactar el **recordatorio por correo** (texto con fecha/hora) con esta misma skill.

## Tipos de comunicación

| Tipo | Uso |
|------|-----|
| `recordatorio` | Avisar fecha, hora o plazo próximo |
| `seguimiento` | Retomar tema pendiente, solicitar actualización |
| `confirmación` | Confirmar asistencia, recepción o acuerdos |

**No aplica en empleado:** tipo `reunion_meet` (solo administrador).

## Extracción de entidades (obligatorio)

Antes de redactar, identifica y valida:

1. **Destinatario(s)** — nombre y/o correo; si falta, **pregunta una vez**.
2. **Fecha / plazo** — reunión, vencimiento o «mañana a las 16:00»; normaliza a texto claro.
3. **Responsable(s)** — quién convoca, ejecuta o debe responder.
4. **Acción pendiente** — qué se espera del destinatario.
5. **Contexto** — reunión, proyecto, referencia previa.

Si falta **destinatario** o **propósito del mensaje**, **no generes borrador final**: indica qué falta y ofrece un ejemplo de frase mínima.

## Flujo de trabajo

1. **Leer** `skills/admin-comms/draft-template.md`.
2. **Clasificar** tipo (recordatorio / seguimiento / confirmación).
3. **Extraer entidades** y mostrar tabla breve al usuario si hubo ambigüedad.
4. **Redactar** asunto y cuerpo en **español profesional** (claro, cortés, sin jerga innecesaria).
5. **Asignar ID** `COMMS-YYYY-MM-DD-NNN` (NNN secuencial del día o timestamp corto).
6. **Guardar** borrador en:
   - `~/Documentos/Comunicaciones/borradores/COMMS_<fecha>_<tema-corto>.md` (crear carpetas si no existen).
7. **Registrar** fila en `LOGS_COMMS.md` con estado **`pendiente_confirmacion`**.
8. **Presentar** al usuario **una sola vez**: entidades, asunto, cuerpo, ID, ruta del archivo, estado.
9. **Detener** y esperar instrucción.

### Si el usuario confirma envío por correo

Frases válidas: «envíalo», «mándalo», «vale», «confirmo», «procede», etc.

1. Actualizar estado a **`confirmado`** en `LOGS_COMMS.md`.
2. Ejecutar protocolo **`email-gmail`**: crear borrador `gog gmail drafts create` con `-a "prueba.openclaw.fj@gmail.com"`.
3. Tras confirmación de envío del borrador Gmail (mismo turno o siguiente según `AGENTS.md`), estado **`enviado`** + fila en `LOGS_EMAIL.md` y `HISTORY.md`.
4. Si `gog` falla: estado **`error`** en `LOGS_COMMS.md` con causa breve (sin secretos).

### Si el usuario NO confirma (Escenario 2)

- Mantener borrador en disco y estado **`pendiente_confirmacion`**.
- **Prohibido** `gog gmail send`, `drafts send` o cualquier despacho externo.
- Ofrecer edición: «¿Quieres cambiar el tono, la fecha o el destinatario?»

### Cancelación

«cancela», «no lo mandes», «espera» → estado **`cancelado`**; no enviar.

## Estados permitidos

| Estado | Significado |
|--------|-------------|
| `pendiente_confirmacion` | Borrador listo; esperando usuario |
| `confirmado` | Usuario autorizó; en proceso de envío |
| `enviado` | Despachado (p. ej. correo enviado) |
| `error` | Fallo o datos insuficientes tras intento |
| `cancelado` | Usuario rechazó o pospuso |

## Personalización de tono

- Por defecto: **formal-profesional** (usted, saludo y cierre estándar).
- Si el usuario pide «más cercano» o «más breve», ajusta y **regenera el archivo** de borrador; nuevo estado `pendiente_confirmacion`.
- Siempre permitir edición manual antes de confirmar.

## Formato de respuesta en chat

```text
## Comunicación preparada — COMMS-YYYY-MM-DD-NNN

**Tipo:** recordatorio | seguimiento | confirmación
**Estado:** pendiente_confirmacion
**Destinatario:** …
**Fecha / plazo:** …
**Archivo:** ~/Documentos/Comunicaciones/borradores/…

### Asunto
…

### Cuerpo
…

Revísalo y dime si lo envío por correo, quieres cambios o cancelas.
```

## Referencias

| Recurso | Ruta |
|---------|------|
| Registro de estados | `LOGS_COMMS.md` |
| Plantilla borrador | `skills/admin-comms/draft-template.md` |
| Envío correo | `skills/email-gmail/SKILL.md` + `AGENTS.md` § Email |
| Guía usuario | `docs/gestion-comunicaciones.md` |
