# Guía rápida de operación

## 1. Instalar por primera vez

### Admin
```bash
git clone https://github.com/juaco323/asistenteOpenClaw.git
cd asistenteOpenClaw
chmod +x docker/admin/*.sh
docker/admin/install.sh
```

Abre:
- `http://127.0.0.1:18789/`

### Empleado
```bash
git clone https://github.com/juaco323/asistenteOpenClaw.git
cd asistenteOpenClaw
chmod +x docker/empleado/*.sh
docker/empleado/install.sh
```

Abre:
- `http://127.0.0.1:18790/`

## 2. Actualizar un agente ya instalado

Primero entra al repo y trae cambios:

```bash
cd asistenteOpenClaw
git pull
```

### Admin
```bash
docker/admin/update.sh
```

### Empleado
```bash
docker/empleado/update.sh
```

Esto sincroniza la configuración del workspace y vuelve a levantar el stack Docker.

## 3. Restaurar un backup

### Admin
```bash
docker/admin/restore.sh docker/admin/backups/ARCHIVO.tgz
```

### Empleado
```bash
docker/empleado/restore.sh docker/empleado/backups/ARCHIVO.tgz
```

## Nota útil

- `install.sh` = instalación inicial
- `update.sh` = actualización de un agente ya instalado
- `backup.sh` = generar respaldo
- `restore.sh` = restaurar respaldo
