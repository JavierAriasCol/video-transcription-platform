# 🎥 Plataforma de Transcripción de Videos a VTT

Una aplicación web local que convierte videos de menos de 5 minutos a archivos de subtítulos VTT usando OpenAI Whisper, con capacidades de traducción automática.

## ✨ Características

- 🎯 **Transcripción precisa** con OpenAI Whisper local
- 🌍 **Soporte multiidioma** - Español, Inglés, Francés, Alemán, Italiano, Portugués, Ruso, Japonés, Coreano, Chino
- 🔄 **Traducción automática** - Transcribe en un idioma y traduce a otro usando OpenAI GPT
- 🔍 **Detección automática** de idioma del video
- 📱 **Interfaz responsive** y fácil de usar
- 🔒 **Procesamiento híbrido** - Transcripción local con Whisper, traducción via API OpenAI
- ⚡ **Rápido y eficiente** para videos cortos
- 📝 **Formato VTT** con timestamps precisos

## 🛠️ Tecnologías

### Backend

- **Python 3.8+** con FastAPI
- **OpenAI Whisper** para transcripción local
- **OpenAI GPT API** para traducción de texto
- **MoviePy** para procesamiento de video
- **Uvicorn** como servidor ASGI

### Frontend

- **HTML5, CSS3, JavaScript** (Vanilla)
- **Responsive Design**
- **Drag & Drop** para archivos
- **Progress tracking** en tiempo real

## 📋 Requisitos

- **Python 3.8 o superior**
- **FFmpeg** (requerido para procesamiento de video)
- **OpenAI API Key** (opcional, solo para traducción)
- Al menos 2GB de RAM libre
- Conexión a internet (para instalación de Whisper y traducción)

### Instalación de FFmpeg

FFmpeg es esencial para el funcionamiento de la aplicación. Tienes varias opciones:

**Opción 1: Script Automático (Recomendado)**

```bash
# Ejecutar el instalador incluido
install_ffmpeg.bat
```

**Opción 2: Chocolatey (Windows)**

```bash
# Instalar Chocolatey primero (como Administrador en PowerShell):
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Luego instalar FFmpeg:
choco install ffmpeg
```

**Opción 3: Winget (Windows 10/11)**

```bash
winget install ffmpeg
```

**Opción 4: Descarga Manual**

1. Ve a https://www.gyan.dev/ffmpeg/builds/
2. Descarga "release builds" > "ffmpeg-release-essentials.zip"
3. Extrae a `C:\ffmpeg`
4. Agrega `C:\ffmpeg\bin` al PATH del sistema

### Configuración de OpenAI API (Para Traducción)

Si deseas usar la funcionalidad de traducción, necesitas una API key de OpenAI:

1. **Obtener API Key**:

   - Ve a https://platform.openai.com/api-keys
   - Crea una cuenta o inicia sesión
   - Genera una nueva API key

2. **Configurar la API Key**:

   ```bash
   # Copia el archivo de ejemplo
   cp backend/.env.example backend/.env

   # Edita el archivo .env y agrega tu API key
   OPENAI_API_KEY=tu_api_key_aquí
   ```

3. **Verificar configuración**:
   - El archivo `.env` debe estar en la carpeta `backend/`
   - Nunca compartas tu API key públicamente
   - La traducción funcionará solo si la API key es válida

**Nota**: La funcionalidad de transcripción funciona sin API key. Solo necesitas la API key para traducir los subtítulos a otros idiomas.

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
# Si tienes git
git clone <repository-url>
cd video-transcription-platform

# O simplemente descarga y extrae los archivos
```

### 2. Configurar el Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Primera ejecución (descarga de modelo Whisper)

```bash
# Ejecutar el servidor por primera vez
python main.py
```

La primera vez que ejecutes la aplicación, Whisper descargará automáticamente el modelo small (~460MB). Esto puede tomar unos minutos dependiendo de tu conexión a internet.

## 🎮 Uso

### 1. Iniciar el Backend

```bash
cd backend
python main.py
```

El servidor se iniciará en `http://127.0.0.1:8000`

### 2. Abrir el Frontend

Tienes varias opciones:

**Opción A: Servidor HTTP simple**

```bash
cd frontend
python -m http.server 3000
```

Luego abre `http://localhost:3000`

**Opción B: Live Server (VS Code)**

- Instala la extensión "Live Server" en VS Code
- Haz clic derecho en `index.html` → "Open with Live Server"

**Opción C: Abrir directamente**

- Simplemente abre `frontend/index.html` en tu navegador

### 3. Usar la Aplicación

1. **Selecciona el idioma de entrada** del video (o usa detección automática)
2. **Selecciona el idioma de salida** (opcional, para traducción)
3. **Arrastra o selecciona** tu archivo de video (máximo 5 minutos)
4. **Haz clic en "Transcribir Video"**
5. **Espera** mientras se procesa:
   - Sin traducción: 1-4 minutos
   - Con traducción: 2-6 minutos (requiere API key de OpenAI)
6. **Descarga** el archivo VTT generado

#### Ejemplos de Uso:

- **Solo transcripción**: Selecciona idioma de entrada, deja idioma de salida vacío
- **Transcripción + traducción**: Video en Español → Subtítulos en Inglés
- **Detección automática**: Usa "Detectar automáticamente" como idioma de entrada

## 📁 Estructura del Proyecto

```
video-transcription-platform/
├── backend/
│   ├── main.py              # Servidor FastAPI principal
│   ├── requirements.txt     # Dependencias Python
│   └── temp_uploads/        # Archivos temporales (se crea automáticamente)
├── frontend/
│   ├── index.html          # Interfaz principal
│   ├── styles.css          # Estilos CSS
│   └── script.js           # Lógica JavaScript
└── README.md               # Este archivo
```

## 🎯 Formatos Soportados

### Videos de Entrada

- **MP4** (recomendado)
- **AVI**
- **MOV**
- **MKV**
- **WebM**
- Y otros formatos soportados por FFmpeg

### Salida

- **VTT** (WebVTT) con timestamps precisos

## ⚙️ Configuración Avanzada

### Cambiar Modelo de Whisper

En `backend/main.py`, línea 25:

```python
# Opciones: tiny, base, small, medium, large
model = whisper.load_model("small")  # Cambiar aquí
```

**Modelos disponibles:**

- `tiny` - Más rápido, menor precisión (~39MB)
- `base` - Balance básico (~140MB)
- `small` - **Por defecto** - Buena precisión (~460MB)
- `medium` - Alta precisión (~1.5GB)
- `large` - Máxima precisión (~3GB)

### Cambiar Puerto del Backend

En `backend/main.py`, última línea:

```python
uvicorn.run(app, host="127.0.0.1", port=8000)  # Cambiar puerto aquí
```

Si cambias el puerto, también actualiza `API_BASE_URL` en `frontend/script.js`.

## 🐛 Solución de Problemas

### Error: "No se puede conectar con el servidor"

- Verifica que el backend esté ejecutándose en http://127.0.0.1:8000
- Comprueba que no haya otro proceso usando el puerto 8000
- Revisa la consola del navegador para más detalles
- Asegúrate de que ambos servicios (frontend y backend) estén corriendo

### Error: "The system cannot find the file specified" / "FFmpeg not found"

Este es el error más común. FFmpeg no está instalado o no está en el PATH:

**Solución rápida:**

1. Ejecuta `install_ffmpeg.bat`
2. O instala manualmente con: `choco install ffmpeg`
3. Reinicia la terminal después de la instalación
4. Verifica con: `ffmpeg -version`

**Si el problema persiste:**

- Reinicia tu computadora después de instalar FFmpeg
- Verifica que FFmpeg esté en el PATH del sistema
- Prueba ejecutar `ffmpeg -version` en una nueva terminal

### Error: "El video debe durar menos de 5 minutos"

- La aplicación tiene un límite de 5 minutos por diseño
- Usa un editor de video para recortar el archivo
- Verifica que el archivo no esté corrupto

### Error: "Error en transcripción" / Baja calidad de transcripción

- Asegúrate de que el audio sea claro y sin ruido de fondo
- Verifica que hayas seleccionado el idioma correcto
- Prueba con un modelo Whisper más grande:
  ```python
  # En main.py, línea 25, cambia:
  model = whisper.load_model("small")  # o "medium", "large"
  ```

### Error: "Python no está instalado"

- Descarga Python 3.8+ desde https://python.org
- Durante la instalación, marca "Add Python to PATH"
- Reinicia la terminal después de la instalación

### Error: "No module named 'whisper'"

- Activa el entorno virtual: `venv\Scripts\activate.bat`
- Reinstala dependencias: `pip install -r requirements.txt`
- Si persiste: `pip install openai-whisper --upgrade`

### La aplicación es muy lenta

- Usa un modelo Whisper más pequeño (`tiny` o `base`)
- Cierra otras aplicaciones que consuman mucha RAM
- Asegúrate de tener al menos 2GB de RAM libre

### Error de CORS / Cross-Origin

- Asegúrate de acceder al frontend desde http://localhost:3000
- No abras el archivo HTML directamente (file://)
- Verifica que el backend esté corriendo en el puerto 8000

### Problemas con Traducción

**Error: "Translation failed" / "API key not configured"**

- Verifica que tengas un archivo `.env` en la carpeta `backend/`
- Asegúrate de que tu API key de OpenAI sea válida
- Comprueba que tengas créditos disponibles en tu cuenta de OpenAI
- El archivo `.env` debe contener: `OPENAI_API_KEY=tu_api_key_aquí`

**La traducción es muy lenta**

- La traducción depende de la API de OpenAI, puede tomar tiempo adicional
- Videos más largos requieren más tiempo de traducción
- Verifica tu conexión a internet

**Error: "Rate limit exceeded"**

- Has excedido el límite de uso de la API de OpenAI
- Espera unos minutos antes de intentar de nuevo
- Considera actualizar tu plan de OpenAI si usas frecuentemente la traducción

## 📊 Rendimiento

### Tiempos Aproximados (modelo small)

**Solo Transcripción:**

- **Video de 30 segundos**: ~20-40 segundos de procesamiento
- **Video de 1 minuto**: ~40-80 segundos de procesamiento
- **Video de 2 minutos**: ~80-160 segundos de procesamiento
- **Video de 3 minutos**: ~120-240 segundos de procesamiento
- **Video de 5 minutos**: ~200-400 segundos de procesamiento

**Transcripción + Traducción:**

- **Video de 30 segundos**: ~30-60 segundos de procesamiento
- **Video de 1 minuto**: ~60-120 segundos de procesamiento
- **Video de 2 minutos**: ~120-240 segundos de procesamiento
- **Video de 3 minutos**: ~180-360 segundos de procesamiento
- **Video de 5 minutos**: ~300-600 segundos de procesamiento

_Nota: Los tiempos de traducción dependen de la velocidad de respuesta de la API de OpenAI_

### Uso de Recursos

- **RAM**: 1-3GB durante el procesamiento
- **CPU**: Uso intensivo durante la transcripción
- **Almacenamiento**: ~500MB para modelo small + archivos temporales

## 🔧 API Endpoints

### GET `/`

Verificar estado del servidor

### POST `/transcribe`

Transcribir video (y opcionalmente traducir)

- **file**: Archivo de video (multipart/form-data)
- **language**: Idioma de entrada ("auto", "spanish", "english", "french", "german", "italian", "portuguese", "russian", "japanese", "korean", "chinese")
- **output_language**: (Opcional) Idioma de salida para traducción

### GET `/translation-status`

Verificar estado de la traducción (endpoint de utilidad)

### GET `/download/{filename}`

Descargar archivo VTT generado

### DELETE `/cleanup`

Limpiar archivos temporales

## 📄 Licencia

Este proyecto es de código abierto. Puedes usarlo, modificarlo y distribuirlo libremente.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema:

1. Revisa la sección de solución de problemas
2. Verifica los logs del servidor
3. Comprueba la consola del navegador
4. Abre un issue con detalles del error

---

**¡Disfruta transcribiendo tus videos! 🎉**
