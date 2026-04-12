# OpenClaw Agents Config Repo

Repositorio de configuración para dos agentes separados:

- `workspace-admin/`
- `workspace-empleado/`

La idea de este repositorio es versionar **configuración y prompts**, no el estado vivo del sistema.

## Qué sí se versiona

- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `TOOLS.md`
- `MEMORY.md`
- archivos de despliegue Docker
- documentación de instalación

## Qué no se versiona

- credenciales
- tokens
- sesiones activas
- auth profiles
- logs
- archivos temporales de ejecución

## Estructura del repositorio

```text
workspace-admin/
workspace-empleado/
docker/
  admin/
  empleado/
README.md
.gitignore
```

## Estrategia recomendada

- Un solo repositorio GitHub privado
- Dos despliegues Docker separados
- Dos volúmenes persistentes separados
- Mismo image base de OpenClaw
- Configuración distinta por agente
- Una máquina por agente

## Persistencia y preferencias

Para esta fase de testeo, **no hace falta una base de datos separada**.

La estrategia recomendada es persistir por agente:

- estado
- configuración
- sesiones
- workspace
- memoria
- preferencias en archivos (`MEMORY.md`, `USER.md`, `TOOLS.md`, etc.)

Si más adelante necesitas analítica estructurada, búsqueda avanzada entre agentes o preferencias centralizadas multiusuario, recién ahí conviene evaluar base de datos.

## Instalación rápida por agente

### Admin

```bash
chmod +x docker/admin/install.sh docker/admin/update.sh
docker/admin/install.sh
```

Control UI:
- `http://127.0.0.1:18789/`

### Empleado

```bash
chmod +x docker/empleado/install.sh docker/empleado/update.sh
docker/empleado/install.sh
```

Control UI:
- `http://127.0.0.1:18790/`

## Actualización

### Admin

```bash
docker/admin/update.sh
```

### Empleado

```bash
docker/empleado/update.sh
```

## Nota

Esta versión es de **testeo**. La versión final puede incorporar endurecimiento, automatización adicional, backups, fijación de versiones e integración más avanzada.
