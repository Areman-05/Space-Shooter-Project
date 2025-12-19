"""
Script para generar sonidos básicos de ejemplo usando síntesis de audio
Estos son sonidos simples que puedes usar mientras descargas recursos mejores
Usa solo bibliotecas estándar de Python (sin numpy)
"""

import os
import sys
import math
import random
import struct

try:
    import wave
    HAS_WAVE = True
except ImportError:
    HAS_WAVE = False
    print("Advertencia: El módulo 'wave' no está disponible.")

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# Crear directorio si no existe
os.makedirs(SOUNDS_DIR, exist_ok=True)

def generate_explosion_sound():
    """Genera un sonido de explosión"""
    sample_rate = 22050
    duration = 0.5
    num_samples = int(sample_rate * duration)
    wave_data = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Ruido blanco filtrado
        noise = random.uniform(-0.5, 0.5)
        if i > 0:
            noise = 0.7 * noise + 0.3 * wave_data[i-1]
        # Envolvente exponencial
        envelope = math.exp(-t * 3)
        wave_data.append(noise * envelope)
    
    return wave_data, sample_rate

def generate_powerup_sound():
    """Genera un sonido de power-up"""
    sample_rate = 22050
    duration = 0.3
    num_samples = int(sample_rate * duration)
    wave_data = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Tono ascendente
        freq_start = 400
        freq_end = 800
        frequency = freq_start + (freq_end - freq_start) * (t / duration)
        
        sample = 0.4 * math.sin(2 * math.pi * frequency * t)
        sample += 0.2 * math.sin(2 * math.pi * frequency * 2 * t)  # Armónico
        
        # Envolvente
        if t < duration * 0.1:
            envelope = t / (duration * 0.1)
        elif t > duration * 0.8:
            envelope = (duration - t) / (duration * 0.2)
        else:
            envelope = 1.0
        wave_data.append(sample * envelope)
    
    return wave_data, sample_rate

def generate_shield_sound():
    """Genera un sonido de escudo activándose"""
    sample_rate = 22050
    duration = 0.4
    num_samples = int(sample_rate * duration)
    wave_data = []
    
    for i in range(num_samples):
        t = i / sample_rate
        frequency = 600
        sample = 0.3 * math.sin(2 * math.pi * frequency * t)
        sample += 0.2 * math.sin(2 * math.pi * frequency * 1.5 * t)
        
        # Modulación
        mod_freq = 10
        mod_depth = 50
        modulated = frequency + mod_depth * math.sin(2 * math.pi * mod_freq * t)
        sample += 0.1 * math.sin(2 * math.pi * modulated * t)
        
        # Envolvente
        envelope = math.exp(-t * 2)
        wave_data.append(sample * envelope)
    
    return wave_data, sample_rate

def generate_missile_sound():
    """Genera un sonido de misil"""
    sample_rate = 22050
    duration = 0.2
    num_samples = int(sample_rate * duration)
    wave_data = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Tono bajo que sube
        freq_start = 150
        freq_end = 300
        frequency = freq_start + (freq_end - freq_start) * (t / duration)
        
        sample = 0.4 * math.sin(2 * math.pi * frequency * t)
        sample += 0.2 * math.sin(2 * math.pi * frequency * 0.5 * t)
        
        # Envolvente
        if t > duration * 0.7:
            envelope = (duration - t) / (duration * 0.3)
        else:
            envelope = 1.0
        wave_data.append(sample * envelope)
    
    return wave_data, sample_rate

def generate_victory_sound():
    """Genera un sonido de victoria/onda completada"""
    sample_rate = 22050
    duration = 0.6
    num_samples = int(sample_rate * duration)
    wave_data = [0.0] * num_samples
    
    notes = [523, 659, 784, 1047]  # C, E, G, C (acorde mayor)
    note_duration = duration / len(notes)
    
    for i, note in enumerate(notes):
        start_idx = int(i * sample_rate * note_duration)
        end_idx = int((i + 1) * sample_rate * note_duration)
        if end_idx > num_samples:
            end_idx = num_samples
        
        for j in range(start_idx, end_idx):
            t = (j - start_idx) / sample_rate
            sample = 0.3 * math.sin(2 * math.pi * note * t)
            envelope = math.exp(-t * 2)
            wave_data[j] = sample * envelope
    
    return wave_data, sample_rate

def save_wav(wave_data, sample_rate, filename):
    """Guarda los datos de onda como archivo WAV"""
    if not HAS_WAVE:
        print(f"Error: No se puede guardar {filename} - módulo 'wave' no disponible")
        return False
    
    filepath = os.path.join(SOUNDS_DIR, filename)
    try:
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16 bits
            wav_file.setframerate(sample_rate)
            
            # Convertir a bytes (16-bit signed integers)
            for sample in wave_data:
                # Clamp y convertir a int16
                sample = max(-1.0, min(1.0, sample))
                int_sample = int(sample * 32767)
                wav_file.writeframes(struct.pack('<h', int_sample))
        
        print(f"[OK] Generado: {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] Error al guardar {filename}: {e}")
        return False

def main():
    print("=" * 60)
    print("Generador de Sonidos Básicos para Space Shooter")
    print("=" * 60)
    print()
    print("Este script genera sonidos simples de ejemplo.")
    print("Para mejores sonidos, descarga recursos de los sitios recomendados.")
    print()
    
    if not HAS_WAVE:
        print("ERROR: El módulo 'wave' no está disponible.")
        print("Este módulo debería estar incluido en Python estándar.")
        return
    
    print("Generando sonidos...")
    print()
    
    # Generar sonidos
    sounds = [
        ("explosion.wav", generate_explosion_sound),
        ("powerup.wav", generate_powerup_sound),
        ("shield_activate.wav", generate_shield_sound),
        ("missile_launch.wav", generate_missile_sound),
        ("wave_complete.wav", generate_victory_sound),
    ]
    
    # Reemplazar el sonido de disparo existente si el usuario quiere
    print("NOTA: No se generará 'alienshoot1.wav' para no sobrescribir el existente.")
    print("      Si quieres reemplazarlo, puedes usar generate_laser_sound() manualmente.")
    print()
    
    for filename, generator_func in sounds:
        wave_data, sample_rate = generator_func()
        save_wav(wave_data, sample_rate, filename)
    
    print()
    print("=" * 60)
    print("¡Sonidos generados!")
    print("=" * 60)
    print()
    print(f"Los archivos se han guardado en: {SOUNDS_DIR}")
    print()
    print("NOTA: Estos son sonidos básicos generados sintéticamente.")
    print("      Para mejores sonidos, descarga recursos de:")
    print("      - OpenGameArt.org")
    print("      - Freesound.org")
    print("      - Pixabay.com")
    print()

if __name__ == "__main__":
    main()

