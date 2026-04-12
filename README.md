# asistenteOpenClaw

Repositorio de configuración para dos agentes OpenClaw separados:

- `admin`
- `empleado`

Cada agente está pensado para ejecutarse por separado, idealmente en una máquina Ubuntu LTS distinta, manteniendo su propio estado, sesiones, memoria y preferencias.

## Ejecución paso a paso

### 1. Clonar el repositorio
```bash
git clone https://github.com/juaco323/asistenteOpenClaw.git
cd asistenteOpenClaw
```

### 2. Elegir qué agente instalar

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

### 3. Actualizar

## Admin
```bash
docker/admin/update.sh
```

## Empleado
```bash
docker/empleado/update.sh
```

### 4. Backup

## Admin
```bash
docker/admin/backup.sh
```

## Empleado
```bash
docker/empleado/backup.sh
```

### 5. Restore

## Admin
```bash
docker/admin/restore.sh docker/admin/backups/ARCHIVO.tgz
```

## Empleado
```bash
docker/empleado/restore.sh docker/empleado/backups/ARCHIVO.tgz
```
