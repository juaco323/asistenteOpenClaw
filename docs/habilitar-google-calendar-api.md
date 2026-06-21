# Habilitar Google Calendar API (proyecto OAuth OpenClaw)

Error típico al crear Meet/Calendar:

```text
403 accessNotConfigured
Google Calendar API has not been used in project 504989080106 before or it is disabled
```

## Datos del proyecto (credencial en `~/Descargas/prueba_openclaw.fj.json`)

| Campo | Valor |
|-------|--------|
| **Project ID** | `august-victor-496423-e8` |
| **Project number** | `504989080106` |
| **Cuenta de pruebas** | `prueba.openclaw.fj@gmail.com` |

## Pasos (5 minutos)

1. Inicia sesión en Google con la cuenta que **creó el proyecto** en Google Cloud (o una cuenta con rol *Editor* / *Owner* en ese proyecto).

2. Abre el enlace directo a la API de Calendar:

   **https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?project=august-victor-496423-e8**

3. Pulsa **Habilitar** / **Enable**.

4. (Recomendado) Habilita también **Google Calendar API** en la lista de APIs habilitadas:

   **https://console.cloud.google.com/apis/dashboard?project=august-victor-496423-e8**

5. Espera **2–5 minutos** (propagación de Google).

6. Prueba desde el host:

   ```bash
   export GOG_KEYRING_BACKEND=file
   export GOG_KEYRING_PASSWORD='(igual que docker/admin/.env)'
   export XDG_CONFIG_HOME="$HOME/.config"

   gog auth list
   gog calendar list -a "prueba.openclaw.fj@gmail.com"
   ```

7. Vuelve a pedir la reunión en OpenClaw (perfil **Administrador**).

## OAuth

Si `gog auth list` ya muestra `calendar` en servicios, **no** hace falta repetir `gog auth add` solo por habilitar la API.

Si falta `calendar`:

```bash
./scripts/gog-auth-setup.sh
```

## Verificación en contenedor admin

```bash
docker exec openclaw-admin gog calendar list -a "prueba.openclaw.fj@gmail.com"
```
