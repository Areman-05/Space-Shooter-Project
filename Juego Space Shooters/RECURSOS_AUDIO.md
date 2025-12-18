# Recursos de Audio para Space Shooter

## Fuentes recomendadas para descargar recursos gratuitos:

### 1. **OpenGameArt.org** (Recomendado - CC0/CC-BY)
- URL: https://opengameart.org
- Buscar: "space shooter music", "sci-fi background", "laser shoot"
- Licencia: Generalmente CC0 (dominio publico) o CC-BY (atribucion)
- Formatos: OGG, WAV, MP3

### 2. **Freesound.org** (Recomendado - CC0)
- URL: https://freesound.org
- Buscar: "space explosion", "laser gun", "powerup", "shield activate"
- Licencia: CC0 (sin atribucion necesaria)
- Formatos: WAV, MP3

### 3. **Pixabay** (Gratis - Sin atribucion)
- URL: https://pixabay.com/es/sound-effects/
- Buscar: "space", "laser", "explosion", "game"
- Licencia: Pixabay License (gratis para uso comercial)
- Formatos: MP3, WAV

### 4. **SoundDino** (Gratis)
- URL: https://sounddino.com/es/effects/
- Buscar: "game", "sci-fi", "cosmic"
- Licencia: Gratis con atribucion
- Formatos: WAV, MP3

## Archivos necesarios para el juego:

### Música de fondo:
- `menu_music.ogg` o `menu_music.mp3` - Música para el menú principal
- `game_music.ogg` o `game_music.mp3` - Música durante el juego

### Efectos de sonido:
- `explosion.wav` - Sonido de explosión
- `powerup.wav` - Sonido al recoger power-up
- `shield_activate.wav` - Sonido al activar escudo
- `missile_launch.wav` - Sonido al lanzar misil
- `wave_complete.wav` - Sonido al completar onda

## Instrucciones:

1. Descarga los archivos de las fuentes recomendadas
2. Colócalos en la carpeta `./sounds/`
3. Asegúrate de que los nombres coincidan con los que espera el código
4. Si usas otros nombres, actualiza las referencias en `main.py`

## Notas:
- Pygame soporta mejor archivos OGG y WAV
- Para música de fondo, OGG es recomendado (mejor compresion)
- Para efectos cortos, WAV es mejor (sin compresion, respuesta inmediata)
- Mantén los archivos pequeños para mejor rendimiento

