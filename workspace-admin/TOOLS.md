# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Auditoría de código (`code-audit`)

- Skill y plantillas: `skills/code-audit/` en este workspace.
- Guía: `docs/auditoria-codigo.md`.
- Reportes alternativos: `~/Documentos/Reportes/auditoria-codigo/` (crear con `mkdir -p` si no existe).
- Perfil admin: priorizar seguridad; registrar en `memory/YYYY-MM-DD.md` si afecta despliegue.
