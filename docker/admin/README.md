# Docker Admin (test)

Despliegue de prueba para el agente administrador.

## Objetivo

Ejecutar el agente `admin` en una máquina Ubuntu LTS con persistencia separada.

## Persistencia sugerida

- estado: `~/.openclaw-admin/`
- workspace: `~/.openclaw-admin/workspace/`

## Siguiente fase

En la siguiente iteración se puede agregar:

- `docker-compose.yml`
- `.env.example`
- script `install.sh`
- script `update.sh`
- guía de migración entre máquinas
