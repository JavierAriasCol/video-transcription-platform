# 🎥 Plataforma de Transcripción de Videos a VTT

Una aplicación web local que convierte videos de menos de 2 minutos a archivos de subtítulos VTT usando OpenAI Whisper.

## ✨ Características

- 🎯 **Transcripción precisa** con OpenAI Whisper local
- 🌍 **Soporte bilingüe** - Español e Inglés
- 📱 **Interfaz responsive** y fácil de usar
- 🔒 **Procesamiento local** - Tus videos nunca salen de tu computadora
- ⚡ **Rápido y eficiente** para videos cortos
- 📝 **Formato VTT** con timestamps precisos

## 🛠️ Tecnologías

### Backend

- **Python 3.8+** con FastAPI
- **OpenAI Whisper** para transcripción local
- **Uvicorn** como servidor ASGI

### Frontend

- **HTML5, CSS3, JavaScript** (Vanilla)
- **Responsive Design**
- **Drag & Drop** para archivos
- **Progress tracking** en tiempo real

## 📋 Requisitos

- **Python 3.8 o superior**
- **FFmpeg** (requerido para procesamiento de video)
- Al menos 2GB de RAM libre
- Conexión a internet (para instalación de Whisper)

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

## 🚀 Instalación y Uso

### Método Rápido (Recomendado)

1. **Descargar el proyecto**
2. **Ejecutar el instalador automático**:
   ```bash
   start_app.bat
   ```

Este script automáticamente:

- Verifica que Python esté instalado
- Crea el entorno virtual
- Instala las dependencias
- Inicia el backend en puerto 8000
- Inicia el frontend en puerto 3000
- Abre la aplicación en tu navegador

### Método Manual

#### 1. Configurar el Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Iniciar el Backend

```bash
cd backend
python main.py
```

El servidor se iniciará en `http://127.0.0.1:8000`

#### 3. Iniciar el Frontend

```bash
cd frontend
python -m http.server 3000
```

Luego abre `http://localhost:3000`

### 4. Usar la Aplicación

1. **Selecciona el idioma** del video (Español o Inglés)
2. **Arrastra o selecciona** tu archivo de video (máximo 2 minutos)
3. **Haz clic en "Transcribir Video"**
4. **Espera** mientras se procesa (1-3 minutos)
5. **Descarga** el archivo VTT generado

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
├── start_app.bat           # Iniciador automático
├── install_ffmpeg.bat      # Instalador de FFmpeg
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

### Error: "FFmpeg not found"

Este es el error más común. FFmpeg no está instalado o no está en el PATH:

**Solución rápida:**

1. Ejecuta `install_ffmpeg.bat`
2. O instala manualmente con: `choco install ffmpeg`
3. Reinicia la terminal después de la instalación
4. Verifica con: `ffmpeg -version`

### Error: "El video debe durar menos de 2 minutos"

- La aplicación tiene un límite de 2 minutos por diseño
- Usa un editor de video para recortar el archivo
- Verifica que el archivo no esté corrupto

### Error: "Python no está instalado"

- Descarga Python 3.8+ desde https://python.org
- Durante la instalación, marca "Add Python to PATH"
- Reinicia la terminal después de la instalación

### Error: "No module named 'whisper'"

- Activa el entorno virtual: `venv\Scripts\activate.bat`
- Reinstala dependencias: `pip install -r requirements.txt`
- Si persiste: `pip install openai-whisper --upgrade`

## 📊 Rendimiento

### Tiempos Aproximados (modelo small)

- **Video de 30 segundos**: ~20-40 segundos de procesamiento
- **Video de 1 minuto**: ~40-80 segundos de procesamiento
- **Video de 2 minutos**: ~80-160 segundos de procesamiento

### Uso de Recursos

- **RAM**: 1-3GB durante el procesamiento
- **CPU**: Uso intensivo durante la transcripción
- **Almacenamiento**: ~500MB para modelo small + archivos temporales

## 🔧 API Endpoints

### GET `/`

Verificar estado del servidor

### POST `/transcribe`

Transcribir video

- **file**: Archivo de video (multipart/form-data)
- **language**: Idioma ("spanish" o "english")

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
