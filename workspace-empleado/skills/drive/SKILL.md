# Skill: Google Drive (Perfil Empleado)

Acceso **restringido** a Google Drive mediante `gog drive` con la cuenta `prueba.openclaw.fj@gmail.com`.

## Permisos
- ✅ Listar y leer archivos existentes
- ✅ Crear y subir archivos nuevos
- ❌ Modificar archivos existentes — PROHIBIDO
- ❌ Eliminar archivos — PROHIBIDO

Ante cualquier solicitud de modificar o eliminar en Drive:
> _"El perfil Empleado no tiene permisos para modificar ni eliminar archivos en Drive. Contacta al Administrador."_

## Comandos permitidos

```bash
# Listar archivos en la raíz
gog drive ls -a "prueba.openclaw.fj@gmail.com"

# Buscar archivos por nombre
gog drive search -a "prueba.openclaw.fj@gmail.com" "nombre del archivo"

# Descargar un archivo de Drive a local (solo lectura)
gog drive download -a "prueba.openclaw.fj@gmail.com" "FILE_ID" \
  --output "/home/joaquin/Documentos/archivo.docx"

# Subir un archivo local nuevo a Drive
gog drive upload -a "prueba.openclaw.fj@gmail.com" "/home/joaquin/Documentos/nuevo_informe.docx"
```

## Enviar un archivo de Drive por Telegram

Si el usuario pide recibir un archivo de Drive en Telegram:

1. Descarga el archivo de Drive a `~/Documentos/`:
```bash
gog drive download -a "prueba.openclaw.fj@gmail.com" "FILE_ID" \
  --output "/home/joaquin/Documentos/nombre_archivo.docx"
```

2. Responde con el marcador de entrega:
```
[[TELEGRAM_FILE:/home/joaquin/Documentos/nombre_archivo.docx]]
```

**Importante:** la ruta de descarga debe ser `/home/joaquin/Documentos/` o subcarpetas dentro de ella. El bot de Telegram solo puede leer archivos dentro de `~/Documentos`, `~/Descargas`, `~/Escritorio` e `~/Imágenes`.

## Subir a Drive un archivo recibido por Telegram

Los archivos enviados por el usuario en Telegram se guardan en:
`~/Documentos/telegram-openclaw-incoming/`

Para subirlos a Drive (solo archivos nuevos):
```bash
gog drive upload -a "prueba.openclaw.fj@gmail.com" \
  "/home/joaquin/Documentos/telegram-openclaw-incoming/nombre_archivo.pdf"
```

## Notas de seguridad
- Siempre usar `-a "prueba.openclaw.fj@gmail.com"` en cada comando.
- Prohibido ejecutar `gog drive delete` o `gog drive update` sobre archivos existentes.
