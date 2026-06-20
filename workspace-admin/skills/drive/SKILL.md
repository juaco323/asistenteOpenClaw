# Skill: Google Drive (Perfil Administrador)

Acceso **completo** a Google Drive mediante `gog drive` con la cuenta `prueba.openclaw.fj@gmail.com`.

## Permisos
- ✅ Listar y leer archivos
- ✅ Crear y subir archivos nuevos
- ✅ Modificar archivos existentes
- ✅ Eliminar archivos (sin protocolo adicional; basta confirmación verbal del Administrador)

## Comandos principales

```bash
# Listar archivos en la raíz
gog drive ls -a "prueba.openclaw.fj@gmail.com"

# Listar archivos en una carpeta específica (por ID)
gog drive ls -a "prueba.openclaw.fj@gmail.com" --folder-id "FOLDER_ID"

# Buscar archivos por nombre
gog drive search -a "prueba.openclaw.fj@gmail.com" "nombre del archivo"

# Descargar un archivo de Drive a local
gog drive download -a "prueba.openclaw.fj@gmail.com" "FILE_ID" --output "/home/node/Documentos/archivo.docx"

# Subir un archivo local a Drive
gog drive upload -a "prueba.openclaw.fj@gmail.com" "/home/node/Documentos/informe.docx"

# Subir a una carpeta específica
gog drive upload -a "prueba.openclaw.fj@gmail.com" "/home/node/Documentos/informe.docx" --folder-id "FOLDER_ID"

# Eliminar un archivo de Drive
gog drive delete -a "prueba.openclaw.fj@gmail.com" "FILE_ID"
```

## Enviar un archivo de Drive por Telegram

Si el usuario pide recibir un archivo de Drive en Telegram:

1. Descarga el archivo de Drive a `~/Documentos/` (ruta accesible por el bot de Telegram):
```bash
gog drive download -a "prueba.openclaw.fj@gmail.com" "FILE_ID" \
  --output "/home/node/Documentos/nombre_archivo.docx"
```

2. Responde con el marcador de entrega:
```
[[TELEGRAM_FILE:/home/node/Documentos/nombre_archivo.docx]]
```

**Importante:** la ruta de descarga debe ser `/home/node/Documentos/` o subcarpetas dentro de ella. El bot de Telegram solo puede leer archivos dentro de `~/Documentos`, `~/Descargas`, `~/Escritorio` e `~/Imágenes`.

## Subir a Drive un archivo recibido por Telegram

Los archivos enviados por el usuario en Telegram se guardan en:
`~/Documentos/telegram-openclaw-incoming/`

Para subirlos a Drive:
```bash
gog drive upload -a "prueba.openclaw.fj@gmail.com" \
  "/home/node/Documentos/telegram-openclaw-incoming/nombre_archivo.pdf"
```

## Notas de seguridad
- Siempre usar `-a "prueba.openclaw.fj@gmail.com"` en cada comando.
- No eliminar archivos de Drive sin confirmación explícita del Administrador en el chat.
