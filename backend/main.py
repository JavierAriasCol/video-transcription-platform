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

def get_media_duration(media_path: str):
    """Obtiene la duración del archivo de video o audio usando FFprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', media_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        
        # Buscar duración en streams de video o audio
        for stream in data.get('streams', []):
            if stream.get('codec_type') in ['video', 'audio']:
                duration = float(stream.get('duration', 0))
                if duration > 0:
                    return duration
        
        # Si no se encuentra en streams, buscar en format
        duration = float(data.get('format', {}).get('duration', 0))
        return duration
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo duración: {str(e)}")

def extract_audio_or_process_audio(input_path: str, audio_path: str):
    """Extrae audio de un archivo de video o procesa archivo de audio usando FFmpeg"""
    try:
        # Verificar si FFmpeg está disponible
        if not check_ffmpeg():
            raise HTTPException(
                status_code=500,
                detail="FFmpeg no está instalado. Por favor instala FFmpeg desde https://ffmpeg.org/download.html"
            )
        
        # Obtener duración del archivo
        duration = get_media_duration(input_path)
        
        # Verificar duración (máximo 30 minutos = 1800 segundos)
        if duration > 1800:
            raise HTTPException(status_code=400, detail="El archivo debe durar menos de 30 minutos")
        
        # Detectar si es archivo de video o audio
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        
        # Verificar si tiene stream de video
        has_video = any(stream.get('codec_type') == 'video' for stream in data.get('streams', []))
        
        if has_video:
            # Es un archivo de video - extraer audio
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1', '-y', audio_path
            ]
        else:
            # Es un archivo de audio - convertir al formato requerido
            cmd = [
                'ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1', '-y', audio_path
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando audio: {result.stderr}"
            )
        
        return duration
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

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
    """Convierte la transcripción a formato VTT con máximo 5 palabras por segmento"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            segment_counter = 1
            
            for segment in transcription_result['segments']:
                start_time_seconds = segment['start']
                end_time_seconds = segment['end']
                text = segment['text'].strip()
                
                # Dividir el texto en palabras
                words = text.split()
                
                # Si el segmento tiene 5 palabras o menos, mantenerlo como está
                if len(words) <= 5:
                    start_time = format_timestamp(start_time_seconds)
                    end_time = format_timestamp(end_time_seconds)
                    
                    f.write(f"{segment_counter}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
                    segment_counter += 1
                else:
                    # Dividir en sub-segmentos de máximo 5 palabras
                    segment_duration = end_time_seconds - start_time_seconds
                    total_words = len(words)
                    
                    # Crear sub-segmentos
                    for i in range(0, total_words, 5):
                        # Obtener las palabras para este sub-segmento
                        sub_words = words[i:i+5]
                        sub_text = ' '.join(sub_words)
                        
                        # Calcular timestamps proporcionales
                        words_in_subsegment = len(sub_words)
                        words_processed = i
                        
                        # Calcular tiempo de inicio y fin proporcional
                        sub_start = start_time_seconds + (words_processed / total_words) * segment_duration
                        sub_end = start_time_seconds + ((words_processed + words_in_subsegment) / total_words) * segment_duration
                        
                        # Formatear timestamps
                        sub_start_formatted = format_timestamp(sub_start)
                        sub_end_formatted = format_timestamp(sub_end)
                        
                        # Escribir sub-segmento
                        f.write(f"{segment_counter}\n")
                        f.write(f"{sub_start_formatted} --> {sub_end_formatted}\n")
                        f.write(f"{sub_text}\n\n")
                        segment_counter += 1
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando archivo VTT: {str(e)}")

def create_clean_transcription(transcription_result, output_path: str):
    """Convierte la transcripción a formato de texto limpio sin timestamps"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Recopilar todo el texto de los segmentos
            full_text = ""
            for segment in transcription_result['segments']:
                text = segment['text'].strip()
                if text:
                    full_text += text + " "
            
            # Limpiar el texto y crear párrafos más naturales
            full_text = full_text.strip()
            
            # Dividir en oraciones usando puntos, signos de exclamación y interrogación
            import re
            sentences = re.split(r'[.!?]+', full_text)
            
            # Agrupar oraciones en párrafos (aproximadamente cada 3-4 oraciones)
            paragraphs = []
            current_paragraph = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    current_paragraph.append(sentence)
                    
                    # Crear nuevo párrafo cada 3-4 oraciones o si la oración es muy larga
                    if len(current_paragraph) >= 3 or len(sentence) > 100:
                        paragraphs.append('. '.join(current_paragraph) + '.')
                        current_paragraph = []
            
            # Añadir último párrafo si queda contenido
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph) + '.')
            
            # Si no se pudieron crear párrafos, usar el texto completo
            if not paragraphs:
                paragraphs = [full_text]
            
            # Escribir párrafos separados por líneas en blanco
            for i, paragraph in enumerate(paragraphs):
                f.write(paragraph)
                if i < len(paragraphs) - 1:  # No añadir línea extra al final
                    f.write('\n\n')
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando transcripción limpia: {str(e)}")

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
async def transcribe_media(
    file: UploadFile = File(...),
    language: str = Form(...),
    transcription_type: str = Form("vtt")
):
    """Endpoint principal para transcribir videos o audios"""
    
    # Debug logging para verificar parámetros recibidos
    print(f"DEBUG - Parámetros recibidos:")
    print(f"DEBUG - file.filename: {file.filename}")
    print(f"DEBUG - file.content_type: {file.content_type}")
    print(f"DEBUG - language: {language}")
    print(f"DEBUG - transcription_type: '{transcription_type}'")
    print(f"DEBUG - transcription_type.lower(): '{transcription_type.lower()}'")
    
    # Validar tipo de archivo
    if not (file.content_type.startswith('video/') or file.content_type.startswith('audio/')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un video o audio")
    
    # Validar idioma de entrada
    if language.lower() not in ['spanish', 'english']:
        raise HTTPException(status_code=400, detail="Idioma debe ser 'spanish' o 'english'")
    
    # Validar tipo de transcripción
    if transcription_type.lower() not in ['vtt', 'clean']:
        raise HTTPException(status_code=400, detail="Tipo de transcripción debe ser 'vtt' o 'clean'")
    
    # Crear nombres de archivos temporales
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_filename = f"input_{timestamp}_{file.filename}"
    audio_filename = f"audio_{timestamp}.wav"
    
    # Determinar extensión del archivo de salida según el tipo
    if transcription_type.lower() == "clean":
        output_filename = f"transcription_{timestamp}.txt"
    else:
        output_filename = f"transcription_{timestamp}.vtt"
    
    input_path = TEMP_DIR / input_filename
    audio_path = TEMP_DIR / audio_filename
    output_path = TEMP_DIR / output_filename
    
    try:
        # Guardar archivo subido
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extraer o procesar audio
        duration = extract_audio_or_process_audio(str(input_path), str(audio_path))
        
        # Transcribir audio
        transcription = transcribe_audio(str(audio_path), language)
        
        # Crear archivo según el tipo solicitado
        print(f"DEBUG - Creando archivo de transcripción...")
        print(f"DEBUG - transcription_type.lower() == 'clean': {transcription_type.lower() == 'clean'}")
        print(f"DEBUG - output_path: {output_path}")
        
        if transcription_type.lower() == "clean":
            print(f"DEBUG - Creando transcripción limpia...")
            create_clean_transcription(transcription, str(output_path))
            transcription_message = "Transcripción limpia completada exitosamente"
            print(f"DEBUG - Transcripción limpia creada exitosamente")
        else:
            print(f"DEBUG - Creando archivo VTT...")
            create_vtt_file(transcription, str(output_path))
            transcription_message = "Transcripción VTT completada exitosamente"
            print(f"DEBUG - Archivo VTT creado exitosamente")
        
        # Retornar información de la transcripción
        return {
            "message": transcription_message,
            "duration": round(duration, 2),
            "language": language,
            "transcription_type": transcription_type.lower(),
            "original_segments_count": len(transcription['segments']),
            "download_url": f"/download/{output_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    finally:
        # Limpiar archivos temporales (excepto archivo de transcripción)
        for temp_file in [input_path, audio_path]:
            if temp_file.exists():
                temp_file.unlink()

@app.get("/download/{filename}")
async def download_transcription(filename: str):
    """Endpoint para descargar archivos de transcripción (VTT o TXT)"""
    file_path = TEMP_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    # Determinar tipo de media según la extensión
    if filename.lower().endswith('.txt'):
        media_type = 'text/plain'
    else:
        media_type = 'text/vtt'
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
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

def create_subtitled_video(video_path: str, vtt_path: str, output_path: str,
                          font_color: str = "#ffffff", background_color: str = "#000000",
                          font_size: int = 20, background_opacity: float = 0.8,
                          box_enabled: bool = False, box_color: str = "#000000"):
    """Crea un video con subtítulos usando FFmpeg"""
    try:
        # Verificar si FFmpeg está disponible
        if not check_ffmpeg():
            raise HTTPException(
                status_code=500,
                detail="FFmpeg no está instalado. Por favor instala FFmpeg desde https://ffmpeg.org/download.html"
            )
        
        # Verificar que el archivo VTT existe
        if not os.path.exists(vtt_path):
            raise HTTPException(
                status_code=500,
                detail=f"Archivo VTT no encontrado: {vtt_path}"
            )
        
        # Convertir a ruta absoluta para evitar problemas de rutas relativas
        vtt_path_absolute = os.path.abspath(vtt_path)
        video_path_absolute = os.path.abspath(video_path)
        output_path_absolute = os.path.abspath(output_path)
        
        # Debug logging - imprimir rutas que se están usando
        print(f"DEBUG - Ruta VTT original: {vtt_path}")
        print(f"DEBUG - Ruta VTT absoluta: {vtt_path_absolute}")
        print(f"DEBUG - Archivo VTT existe: {os.path.exists(vtt_path_absolute)}")
        print(f"DEBUG - Ruta video absoluta: {video_path_absolute}")
        print(f"DEBUG - Ruta output absoluta: {output_path_absolute}")
        
        # Convertir colores hex a formato FFmpeg
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        font_rgb = hex_to_rgb(font_color)
        bg_rgb = hex_to_rgb(background_color)
        
        # Usar ruta absoluta y escapar caracteres especiales para Windows
        # Reemplazar \ con \\ y : con \: para FFmpeg en Windows
        vtt_path_for_filter = vtt_path_absolute.replace('\\', '\\\\').replace(':', '\\:')
        
        # Crear filtro de subtítulos con sintaxis correcta usando filename=
        if box_enabled:
            # Configuración para caja - BorderStyle=4 crea una caja opaca de fondo
            box_rgb = hex_to_rgb(box_color)
            
            # Detectar si el color es muy oscuro y ajustar opacidad automáticamente
            # Calcular luminancia del color para determinar si es oscuro
            luminance = (0.299 * box_rgb[0] + 0.587 * box_rgb[1] + 0.114 * box_rgb[2])
            
            # Si el color es muy oscuro (luminance < 50), usar menos opacidad para mejor visibilidad
            # Si es claro, usar más opacidad
            if luminance < 50:
                alpha = "A0"  # 62% opaco para colores oscuros
                print(f"DEBUG - Color oscuro detectado (luminance: {luminance:.1f}), usando opacidad 62%")
            else:
                alpha = "D0"  # 81% opaco para colores claros
                print(f"DEBUG - Color claro detectado (luminance: {luminance:.1f}), usando opacidad 81%")
            
            # Para cajas, usamos BorderStyle=4 y configuramos BackColour con opacidad
            # El formato de color en ASS es &HAABBGGRR donde AA es alpha (transparencia)
            subtitle_filter = (
                f"subtitles=filename='{vtt_path_for_filter}':force_style='"
                f"FontSize={font_size},"
                f"PrimaryColour=&H00{font_rgb[2]:02x}{font_rgb[1]:02x}{font_rgb[0]:02x},"
                f"BorderStyle=4,"
                f"BackColour=&H{alpha}{box_rgb[2]:02x}{box_rgb[1]:02x}{box_rgb[0]:02x},"
                f"Outline=1,"
                f"OutlineColour=&H00000000,"
                f"Shadow=0,"
                f"MarginV=20,"
                f"MarginL=15,"
                f"MarginR=15'"
            )
            print(f"DEBUG - Modo caja habilitado:")
            print(f"DEBUG - Color de caja RGB: {box_rgb}")
            print(f"DEBUG - BackColour con opacidad automática: &H{alpha}{box_rgb[2]:02x}{box_rgb[1]:02x}{box_rgb[0]:02x}")
            print(f"DEBUG - Configuración: BorderStyle=4, Outline=1 para mejor visibilidad")
        else:
            # Configuración normal sin caja (BorderStyle=1 con outline)
            subtitle_filter = (
                f"subtitles=filename='{vtt_path_for_filter}':force_style='"
                f"FontSize={font_size},"
                f"PrimaryColour=&H00{font_rgb[2]:02x}{font_rgb[1]:02x}{font_rgb[0]:02x},"
                f"BorderStyle=1,"
                f"OutlineColour=&H00{bg_rgb[2]:02x}{bg_rgb[1]:02x}{bg_rgb[0]:02x},"
                f"Outline=2,"
                f"Shadow=1,"
                f"MarginV=20'"
            )
            print(f"DEBUG - Modo normal (sin caja)")
        
        print(f"DEBUG - Filtro de subtítulos: {subtitle_filter}")
        
        # Comando FFmpeg para añadir subtítulos
        cmd = [
            'ffmpeg', '-i', video_path_absolute, '-vf', subtitle_filter,
            '-c:a', 'copy', '-y', output_path_absolute
        ]
        
        print(f"DEBUG - Comando FFmpeg: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"DEBUG - Error FFmpeg stdout: {result.stdout}")
            print(f"DEBUG - Error FFmpeg stderr: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Error añadiendo subtítulos: {result.stderr}"
            )
        
        print("DEBUG - Video subtitulado creado exitosamente")
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG - Excepción en create_subtitled_video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando video: {str(e)}")

def count_vtt_subtitles(vtt_path: str):
    """Cuenta el número de subtítulos en un archivo VTT"""
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Contar líneas que contienen timestamps (formato: HH:MM:SS.mmm --> HH:MM:SS.mmm)
            import re
            timestamps = re.findall(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', content)
            return len(timestamps)
    except Exception:
        return 0

@app.post("/subtitle")
async def subtitle_video(
    video: UploadFile = File(...),
    vtt: UploadFile = File(...),
    font_color: str = Form("#ffffff"),
    background_color: str = Form("#000000"),
    font_size: int = Form(20),
    background_opacity: float = Form(0.8),
    box_enabled: bool = Form(False),
    box_color: str = Form("#000000")
):
    """Endpoint para añadir subtítulos a un video"""
    
    # Validar tipo de archivo de video
    if not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un video")
    
    # Validar archivo VTT
    if not vtt.filename.lower().endswith('.vtt'):
        raise HTTPException(status_code=400, detail="El archivo de subtítulos debe ser VTT")
    
    # Crear nombres de archivos temporales
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"input_video_{timestamp}_{video.filename}"
    vtt_filename = f"subtitles_{timestamp}.vtt"
    output_filename = f"subtitled_video_{timestamp}.mp4"
    
    # Usar os.path.join para construcción correcta de rutas
    video_path = os.path.join(str(TEMP_DIR), video_filename)
    vtt_path = os.path.join(str(TEMP_DIR), vtt_filename)
    output_path = os.path.join(str(TEMP_DIR), output_filename)
    
    # Debug logging para verificar rutas
    print(f"DEBUG - Construyendo rutas:")
    print(f"DEBUG - TEMP_DIR: {TEMP_DIR}")
    print(f"DEBUG - video_path: {video_path}")
    print(f"DEBUG - vtt_path: {vtt_path}")
    print(f"DEBUG - output_path: {output_path}")
    
    try:
        # Guardar archivos subidos
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        with open(vtt_path, "wb") as buffer:
            shutil.copyfileobj(vtt.file, buffer)
        
        # Obtener duración del video
        duration = get_media_duration(video_path)
        
        # Contar subtítulos
        subtitle_count = count_vtt_subtitles(vtt_path)
        
        # Crear video subtitulado
        create_subtitled_video(
            video_path, vtt_path, output_path,
            font_color, background_color, font_size, background_opacity,
            box_enabled, box_color
        )
        
        # Obtener tamaño del archivo resultante
        file_size = os.path.getsize(output_path)
        
        # Retornar información del video subtitulado
        return {
            "message": "Video subtitulado completado exitosamente",
            "duration": round(duration, 2),
            "subtitle_count": subtitle_count,
            "file_size": file_size,
            "download_url": f"/download-video/{output_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    finally:
        # Limpiar archivos temporales de entrada
        for temp_file_path in [video_path, vtt_path]:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

@app.get("/download-video/{filename}")
async def download_video(filename: str):
    """Endpoint para descargar videos subtitulados"""
    file_path = os.path.join(str(TEMP_DIR), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='video/mp4'
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)