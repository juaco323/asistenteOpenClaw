# Migración: OpenClaw nativo → Docker (admin)

Checklist para pasar de **OpenClaw nativo** (`~/.openclaw/`) al **stack Docker del repo** (`docker/admin` → `~/.openclaw-admin/`), sin tener dos gateways compitiendo por el mismo puerto.

---

## Antes (nativo sigue siendo la fuente de verdad)

1. **Respaldo del estado nativo** (por si algo sale mal):

   ```bash
   tar -czf ~/openclaw-native-backup-$(date +%Y%m%d-%H%M%S).tgz -C "$HOME" .openclaw
   ```

2. **Anota** (o guarda en un sitio seguro): modelo principal, canales/plugins que uses, y si dependes de `~/.openclaw/.env` para claves.

---

## Cortar el nativo (obligatorio si quieres el mismo puerto 18789)

3. **Para el gateway nativo** (servicio systemd, `openclaw gateway stop`, o el comando que uses). Comprueba que **nada** escuche en `18789`:

   ```bash
   ss -tlnp | grep 18789 || true
   ```

---

## Preparar Docker admin desde el repo

4. **Repo y permisos:**

   ```bash
   cd /ruta/a/asistenteOpenClaw   # ej. ~/Documentos/cursor-openclaw
   chmod +x docker/admin/*.sh
   ```

5. **Estrategia de datos:**

   - **A – Instalación limpia y reconfiguras en la UI**  
     Ejecutas `docker/admin/install.sh` (crea `~/.openclaw-admin`, copia `workspace-admin`, genera `docker/admin/.env` si no existe). Luego vuelves a poner modelo, plugins y claves como en nativo.

   - **B – Llevar casi todo el estado nativo**  
     - Crea el directorio destino si no existe: `mkdir -p ~/.openclaw-admin`  
     - Copia el contenido de `~/.openclaw/` a `~/.openclaw-admin/` **antes** del primer `up` del contenedor, o con el contenedor parado.  
     - **Revisa `~/.openclaw-admin/openclaw.json`:** las rutas absolutas tipo `.../.openclaw/workspace` deben ser coherentes con el volumen montado. En el stack actual el workspace se monta desde el repo (`workspace-admin/` → `/home/node/.openclaw/workspace` en el contenedor). Si no, el contenedor puede ver rutas incorrectas.

6. **Variables y token Docker**  
   - Claves (`OPENAI_API_KEY`, etc.) en `docker/admin/.env`.  
   - El **token del Control UI** del contenedor es `OPENCLAW_GATEWAY_TOKEN` en ese mismo `.env` (puede ser distinto del token en `openclaw.json` nativo). Tras migrar, entra con el token del `.env` de Docker.

7. **Levantar el stack:**

   ```bash
   docker/admin/install.sh
   ```

   Si ya tenías `docker/admin/.env` y datos en `~/.openclaw-admin`, basta con:

   ```bash
   cd docker/admin
   docker compose --env-file .env -f docker-compose.yml pull
   docker compose --env-file .env -f docker-compose.yml up -d
   ```

---

## Validar

8. Abre **`http://127.0.0.1:18789/`** y autentica con el token de `docker/admin/.env`.

9. En la UI: el workspace debería quedar bajo **`~/.openclaw-admin/...`**, no `~/.openclaw/...`.

10. Comprueba modelo, sesión nueva (`/new` si hace falta) y una petición de prueba al LLM.

11. Cuando estés conforme, **opcional:** si ya no quieres el nativo, en lugar de borrar de golpe puedes renombrar un tiempo:

    ```bash
    mv ~/.openclaw ~/.openclaw.disabled
    ```

---

## Después (mantenimiento en Docker)

12. Actualizaciones: `git pull` + `docker/admin/update.sh`.

13. Respaldos del **estado Docker**: `docker/admin/backup.sh` (genera `.tgz` del directorio configurado en `OPENCLAW_STATE_DIR`).

---

## Resumen

| Aspecto | Nativo | Docker admin (repo) |
|--------|--------|----------------------|
| Estado principal | `~/.openclaw/` | `~/.openclaw-admin/` |
| Claves / env | `~/.openclaw/.env`, shell, o `openclaw.json` | `docker/admin/.env` + `docker-compose.yml` |
| Puerto típico UI | 18789 | 18789 — no levantar nativo y Docker a la vez en el mismo puerto |

Mientras uses solo nativo, todo vive en `~/.openclaw/`. El dashboard “desde el proyecto” solo refleja la config Docker si el proceso que escucha en ese puerto es el **contenedor** con ese estado.

Para el agente **empleado**, el flujo es análogo usando `docker/empleado/` y `~/.openclaw-empleado/` (puerto host típico `18790`). No mezclar backups de admin y empleado sin revisar rutas y tokens en cada `.env`.
