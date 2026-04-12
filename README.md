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

## Estructura recomendada

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

## Nota

Esta versión es de **testeo**. La versión final puede incorporar endurecimiento, automatización adicional, backups y estrategia de actualización.
