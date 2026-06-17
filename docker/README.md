# Docker: stack completo

Admin, empleado y bot de Telegram están en carpetas separadas con su propio `docker-compose.yml` y `.env`.

## Variables de entorno y `docker compose` (importante)

Si en la misma sesión de terminal ejecutaste `set -a && . docker/empleado/.env` (o exportaste `OPENCLAW_*` / `GOG_*`), **Docker Compose puede priorizar esas variables sobre** `--env-file docker/admin/.env`. Eso ha provocado en algunos entornos que el stack **admin** intente crear el contenedor **`openclaw-empleado`**, use imagen/token equivocados o una **`GOG_KEYRING_PASSWORD`** distinta → errores de llavero (`integrity check failed`).

**Recomendación:** para levantar o recrear **admin**, usar entorno limpio o una terminal nueva:

```bash
cd /ruta/al/repo
env -i HOME="$HOME" PATH="$PATH" USER="${USER:-$USERNAME}" \
  docker compose -p admin --env-file docker/admin/.env -f docker/admin/docker-compose.yml up -d
```

Para **empleado**, análogo con `docker/empleado/.env` y `-p empleado` (o nueva terminal sin exports previos).

## Levantar todo (una sola vez configurados los `.env`)

Desde la raíz del repositorio:

```bash
chmod +x docker/stack-up.sh docker/stack-down.sh
./docker/stack-up.sh
```

Eso ejecuta `docker compose up` para `docker/admin`, `docker/empleado` y `docker/telegram` en ese orden.

### Credenciales desde `.docx`

Si tienes los tres archivos `.env admin.docx`, `.env empleado.docx` y `.env telegram.docx`:

```bash
cp "/ruta/.env admin.docx" credentials-inbox/
cp "/ruta/.env empleado.docx" credentials-inbox/
cp "/ruta/.env telegram.docx" credentials-inbox/
chmod +x scripts/apply-env-from-docx.sh
./scripts/apply-env-from-docx.sh
./docker/stack-up.sh   # o stack-up-cloud.sh en entornos cloud sin DNS en bridge Docker
```

### Entornos cloud / sin DNS en bridge Docker

En máquinas donde `docker build` o contenedores no resuelven DNS (p. ej. agentes cloud), usa:

```bash
chmod +x scripts/ensure-dockerd.sh docker/stack-up-cloud.sh
./docker/stack-up-cloud.sh
```

### PC local (`/home/joaquin` u otro home)

Con Docker Desktop o Engine en marcha:

```bash
chmod +x scripts/pc-up.sh scripts/set-env-home.sh
./scripts/pc-up.sh
```

`pc-up.sh` aplica credenciales desde `credentials-inbox/` si existen, ajusta rutas a `/home/joaquin`, crea carpetas de estado y ejecuta `./docker/stack-up.sh`.

Solo reescribir rutas en `.env` ya existentes:

```bash
./scripts/set-env-home.sh /home/joaquin
```

## Bajar todo

```bash
./docker/stack-down.sh
```

## Workspaces en el repo

Los contenedores **admin** y **empleado** montan `workspace-admin/` y `workspace-empleado/`. Cada stack incluye el **panel de histórico de pruebas LLM** (puertos `LLM_TEST_PANEL_HOST_PORT` en cada `.env`; por defecto en compose suelen ser **18794** admin y **18795** empleado para no chocar con los gateways).

No hace falta copiar el workspace a `~/.openclaw-*/workspace`; el estado (sesiones, etc.) sigue en `OPENCLAW_STATE_DIR` definido en cada `.env`.

## Componentes

| Carpeta | Rol |
|---------|-----|
| `docker/admin` | Gateway admin + `gog`; `~/.config/gogcli`→`/home/node/.config/gogcli` (**rw**); `workspace-empleado`→`/app/logs_shared` (**rw**). Mantener **`GOG_ACCOUNT=prueba.openclaw.fj@gmail.com`** en `.env`. |
| `docker/empleado` | Gateway empleado (Python + `gog`); `~/.config/gogcli`→`/home/node/.config/gogcli` (**rw**). **`GOG_ACCOUNT=prueba.openclaw.fj@gmail.com`**. |
| `docker/telegram` | Bot que habla con ambos gateways |

Instalación inicial por pieza: `docker/*/install.sh`. Actualizar: `docker/*/update.sh`.

## Gmail / GOG — qué hay que tener en el **host**

Para que **`gog gmail …`** funcione dentro de **admin/empleado**, el volumen **`${OPENCLAW_HOST_HOME}/.config/gogcli`** debe existir en tu usuario y **contener OAuth + sesión Gmail** obtenidas en esa misma máquina y con **la misma** `GOG_KEYRING_PASSWORD` que en `docker/*/ .env`.

1. **`GOG_KEYRING_PASSWORD` y `GOG_ACCOUNT`** en `docker/admin/.env` y `docker/empleado/.env` (ya documentado en cada README).
2. **JSON del cliente OAuth 2.0** de Google Cloud (descarga manual desde la consola), guardado p. ej. como **`~/Descargas/prueba_openclaw.fj.json`**.
3. En una terminal **del host**, con **`gog`** instalado:
   ```bash
   chmod +x scripts/register-gmail-gog-on-host.sh
   scripts/register-gmail-gog-on-host.sh
   ```
   El script ejecuta **`gog auth credentials set`** con ese JSON y te indica el segundo paso:
   **`gog auth add … --services gmail`** (interactivo, abre navegador o muestra URL).
4. **`gog auth list`** debe mostrar autorización válida antes de pedir borradores al agente desde Cursor o Telegram.
5. Pauta detallada de comandos: `skills/email-gmail/SKILL.md` y `docker/empleado/README.md` (sección Gmail / GOG).

Si **`~/.config/gogcli`** está vacío pero la API key y Telegram ya funcionan, lo único que falta para **correo** suele ser el paso OAuth anterior.
