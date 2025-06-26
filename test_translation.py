#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de traducción
"""

import os
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from main import translate_transcription_segments, openai_client
    print("✅ Importación exitosa de funciones de traducción")
except ImportError as e:
    print(f"❌ Error importando funciones: {e}")
    sys.exit(1)

def test_translation():
    """Prueba básica de traducción"""
    
    # Verificar que el cliente de OpenAI esté configurado
    if openai_client is None:
        print("⚠️  Cliente OpenAI no configurado - traducción no disponible")
        print("   Para habilitar traducción:")
        print("   1. Copia backend/.env.example a backend/.env")
        print("   2. Agrega tu OPENAI_API_KEY en el archivo .env")
        return False
    
    print("✅ Cliente OpenAI configurado correctamente")
    
    # Datos de prueba
    test_segments = [
        {
            'start': 0.0,
            'end': 2.5,
            'text': 'Hola, este es un mensaje de prueba.'
        },
        {
            'start': 2.5,
            'end': 5.0,
            'text': 'La traducción debería funcionar correctamente.'
        }
    ]
    
    try:
        print("🔄 Probando traducción de español a inglés...")
        translated_segments = translate_transcription_segments(
            test_segments, 
            'spanish', 
            'english'
        )
        
        print("✅ Traducción exitosa!")
        print("\nResultados:")
        for i, (original, translated) in enumerate(zip(test_segments, translated_segments)):
            print(f"  Segmento {i+1}:")
            print(f"    Original:  {original['text']}")
            print(f"    Traducido: {translated['text']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en traducción: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de traducción...\n")
    
    success = test_translation()
    
    if success:
        print("🎉 Todas las pruebas pasaron exitosamente!")
    else:
        print("💥 Algunas pruebas fallaron. Revisa la configuración.")
        sys.exit(1)