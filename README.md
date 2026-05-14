# asistenteOpenClaw

Repositorio de configuracion para dos agentes OpenClaw separados:

- `admin`
- `empleado`

Cada agente esta pensado para ejecutarse por separado, manteniendo su propio estado, sesiones, memoria y preferencias.

## Componentes

- `docker/admin`: stack Docker para el perfil administrador
- `docker/empleado`: stack Docker para el perfil empleado
- `docker/telegram`: despliegue del bot de Telegram que conversa con ambas instancias
- `workspace-admin`: workspace del agente administrador
- `workspace-empleado`: workspace del agente empleado

## Ejecucion paso a paso

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

Luego abre:

- `http://127.0.0.1:18789/`

## Instalar empleado

```bash
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

Luego abre:

- `http://127.0.0.1:18790/`

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
