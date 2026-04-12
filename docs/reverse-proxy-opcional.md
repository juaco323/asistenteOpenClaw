# Reverse proxy opcional

Para la fase de test no es obligatorio usar reverse proxy.

Puedes exponer cada agente directamente por puerto local:

- admin: `18789`
- empleado: `18790`

## Cuándo conviene agregar proxy

- si quieres HTTPS
- si vas a publicar acceso fuera de localhost
- si quieres dominio propio por agente
- si quieres centralizar acceso y logs

## Recomendación simple

Cuando pases a una versión más estable, conviene agregar un proxy como Caddy o Nginx delante de cada stack.

Ejemplo conceptual:

- `admin.tu-dominio.com` → `127.0.0.1:18789`
- `empleado.tu-dominio.com` → `127.0.0.1:18790`
