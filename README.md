# asistenteOpenClaw

Repositorio de configuracion para dos agentes OpenClaw separados:

- `admin`
- `empleado`

Cada agente esta pensado para ejecutarse por separado, manteniendo su propio estado, sesiones, memoria y preferencias.

## Componentes

- `docker/admin`: stack Docker para el perfil administrador
- `docker/empleado`: stack Docker para el perfil empleado
- `docker/telegram`: despliegue del bot de Telegram que conversa con ambas instancias
- `workspace-admin`: workspace del agente administrador (montado en el contenedor admin)
- `workspace-empleado`: workspace del agente empleado (montado en el contenedor empleado)

## Levantar todo el stack (Docker)

Tras configurar `docker/admin/.env`, `docker/empleado/.env` y `docker/telegram/.env` (cada uno desde su `.env.example`):

```bash
chmod +x docker/stack-up.sh docker/stack-down.sh
./docker/stack-up.sh
```

Detener: `./docker/stack-down.sh`. Detalle en `docker/README.md`.

## Ejecucion paso a paso (por componente)

### 1. Clonar el repositorio

```bash
git clone https://github.com/juaco323/asistenteOpenClaw.git
cd asistenteOpenClaw
```

### 2. Elegir que agente instalar

## Instalar admin

```bash
chmod +x docker/admin/*.sh
docker/admin/install.sh
```

Luego abre el panel (puerto según `OPENCLAW_HOST_PORT` en `docker/admin/.env`, por ejemplo `http://127.0.0.1:18789/`).

## Instalar empleado

```bash
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

Luego abre el panel (puerto según `OPENCLAW_HOST_PORT` en `docker/empleado/.env`, por ejemplo `http://127.0.0.1:18790/`).

### 3. Instalar el bot de Telegram

```bash
chmod +x docker/telegram/*.sh
docker/telegram/install.sh
```

### 4. Actualizar

Primero trae los cambios del repositorio:

```bash
git pull
```

Luego actualiza el componente correspondiente.

## Admin

```bash
docker/admin/update.sh
```

## Empleado

```bash
docker/empleado/update.sh
```

## Telegram

```bash
docker/telegram/update.sh
```

### 5. Documentacion de conexion Telegram

Consulta:

- `docs/conexion-telegram-openclaw.md`
- `integrations/telegram-bot/README.md`
- `docker/telegram/README.md`

El bot incluye:

- autenticacion por contraseña al cambiar entre perfiles (`/workspace`)
- entrega de archivos por Telegram (`/get` o lenguaje natural)
- politica de archivos por workspace (`integrations/telegram-bot/config/workspace-file-policy.yaml`)
- cierre de sesion de perfil con `/salir` (requiere reautenticacion para `/chat`)

### 6. Backup y restore

## Admin

```bash
docker/admin/backup.sh
```

## Empleado

```bash
docker/empleado/backup.sh
```
