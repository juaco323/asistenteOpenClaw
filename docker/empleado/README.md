# Docker Empleado (test)

Despliegue de prueba para el agente empleado.

## Objetivo

Ejecutar el agente `empleado` en una máquina Ubuntu LTS con persistencia separada.

## Persistencia sugerida

- estado: `~/.openclaw-empleado/`
- workspace: `~/.openclaw-empleado/workspace/`

## Siguiente fase

En la siguiente iteración se puede agregar:

- `docker-compose.yml`
- `.env.example`
- script `install.sh`
- script `update.sh`
- guía de migración entre máquinas
