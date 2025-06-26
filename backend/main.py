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
import sys
from openai import OpenAI
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Video Transcription API", version="2.0.0")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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

# Configurar OpenAI para traducción
openai_client = None
translation_enabled = False

try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "tu_api_key_aqui":
        openai_client = OpenAI(api_key=api_key)
        translation_enabled = True
        print("✅ OpenAI configurado - Traducción habilitada")
    else:
        print("⚠️  OpenAI API key no configurada - Solo transcripción disponible")
except Exception as e:
    print(f"⚠️  Error configurando OpenAI: {e}")

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
        
        # Verificar duración (máximo 5 minutos = 300 segundos)
        if duration > 300:
            raise HTTPException(status_code=400, detail="El video debe durar menos de 5 minutos")
        
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

def translate_text(text: str, source_lang: str, target_lang: str):
    """Traduce texto usando OpenAI GPT"""
    if not translation_enabled or not openai_client:
        raise HTTPException(status_code=503, detail="Traducción no disponible - API key no configurada")
    
    try:
        # Mapear códigos de idioma
        lang_names = {
            "spanish": "español",
            "english": "inglés"
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        prompt = f"""Traduce el siguiente texto de {source_name} a {target_name}.
Mantén el tono natural y el contexto. Solo devuelve la traducción, sin explicaciones adicionales.

Texto a traducir:
{text}"""

        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "Eres un traductor profesional especializado en subtítulos de video."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en traducción: {str(e)}")

def translate_transcription_segments(segments, source_lang: str, target_lang: str):
    """Traduce todos los segmentos de una transcripción"""
    if source_lang == target_lang:
        return segments
    
    translated_segments = []
    
    for segment in segments:
        try:
            original_text = segment['text'].strip()
            if original_text:
                translated_text = translate_text(original_text, source_lang, target_lang)
                
                # Crear nuevo segmento con traducción
                translated_segment = {
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': translated_text
                }
                translated_segments.append(translated_segment)
            
        except Exception as e:
            # Si falla la traducción de un segmento, usar el original
            print(f"Error traduciendo segmento: {e}")
            translated_segments.append(segment)
    
    return translated_segments

@app.get("/")
async def root():
    return {
        "message": "Video Transcription API",
        "status": "running",
        "translation_enabled": translation_enabled,
        "version": "2.0.0"
    }

@app.get("/translation-status")
async def translation_status():
    """Verifica si la traducción está disponible"""
    return {
        "translation_enabled": translation_enabled,
        "supported_languages": ["spanish", "english"] if translation_enabled else [],
        "message": "Traducción disponible" if translation_enabled else "Configurar OPENAI_API_KEY para habilitar traducción"
    }

@app.post("/transcribe")
async def transcribe_video(
    file: UploadFile = File(...),
    language: str = Form(...),
    output_language: str = Form(None)
):
    """Endpoint principal para transcribir videos con traducción opcional"""
    
    # Validar tipo de archivo
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un video")
    
    # Validar idioma de entrada
    if language.lower() not in ['spanish', 'english']:
        raise HTTPException(status_code=400, detail="Idioma de entrada debe ser 'spanish' o 'english'")
    
    # Validar idioma de salida si se proporciona
    if output_language and output_language.lower() not in ['spanish', 'english']:
        raise HTTPException(status_code=400, detail="Idioma de salida debe ser 'spanish' o 'english'")
    
    # Si no se especifica idioma de salida, usar el mismo de entrada
    if not output_language:
        output_language = language
    
    # Verificar si se requiere traducción
    needs_translation = language.lower() != output_language.lower()
    
    if needs_translation and not translation_enabled:
        raise HTTPException(
            status_code=503,
            detail="Traducción no disponible - Configure OPENAI_API_KEY para habilitar traducción"
        )
    
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
        
        # Aplicar traducción si es necesaria
        final_segments = transcription['segments']
        if needs_translation:
            print(f"Traduciendo de {language} a {output_language}...")
            final_segments = translate_transcription_segments(
                transcription['segments'],
                language.lower(),
                output_language.lower()
            )
        
        # Crear transcripción final con segmentos (traducidos o no)
        final_transcription = {
            'segments': final_segments,
            'language': transcription.get('language', language)
        }
        
        # Crear archivo VTT
        create_vtt_file(final_transcription, str(vtt_path))
        
        # Retornar información de la transcripción
        return {
            "message": "Transcripción completada exitosamente" + (" con traducción" if needs_translation else ""),
            "duration": round(duration, 2),
            "input_language": language,
            "output_language": output_language,
            "translated": needs_translation,
            "segments_count": len(final_segments),
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