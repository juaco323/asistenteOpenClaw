# Skill: Gmail mediante GOG CLI

> **Línea roja:** Solo **`prueba.openclaw.fj@gmail.com`** para Gmail y OAuth del proyecto. **No** mencionar ni usar **ninguna otra** dirección (ni personal ni histórica); **`-a` obligatorio** en todos los `gog gmail …`. En el chat **no** cites direcciones distintas de la cuenta de pruebas.

Esta skill define cómo usar la CLI [`gog`](https://gogcli.sh/) (Google Workspace en terminal) para Gmail con OAuth 2.0 y llavero local, sin exponer secretos en el chat.

## Cuenta y credenciales de este proyecto (obligatorio)

- **Única cuenta remitente** salvo orden explícita distinta del usuario: **`prueba.openclaw.fj@gmail.com`**.
- En **cada** comando `gog gmail …` usar **siempre** `-a "prueba.openclaw.fj@gmail.com"`. **No** confiar en la cuenta marcada como `default` en `gog auth list` (puede ser un correo personal) y **no** usar cuentas ajenas a la de pruebas sin instrucción escrita del usuario.
- **JSON de cliente OAuth** en Descargas: **`$HOME/Descargas/prueba_openclaw.fj.json`** (si en el disco aún existe solo `prueba_openclaw_fj.json`, es equivalente; unificar el nombre al acordado).

## Cuándo usarla

- Crear borradores, listar borradores o **enviar** solo tras confirmación explícita del usuario.
- **Empleado:** ver `workspace-empleado/AGENTS.md`; trazas en `workspace-empleado/LOGS_EMAIL.md` y `HISTORY.md`.
- **Administrador:** ver `workspace-admin/AGENTS.md` (mismo flujo borrador → confirmación → `drafts send`). En contenedor **admin**, las trazas compartidas van en **`/app/logs_shared/LOGS_EMAIL.md`** y **`/app/logs_shared/HISTORY.md`** (mismos archivos que `workspace-empleado/` en el repo); en la tabla, columna agente: **`Administrador`**.

## Coherencia host ↔ Docker

El contenedor usa `GOG_KEYRING_BACKEND=file` y `GOG_KEYRING_PASSWORD` (definido en `docker/*/ .env`). Para que los tokens creados en tu **terminal Ubuntu** sean los mismos que ve el contenedor, ejecuta los comandos de `gog auth …` en el host con **las mismas** variables:

```bash
export GOG_KEYRING_BACKEND=file
export GOG_KEYRING_PASSWORD='la misma clave que en docker/empleado/.env y docker/admin/.env'
```

Luego `gog auth credentials set …` y `gog auth add prueba.openclaw.fj@gmail.com --services gmail`.

## Comandos permitidos (sintaxis verificada; `gog` v0.16.x)

**Registrar credenciales de cliente OAuth** (una vez por máquina / llavero; en terminal del host):

```bash
gog auth credentials set "$HOME/Descargas/prueba_openclaw.fj.json"
```

**Autorizar la cuenta Gmail** (flujo interactivo en terminal del host):

```bash
gog auth add prueba.openclaw.fj@gmail.com --services gmail
```

**Diagnóstico de sesión** (solo comprobación; **no** elegir remitente según la columna default):

```bash
gog auth list
```

**Formato del cuerpo (obligatorio):** el correo debe leerse como texto formal normal en Gmail. **Prohibido** en `--body`:
- secuencias literales `\n`, `\r`, `\t` (provocan «Hola,\n\n…» en el mensaje recibido);
- prefijo `$` u otros restos de shell/heredoc al inicio del texto.

Para **cualquier** mensaje con más de una línea o párrafos, usar **`--body-file`** (o el script `scripts/gog-gmail-draft.sh`) con saltos de línea **reales** en el archivo, no escapes.

**Crear borrador** (paso obligatorio antes de un envío nuevo):

```bash
# Cuerpo de una sola línea (sin párrafos):
gog gmail drafts create -a "prueba.openclaw.fj@gmail.com" --to "destinatario@dominio.com" --subject "Asunto" --body "Cuerpo en una línea"

# Cuerpo con párrafos (recomendado):
BODY="$(mktemp)"
cat >"$BODY" <<'EOF'
Estimado/a,

Le escribo para confirmar la reunión de hoy a las 22:00.

Saludos cordiales.
EOF
gog gmail drafts create -a "prueba.openclaw.fj@gmail.com" \
  --to "destinatario@dominio.com" --subject "Asunto" --body-file "$BODY"
rm -f "$BODY"

# O desde stdin:
gog gmail drafts create -a "prueba.openclaw.fj@gmail.com" \
  --to "destinatario@dominio.com" --subject "Asunto" --body-file - <<'EOF'
Estimado/a,

Mensaje con párrafos reales.

Saludos cordiales.
EOF
```

**Borrador con adjunto(s)** — flag repetible `--attach` con **ruta absoluta** accesible desde donde ejecuta `gog` (en Docker del gateway suele coincidir con la del host si el home está montado igual). Ejemplo:

```bash
gog gmail drafts create -a "prueba.openclaw.fj@gmail.com" --to "destinatario@dominio.com" --subject "Asunto" --body "Cuerpo" --attach "/ruta/al/archivo.pdf" --attach "/ruta/al/otro.png"
```

Desde **Telegram**, los documentos o fotos que envía el usuario en `/chat` el bot los guarda bajo `Documentos/telegram-openclaw-incoming/` (respecto a `TELEGRAM_HOST_HOME`); usa esa ruta absoluta en `--attach`.

**Listar borradores**:

```bash
gog gmail drafts list -a "prueba.openclaw.fj@gmail.com"
```

## Consultar bandeja — recibidos **y** enviados/respondidos (obligatorio)

Cuando el usuario pida ver correos, la bandeja, mensajes recientes, **mensajes respondidos**, **enviados**, historial de Gmail o equivalente («¿qué correos tengo?», «muéstrame los respondidos», «últimos emails», etc.):

1. **Ejecuta siempre dos consultas** (salvo que pida **explícitamente** solo recibidos o solo enviados):
   - **Recibidos:** `gog gmail search "in:inbox" -a "prueba.openclaw.fj@gmail.com" --max 10 --plain`
   - **Enviados / respondidos:** `gog gmail search "in:sent" -a "prueba.openclaw.fj@gmail.com" --max 10 --plain`
2. **Presenta dos secciones claras** en el chat: `### Recibidos` y `### Enviados / respondidos`. Por cada fila resume fecha, remitente/destinatario (según columna FROM), asunto e ID.
3. **Prohibido** responder solo con `in:inbox` si el usuario menciona respondidos, enviados, salida o historial de correos salientes.
4. Si el usuario pide **solo respondidos/enviados**, usa `in:sent` (opcionalmente acotar: `in:sent newer_than:7d`, `from:prueba.openclaw.fj@gmail.com`).
5. **Hilos con varias partes:** si la columna THREAD indica `[N msgs]`, puedes ampliar con `gog gmail thread get <threadId> -a "prueba.openclaw.fj@gmail.com" --plain` para mostrar la conversación completa (incluye respuestas).
6. **Trazas locales complementarias** (no sustituyen la bandeja Gmail): leer `LOGS_EMAIL.md` y `HISTORY.md` (admin: `/app/logs_shared/…`) y mencionar envíos registrados por el agente (`EMAIL_SENT`, «Correo enviado») si aportan contexto.

Ejemplo de consulta acotada:

```bash
gog gmail search "in:inbox is:unread" -a "prueba.openclaw.fj@gmail.com" --max 5 --plain
gog gmail search "in:sent newer_than:14d" -a "prueba.openclaw.fj@gmail.com" --max 5 --plain
```

## Confirmación de envío — lenguaje natural (es obligatorio aplicarla)

Si ya mostraste al usuario **asunto**, **cuerpo** e **ID de borrador**, una respuesta posterior que **aprueba enviar ese borrador** en español coloquial es confirmación suficiente. Ejemplos no exhaustivos: «envíalo», «enviar», «mándalo», «mandalo», «hazlo», «procede», «adelante», «sí», «vale», «ok», «de acuerdo», «confirmo», «dale», «que lo mandes», «sí mándalo», etc.

**Conducta:**

- Ejecutar en el mismo turno `gog gmail drafts send "DRAFT_ID"`; **prohibido** tras «envíalo» / equivalentes volver a pegar **asunto o cuerpo enteros** (el usuario ya los vio). Respuesta breve: resultado del comando + ID (y trazas si aplicas).
- **Excepción:** solo si el usuario pide explícitamente «muéstrame otra vez el borrador» o «repítelo», puedes reproducir asunto/cuerpo.
- Si varios borradores están «activos» y el mensaje es ambiguo, pregunta qué **`DRAFT_ID`** enviar antes de lanzar `drafts send`.
- Cancelación u objeción («no mandes», «cancela», «espera») **no** dispara envío.

**Excepción — correo de motivo al cancelar reunión (solo Administrador):** si el usuario ya confirmó la cancelación con motivo, ejecuta en el mismo turno:
- **Google Calendar/Meet:** `scripts/gog-calendar-meet-cancel.sh`
- **Zoom:** `scripts/zoom-meeting-cancel.sh`

Esos scripts envían el Gmail **automáticamente** (`drafts create` + `drafts send`). **No** muestres borrador ni pidas «envíalo» para esos correos.

**Enviar un borrador existente** (solo tras confirmación inequívoca en el chat):

```bash
gog gmail drafts send "DRAFT_ID" -a "prueba.openclaw.fj@gmail.com"
```

`DRAFT_ID` es el identificador devuelto por la API al crear el borrador (mostrarlo siempre en el chat antes de enviar).

## Comandos prohibidos en flujo asistido

- **`gog gmail send`** como sustituto del flujo borrador + confirmación para mensajes nuevos solicitados por el usuario.
- Cualquier flag que evite confirmación humana para un envío real (`--force` donde aplique a envíos destructivos, `--no-input` para sortear al usuario en entorno asistido, etc.), salvo instrucción explícita contraria del propietario del sistema.

## Variables de entorno relevantes (Docker / servidor)

- `GOG_KEYRING_BACKEND=file`
- `GOG_KEYRING_PASSWORD` — definida en `docker/*/ .env` del host; **no** commitear.
- `GOG_ACCOUNT` (opcional) — cuenta por defecto si el entorno la fija.

Montaje típico en Docker: el directorio **`~/.config/gogcli`** del host (credenciales OAuth, `config.json`, carpeta `keyring/`) se monta en **`/home/node/.config/gogcli`** dentro del contenedor. **No** usar `~/.config/gog` para esto: `gog` lee y escribe bajo **`gogcli`**.

## Seguridad

- **No** solicitar ni aceptar contraseñas de Google, refresh tokens pegados en chat ni contenido completo del JSON de cliente.
- Si falla la autenticación, indicar que la usuaria debe ejecutar `gog auth add` / `gog auth credentials set` **en su terminal Ubuntu**, sin reintentos automáticos encadenados desde el agente.

## Nota sobre `--gmail-no-send`

La CLI expone `--gmail-no-send` para bloquear envíos a nivel proceso. En entornos de producción restringida puede activarse; si está activo, `drafts send` fallará a propósito.
