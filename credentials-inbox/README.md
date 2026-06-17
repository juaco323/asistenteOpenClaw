# Credenciales (no versionar valores reales)

Coloca aquí **uno** de estos formatos por perfil:

| Perfil   | Archivo `.env` plano | Archivo `.docx`      |
|----------|----------------------|----------------------|
| admin    | `admin.env`          | `.env admin.docx`    |
| empleado | `empleado.env`       | `.env empleado.docx` |
| telegram | `telegram.env`       | `.env telegram.docx` |

Desde la raíz del repo:

```bash
chmod +x scripts/apply-env-from-docx.sh
./scripts/apply-env-from-docx.sh
./docker/stack-up-cloud.sh   # entorno cloud
# o: ./docker/stack-up.sh    # PC local con Docker normal
```

Si los `.env` vienen de `/home/joaquin/...`, las rutas `OPENCLAW_HOST_HOME` y `TELEGRAM_HOST_HOME` se reescriben automáticamente al `$HOME` del host actual.
