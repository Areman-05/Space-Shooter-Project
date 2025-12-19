"""
Script para descargar recursos de audio e imágenes para Space Shooter
Algunos recursos requieren descarga manual debido a políticas de los sitios web.
"""

import os
import sys
import urllib.request
import urllib.error

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# Crear directorios si no existen
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def download_file(url, filepath, description):
    """Descarga un archivo de una URL"""
    try:
        print(f"Descargando {description}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ {description} descargado exitosamente en {filepath}")
        return True
    except urllib.error.URLError as e:
        print(f"✗ Error al descargar {description}: {e}")
        print(f"  URL: {url}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado al descargar {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("Descargador de Recursos para Space Shooter")
    print("=" * 60)
    print()
    
    # Recursos que se pueden descargar automáticamente
    # Nota: Muchos sitios requieren descarga manual
    resources = {
        # Efectos de sonido - URLs de ejemplo (requieren reemplazo con URLs reales)
        # Estos son ejemplos, necesitarás URLs reales de recursos CC0
        
        # Música de fondo - Ejemplos de sitios que permiten descarga directa
        # Nota: Necesitarás URLs reales de recursos CC0/libres
        
        # Imágenes - Ejemplos
        # Nota: Necesitarás URLs reales
    }
    
    print("NOTA: Muchos recursos requieren descarga manual.")
    print("Por favor, visita los siguientes sitios y descarga los recursos:")
    print()
    
    print("=" * 60)
    print("RECURSOS RECOMENDADOS - DESCARGA MANUAL")
    print("=" * 60)
    print()
    
    print("1. OPENGAMEART.ORG (Recomendado)")
    print("   URL: https://opengameart.org")
    print("   Buscar:")
    print("   - 'space shooter music' para música de fondo")
    print("   - 'laser shoot' para sonidos de disparo")
    print("   - 'explosion' para sonidos de explosión")
    print("   - 'powerup' para sonidos de power-ups")
    print()
    
    print("2. FREESOUND.ORG")
    print("   URL: https://freesound.org")
    print("   Buscar:")
    print("   - 'space explosion' (filtro: CC0)")
    print("   - 'laser gun' (filtro: CC0)")
    print("   - 'powerup' (filtro: CC0)")
    print("   - 'shield' (filtro: CC0)")
    print()
    
    print("3. PIXABAY")
    print("   URL: https://pixabay.com/es/sound-effects/")
    print("   Buscar: 'space', 'laser', 'explosion', 'game'")
    print()
    
    print("=" * 60)
    print("ARCHIVOS NECESARIOS")
    print("=" * 60)
    print()
    print("Coloca los archivos descargados en las siguientes carpetas:")
    print()
    print(f"SONIDOS: {SOUNDS_DIR}")
    print("  - menu_music.ogg o menu_music.mp3")
    print("  - game_music.ogg o game_music.mp3")
    print("  - explosion.wav")
    print("  - powerup.wav")
    print("  - shield_activate.wav")
    print("  - missile_launch.wav")
    print("  - wave_complete.wav")
    print()
    print(f"IMAGENES: {IMAGES_DIR}")
    print("  - (Opcional) Imágenes adicionales para fondos")
    print()
    
    print("=" * 60)
    print("ENLACES DIRECTOS RECOMENDADOS")
    print("=" * 60)
    print()
    print("Busca estos recursos específicos:")
    print()
    print("MÚSICA DE FONDO:")
    print("  - OpenGameArt: https://opengameart.org/content/space-shooter-music")
    print("  - Buscar: 'space', 'sci-fi', 'retro'")
    print()
    print("EFECTOS DE SONIDO:")
    print("  - Freesound: https://freesound.org/browse/tags/space/")
    print("  - Freesound: https://freesound.org/browse/tags/laser/")
    print("  - Freesound: https://freesound.org/browse/tags/explosion/")
    print()
    
    # Intentar descargar algunos recursos de ejemplo si hay URLs disponibles
    # (Esto requeriría URLs reales de recursos CC0)
    
    print("=" * 60)
    print("INSTRUCCIONES")
    print("=" * 60)
    print()
    print("1. Visita los sitios web mencionados arriba")
    print("2. Busca los recursos usando los términos sugeridos")
    print("3. Filtra por licencia CC0 (dominio público) cuando sea posible")
    print("4. Descarga los archivos y colócalos en las carpetas indicadas")
    print("5. Asegúrate de que los nombres coincidan con los esperados")
    print()
    print("El juego funcionará sin estos archivos, pero mejorará")
    print("significativamente la experiencia con ellos.")
    print()

if __name__ == "__main__":
    main()

