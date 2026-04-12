# Despliegue de test en Ubuntu LTS

Esta guía aplica tanto para `admin` como para `empleado`, cambiando solo la carpeta correspondiente.

## Requisitos

- Ubuntu LTS
- Docker Engine
- Docker Compose v2
- Git

## Flujo por máquina

### Admin
```bash
git clone https://github.com/juaco323/asistenteOpenClaw.git
cd asistenteOpenClaw
chmod +x docker/admin/*.sh
docker/admin/install.sh
```

### Empleado
```bash
git clone https://github.com/juaco323/asistenteOpenClaw.git
cd asistenteOpenClaw
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

## Persistencia

Cada agente guarda su estado por separado:

- admin: `~/.openclaw-admin/`
- empleado: `~/.openclaw-empleado/`

Esto permite mover cada agente a otra máquina conservando configuración, memoria y sesiones, siempre que copies esa carpeta.

## Actualización

Primero trae los cambios del repositorio:

```bash
git pull
```

Luego ejecuta:

### Admin
```bash
docker/admin/update.sh
```

### Empleado
```bash
docker/empleado/update.sh
```

El script de actualización vuelve a copiar la configuración del workspace desde el repo local al workspace persistente del agente y después relanza el stack.

## Backup

### Admin
```bash
docker/admin/backup.sh
```

### Empleado
```bash
docker/empleado/backup.sh
```

## Restore

### Admin
```bash
docker/admin/restore.sh docker/admin/backups/ARCHIVO.tgz
```

### Empleado
```bash
docker/empleado/restore.sh docker/empleado/backups/ARCHIVO.tgz
```

## Nota sobre base de datos

Para esta fase no se requiere una base de datos separada. La persistencia se apoya en el volumen de estado y en los archivos del workspace.
