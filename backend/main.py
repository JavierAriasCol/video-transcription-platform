from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import whisper
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import uvicorn
import subprocess

app = FastAPI(title="Video Transcription API", version="1.0.0")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio para archivos temporales
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

# Cargar modelo Whisper (se descarga automáticamente la primera vez)
print("Cargando modelo Whisper...")
model = whisper.load_model("small")
print("Modelo Whisper 'small' cargado exitosamente")

def check_ffmpeg():
    """Verifica si FFmpeg está disponible"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_duration(video_path: str):
    """Obtiene la duración del video usando FFprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        
        # Buscar duración en streams de video
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                duration = float(stream.get('duration', 0))
                if duration > 0:
                    return duration
        
        # Si no se encuentra en streams, buscar en format
        duration = float(data.get('format', {}).get('duration', 0))
        return duration
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo duración: {str(e)}")

def extract_audio_from_video(video_path: str, audio_path: str):
    """Extrae audio de un archivo de video usando FFmpeg"""
    try:
        # Verificar si FFmpeg está disponible
        if not check_ffmpeg():
            raise HTTPException(
                status_code=500,
                detail="FFmpeg no está instalado. Por favor instala FFmpeg desde https://ffmpeg.org/download.html"
            )
        
        # Obtener duración del video
        duration = get_video_duration(video_path)
        
        # Verificar duración (máximo 2 minutos = 120 segundos)
        if duration > 120:
            raise HTTPException(status_code=400, detail="El video debe durar menos de 2 minutos")
        
        # Extraer audio usando FFmpeg
        cmd = [
            'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1', '-y', audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Error extrayendo audio: {result.stderr}"
            )
        
        return duration
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando video: {str(e)}")

def transcribe_audio(audio_path: str, language: str):
    """Transcribe audio usando Whisper"""
    try:
        # Mapear idiomas
        lang_map = {
            "spanish": "es",
            "english": "en"
        }
        
        whisper_lang = lang_map.get(language.lower(), "es")
        
        # Transcribir
        result = model.transcribe(audio_path, language=whisper_lang)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en transcripción: {str(e)}")

def create_vtt_file(transcription_result, output_path: str):
    """Convierte la transcripción a formato VTT"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for segment in transcription_result['segments']:
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando archivo VTT: {str(e)}")

def format_timestamp(seconds):
    """Convierte segundos a formato VTT (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

@app.get("/")
async def root():
    return {
        "message": "Video Transcription API",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/transcribe")
async def transcribe_video(
    file: UploadFile = File(...),
    language: str = Form(...)
):
    """Endpoint principal para transcribir videos"""
    
    # Validar tipo de archivo
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un video")
    
    # Validar idioma de entrada
    if language.lower() not in ['spanish', 'english']:
        raise HTTPException(status_code=400, detail="Idioma debe ser 'spanish' o 'english'")
    
    # Crear nombres de archivos temporales
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"video_{timestamp}_{file.filename}"
    audio_filename = f"audio_{timestamp}.wav"
    vtt_filename = f"transcription_{timestamp}.vtt"
    
    video_path = TEMP_DIR / video_filename
    audio_path = TEMP_DIR / audio_filename
    vtt_path = TEMP_DIR / vtt_filename
    
    try:
        # Guardar video subido
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extraer audio del video
        duration = extract_audio_from_video(str(video_path), str(audio_path))
        
        # Transcribir audio
        transcription = transcribe_audio(str(audio_path), language)
        
        # Crear archivo VTT
        create_vtt_file(transcription, str(vtt_path))
        
        # Retornar información de la transcripción
        return {
            "message": "Transcripción completada exitosamente",
            "duration": round(duration, 2),
            "language": language,
            "segments_count": len(transcription['segments']),
            "download_url": f"/download/{vtt_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    finally:
        # Limpiar archivos temporales (excepto VTT)
        for temp_file in [video_path, audio_path]:
            if temp_file.exists():
                temp_file.unlink()

@app.get("/download/{filename}")
async def download_vtt(filename: str):
    """Endpoint para descargar archivos VTT"""
    file_path = TEMP_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='text/vtt'
    )

@app.delete("/cleanup")
async def cleanup_temp_files():
    """Endpoint para limpiar archivos temporales"""
    try:
        count = 0
        for file_path in TEMP_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
                count += 1
        
        return {"message": f"Se eliminaron {count} archivos temporales"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando archivos: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)