# Docker Empleado (test)

Despliegue de prueba para el agente empleado en Ubuntu LTS.

## Qué incluye

- `docker-compose.yml`
- `Dockerfile` (extiende OpenClaw; Python ofimática + CLI `gog`)
- `.env.example`
- `install.sh`
- `update.sh`
- `backup.sh`
- `restore.sh`

## Instalación

```bash
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

## URL

- Control UI OpenClaw (gateway): `http://127.0.0.1:<OPENCLAW_HOST_PORT>/` (valor en `docker/empleado/.env`; el ejemplo usa `18790`).
- **Histórico de pruebas LLM (empleado):** `http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/` (por defecto en compose `18795`; configurable en `.env`).

## Archivos importantes

- token y variables: `docker/empleado/.env`
- estado persistente: `~/.openclaw-empleado/`

## Mantenimiento

### Actualizar
```bash
docker/empleado/update.sh
```

### Backup
```bash
docker/empleado/backup.sh
```

### Restore
```bash
docker/empleado/restore.sh docker/empleado/backups/ARCHIVO.tgz
```

## Gmail / GOG (OAuth)

- Variables en `docker/empleado/.env`: **`GOG_KEYRING_PASSWORD`** (obligatoria para llavero `file`), **`GOG_ACCOUNT=prueba.openclaw.fj@gmail.com`** (remitente del proyecto). El compose monta **`${OPENCLAW_HOST_HOME}/.config/gogcli`** en el contenedor (ruta real de `gog` en Ubuntu).
- El compose monta **`${OPENCLAW_HOST_HOME}/.config/gogcli`** → `/home/node/.config/gogcli` para reutilizar el mismo almacén que en Ubuntu (`gog` usa la ruta `~/.config/gogcli`, no `.config/gog`).
- **Misma clave de llavero en host y contenedor:** antes de `gog auth add` en el host, usa `export GOG_KEYRING_BACKEND=file` y `export GOG_KEYRING_PASSWORD='…'` con el mismo valor que en `docker/empleado/.env`; si no, el contenedor no verá la sesión recién creada.
- En la imagen del empleado se instala la CLI `gog` (openclaw/gogcli). Registrar credenciales y autorizar cuenta en **terminal del host** antes de operar desde el agente:
  - `gog auth credentials set ~/Descargas/prueba_openclaw.fj.json`
  - `gog auth add prueba.openclaw.fj@gmail.com --services gmail`

## Observación

Esta es una base de test con imagen fijada a `2026.5.7` (requerida por plugins tipo IRC/Matrix/Mattermost ≥ 2026.4.10).
