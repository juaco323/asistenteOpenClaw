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

**Crear borrador** (paso obligatorio antes de un envío nuevo):

```bash
gog gmail drafts create -a "prueba.openclaw.fj@gmail.com" --to "destinatario@dominio.com" --subject "Asunto" --body "Cuerpo en texto plano"
```

**Listar borradores**:

```bash
gog gmail drafts list -a "prueba.openclaw.fj@gmail.com"
```

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
