import pygame
import random
import math
import os
from pygame.locals import *

# Obtener el directorio raíz del proyecto (un nivel arriba del script)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Cargar efectos de sonido (con manejo de errores si no existen)
try:
    shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "alienshoot1.wav"))
except:
    shoot_sound = None

try:
    start_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "start.ogg"))
except:
    start_sound = None

# Efectos de sonido adicionales (opcionales)
try:
    explosion_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "explosion.wav"))
except:
    explosion_sound = None

try:
    powerup_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "powerup.wav"))
except:
    powerup_sound = None

try:
    shield_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "shield_activate.wav"))
except:
    shield_sound = None

try:
    missile_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "missile_launch.wav"))
except:
    missile_sound = None

try:
    wave_complete_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "wave_complete.wav"))
except:
    wave_complete_sound = None

# Música de fondo (opcional)
menu_music_path = os.path.join(BASE_DIR, "sounds", "menu_music.ogg")
game_music_path = os.path.join(BASE_DIR, "sounds", "game_music.ogg")

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (255, 0, 255)

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)
tiny_font = pygame.font.SysFont("Arial", 16)

# Fuente grande para título arcade
try:
    arcade_font_large = pygame.font.Font(None, 72)
    arcade_font_medium = pygame.font.Font(None, 48)
except:
    arcade_font_large = pygame.font.SysFont("Arial", 72)
    arcade_font_medium = pygame.font.SysFont("Arial", 48)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, "images", "DurrrSpaceShip.png"))
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.base_speed = 2
        self.speed = self.base_speed
        self.lives = 3
        
        # Power-ups
        self.shield_active = False
        self.shield_time = 0
        self.speed_boost_active = False
        self.speed_boost_time = 0
        self.weapon_type = "normal"  # normal, rapid, spread, laser
        self.weapon_time = 0
        self.missiles_available = 0
        
        # Cooldowns
        self.shoot_cooldown = 0
        self.missile_cooldown = 0

    def update(self, score):
        base_speed = self.base_speed + (score // 150)
        if self.speed_boost_active:
            self.speed = base_speed * 2.5
        else:
            self.speed = base_speed
            
        # Actualizar timers
        if self.shield_active:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield_active = False
                
        if self.speed_boost_active:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost_active = False
                
        if self.weapon_type != "normal":
            self.weapon_time -= 1
            if self.weapon_time <= 0:
                self.weapon_type = "normal"
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
    
    def activate_shield(self, duration=600):
        self.shield_active = True
        self.shield_time = duration
    
    def activate_speed_boost(self, duration=600):
        self.speed_boost_active = True
        self.speed_boost_time = duration
    
    def activate_weapon(self, weapon_type, duration=600):
        self.weapon_type = weapon_type
        self.weapon_time = duration
    
    def add_missiles(self, count=3):
        self.missiles_available += count
    
    def draw_shield(self, surface):
        if self.shield_active:
            time = pygame.time.get_ticks() / 100
            shield_alpha = int(128 + 127 * math.sin(time))
            shield_radius = max(self.rect.width, self.rect.height) // 2 + 10
            shield_surface = pygame.Surface((shield_radius * 2 + 20, shield_radius * 2 + 20), pygame.SRCALPHA)
            center = (shield_radius + 10, shield_radius + 10)
            
            # Círculo exterior pulsante
            for i in range(3):
                alpha = int(shield_alpha * (1 - i * 0.3))
                radius = shield_radius + i * 3 + int(5 * math.sin(time + i))
                pygame.draw.circle(shield_surface, (0, 200, 255, alpha), center, radius, 2)
            
            surface.blit(shield_surface, (self.rect.centerx - shield_radius - 10, 
                                        self.rect.centery - shield_radius - 10))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color=RED, size=(5, 10), angle=0):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.angle = angle
        self.speed_x = speed * math.sin(math.radians(angle))
        self.speed_y = speed * math.cos(math.radians(angle))

    def update(self):
        if self.angle == 0:
            self.rect.y += self.speed
        else:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 15))
        self.image.fill(ORANGE)
        pygame.draw.polygon(self.image, YELLOW, [(4, 0), (0, 15), (8, 15)])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -8
        self.explosion_radius = 60

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
    
    def explode(self):
        return self.explosion_radius

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, "images", "Asteroid Brown.png"))
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type):
        super().__init__()
        self.power_type = power_type  # shield, speed, rapid, spread, laser, missile
        self.base_image = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        colors = {
            "shield": CYAN,
            "speed": GREEN,
            "rapid": YELLOW,
            "spread": PURPLE,
            "laser": RED,
            "missile": ORANGE
        }
        
        color = colors.get(power_type, WHITE)
        pygame.draw.circle(self.base_image, color, (15, 15), 14)
        pygame.draw.circle(self.base_image, WHITE, (15, 15), 12, 2)
        pygame.draw.circle(self.base_image, color, (15, 15), 8)
        
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 3
        self.rotation = 0
        self.pulse = 0

    def update(self):
        self.rect.y += self.speed
        self.rotation += 5
        self.pulse += 0.2
        if self.rect.top > HEIGHT:
            self.kill()
    
    def draw(self, surface):
        # Efecto de pulso
        pulse_size = 1 + 0.1 * math.sin(self.pulse)
        scaled_image = pygame.transform.scale(self.base_image, 
                                             (int(30 * pulse_size), int(30 * pulse_size)))
        rotated_image = pygame.transform.rotate(scaled_image, self.rotation)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)

class Explosion:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius
        self.life = 20
        self.particles = []
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle),
                'life': random.randint(10, 20),
                'color': random.choice([RED, ORANGE, YELLOW])
            })
    
    def update(self):
        self.life -= 1
        self.radius = int(self.max_radius * (self.life / 20))
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
        return self.life > 0
    
    def draw(self, surface):
        if self.radius > 0:
            for i in range(3):
                alpha = int(255 * (self.life / 20))
                color = (255, min(100 + i * 50, 255), 0, alpha)
                pygame.draw.circle(surface, color[:3], (int(self.x), int(self.y)), 
                                 self.radius - i * 5)
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / 20))
                size = max(1, int(3 * (particle['life'] / 20)))
                pygame.draw.circle(surface, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(10, 20)
        self.color = color
        self.size = random.randint(2, 4)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 20))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 2)
        self.brightness = random.randint(150, 255)
    
    def update(self, player_speed):
        self.y += self.speed + player_speed * 0.1
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

def show_splash_screen():
    """Pantalla de carga arcade ultra mejorada con efectos visuales épicos"""
    clock_splash = pygame.time.Clock()
    splash_duration = 4000  # 4 segundos para disfrutar los efectos
    start_time = pygame.time.get_ticks()
    
    # Crear estrellas para el fondo (más estrellas)
    splash_stars = [Star() for _ in range(200)]
    
    # Partículas arcade mejoradas
    splash_particles = []
    for _ in range(50):
        splash_particles.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-3, 3),
            'size': random.randint(3, 8),
            'color': random.choice([CYAN, YELLOW, GREEN, PURPLE, ORANGE, RED]),
            'life': random.randint(40, 80),
            'glow': random.uniform(0.5, 1.5)
        })
    
    # Partículas de energía que orbitan
    energy_particles = []
    for _ in range(20):
        angle = random.uniform(0, 2 * math.pi)
        energy_particles.append({
            'angle': angle,
            'radius': random.uniform(100, 200),
            'speed': random.uniform(0.02, 0.05),
            'size': random.randint(2, 4),
            'color': random.choice([CYAN, YELLOW])
        })
    
    # Efectos de scanlines (líneas de escaneo retro)
    scanline_offset = 0
    
    # Intentar cargar imagen de fondo
    background_image = None
    try:
        bg_path = os.path.join(BASE_DIR, "images", "astrominer.png")
        if os.path.exists(bg_path):
            bg_img = pygame.image.load(bg_path)
            background_image = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    except:
        pass
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        
        if elapsed >= splash_duration:
            running = False
            break
        
        clock_splash.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                running = False
                break
        
        # Actualizar estrellas (más rápido)
        for star in splash_stars:
            star.update(3)
        
        # Actualizar partículas arcade
        for particle in splash_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['glow'] += 0.1
            if particle['life'] <= 0:
                particle['x'] = random.randint(0, WIDTH)
                particle['y'] = random.randint(0, HEIGHT)
                particle['life'] = random.randint(40, 80)
                particle['vx'] = random.uniform(-3, 3)
                particle['vy'] = random.uniform(-3, 3)
        
        # Actualizar partículas de energía orbitales
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        for particle in energy_particles:
            particle['angle'] += particle['speed']
            particle['radius'] += math.sin(elapsed / 500) * 0.5
        
        # Actualizar scanlines
        scanline_offset = (scanline_offset + 2) % 4
        
        # Dibujar fondo
        screen.fill(BLACK)
        
        # Dibujar imagen de fondo si existe (con efecto de pulso)
        if background_image:
            pulse = 0.3 + 0.2 * math.sin(elapsed / 300)
            alpha = int(40 * pulse)
            bg_surface = background_image.copy()
            bg_surface.set_alpha(alpha)
            # Efecto de zoom sutil
            zoom = 1.0 + 0.05 * math.sin(elapsed / 400)
            zoomed = pygame.transform.scale(bg_surface, 
                                          (int(WIDTH * zoom), int(HEIGHT * zoom)))
            offset_x = (zoomed.get_width() - WIDTH) // 2
            offset_y = (zoomed.get_height() - HEIGHT) // 2
            screen.blit(zoomed, (-offset_x, -offset_y))
        
        # Dibujar estrellas con efecto de movimiento
        for star in splash_stars:
            star.draw(screen)
        
        # Dibujar partículas arcade con efecto de brillo
        for particle in splash_particles:
            if particle['life'] > 0:
                size = int(particle['size'] * (1 + 0.3 * math.sin(particle['glow'])))
                glow_size = size + 2
                # Brillo exterior
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                glow_alpha = int(100 * (particle['life'] / 80))
                glow_color = (*particle['color'], glow_alpha)
                pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
                screen.blit(glow_surface, (int(particle['x']) - glow_size, int(particle['y']) - glow_size))
                # Partícula principal
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
        
        # Dibujar partículas de energía orbitales
        for particle in energy_particles:
            x = center_x + particle['radius'] * math.cos(particle['angle'])
            y = center_y + particle['radius'] * math.sin(particle['angle'])
            size = particle['size'] + int(2 * math.sin(elapsed / 200 + particle['angle']))
            # Brillo
            glow_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*particle['color'], 100), 
                             (size * 1.5, size * 1.5), size * 1.5)
            screen.blit(glow_surface, (int(x) - size * 1.5, int(y) - size * 1.5))
            pygame.draw.circle(screen, particle['color'], (int(x), int(y)), size)
        
        # Efecto de parpadeo arcade mejorado
        blink = int(255 * (0.8 + 0.2 * math.sin(elapsed / 100)))
        blink_fast = int(255 * (0.7 + 0.3 * math.sin(elapsed / 50)))
        
        # Título principal "SPACE SHOOTERS" con efectos épicos
        title_text = "SPACE SHOOTERS"
        title_y = HEIGHT // 3
        
        # Efecto de distorsión/ondulación en el texto
        wave_offset = int(5 * math.sin(elapsed / 200))
        
        # Múltiples capas de sombra para profundidad
        for layer in range(5, 0, -1):
            shadow_alpha = 50 + layer * 10
            shadow_color = (0, 0, 0, shadow_alpha)
            for offset_x in range(-layer, layer + 1):
                for offset_y in range(-layer, layer + 1):
                    if offset_x != 0 or offset_y != 0:
                        shadow = arcade_font_large.render(title_text, True, (0, 0, 0))
                        shadow_surface = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
                        shadow_surface.set_alpha(shadow_alpha)
                        shadow_surface.blit(shadow, (0, 0))
                        screen.blit(shadow_surface, 
                                  (WIDTH // 2 - shadow.get_width() // 2 + offset_x, 
                                   title_y + offset_y + wave_offset))
        
        # Capa exterior con múltiples colores neón
        colors = [
            (blink, 0, 255),      # Magenta
            (0, blink, 255),      # Cyan
            (blink, blink, 255),   # Azul brillante
        ]
        color_index = int((elapsed / 200) % len(colors))
        outer_color = colors[color_index]
        
        # Brillo exterior pulsante
        for i in range(3):
            glow_alpha = int((100 - i * 30) * (0.5 + 0.5 * math.sin(elapsed / 150)))
            outer_glow = arcade_font_large.render(title_text, True, outer_color)
            glow_surface = pygame.Surface(outer_glow.get_size(), pygame.SRCALPHA)
            glow_surface.set_alpha(glow_alpha)
            glow_surface.blit(outer_glow, (0, 0))
            offset = i * 2
            screen.blit(glow_surface, 
                      (WIDTH // 2 - outer_glow.get_width() // 2 - offset, 
                       title_y - offset + wave_offset))
        
        # Capa principal con efecto de arcoíris
        hue = (elapsed / 50) % 360
        r = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue))))
        g = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue + 120))))
        b = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue + 240))))
        neon_color = (r, g, b)
        
        main_text = arcade_font_large.render(title_text, True, neon_color)
        screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2, 
                               title_y + wave_offset))
        
        # Capa interior con brillo intenso
        inner_glow = arcade_font_large.render(title_text, True, (255, 255, 255))
        inner_surface = pygame.Surface(inner_glow.get_size(), pygame.SRCALPHA)
        inner_alpha = int(blink_fast * 0.6)
        inner_surface.set_alpha(inner_alpha)
        inner_surface.blit(inner_glow, (0, 0))
        screen.blit(inner_surface, (WIDTH // 2 - main_text.get_width() // 2, 
                                   title_y + wave_offset))
        
        # Efecto de "carga" animado mejorado
        loading_text = "CARGANDO"
        dots = "." * (int(elapsed / 250) % 4)
        loading_full = loading_text + dots
        
        # Sombra múltiple para texto de carga
        for i in range(3):
            shadow_alpha = 100 - i * 30
            loading_shadow = small_font.render(loading_full, True, (0, 0, 0))
            shadow_surf = pygame.Surface(loading_shadow.get_size(), pygame.SRCALPHA)
            shadow_surf.set_alpha(shadow_alpha)
            shadow_surf.blit(loading_shadow, (0, 0))
            screen.blit(shadow_surf, 
                      (WIDTH // 2 - loading_shadow.get_width() // 2 + i, 
                       HEIGHT // 2 + 100 + i))
        
        # Texto de carga con efecto neón
        loading_alpha = int(150 + 105 * math.sin(elapsed / 150))
        loading_alpha = max(0, min(255, loading_alpha))  # Asegurar que esté entre 0 y 255
        loading_color = (0, loading_alpha, 255)
        loading_surface = small_font.render(loading_full, True, loading_color)
        screen.blit(loading_surface, (WIDTH // 2 - loading_surface.get_width() // 2, 
                                     HEIGHT // 2 + 100))
        
        # Barra de carga mejorada con efectos
        bar_width = 400
        bar_height = 30
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = HEIGHT // 2 + 150
        
        # Fondo de la barra con borde neón
        pygame.draw.rect(screen, (20, 20, 20), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # Borde neón pulsante
        border_glow = int(100 + 155 * math.sin(elapsed / 100))
        border_glow = max(0, min(255, border_glow))  # Asegurar que esté entre 0 y 255
        pygame.draw.rect(screen, (0, border_glow, 255), (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Barra de progreso con múltiples efectos
        progress = min(elapsed / splash_duration, 1.0)
        progress_width = int(bar_width * progress)
        
        # Gradiente animado en la barra
        for i in range(progress_width):
            hue_offset = (i + elapsed / 10) % 360
            r = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue_offset))))
            g = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue_offset + 120))))
            b = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue_offset + 240))))
            color = (r, g, b)
            pygame.draw.line(screen, color, 
                           (bar_x + i, bar_y), 
                           (bar_x + i, bar_y + bar_height))
        
        # Brillo deslizante en la barra
        if progress_width > 0:
            glow_pos = int(progress_width - 30 + 30 * math.sin(elapsed / 100))
            glow_pos = max(0, min(progress_width, glow_pos))
            glow_width = 40
            for i in range(glow_width):
                if glow_pos - i >= 0:
                    alpha = int(255 * (1 - i / glow_width))
                    glow_surface = pygame.Surface((1, bar_height), pygame.SRCALPHA)
                    glow_surface.fill((255, 255, 255, alpha))
                    screen.blit(glow_surface, (bar_x + glow_pos - i, bar_y))
        
        # Efectos de líneas arcade mejorados en los bordes
        line_thickness = 4
        line_length = 80
        line_speed = elapsed / 8
        
        # Líneas superiores e inferiores con efecto de brillo
        for i in range(0, WIDTH, 120):
            x = (i + line_speed) % (WIDTH + line_length) - line_length
            line_alpha = int(150 + 105 * math.sin((elapsed + i) / 200))
            line_color = (0, line_alpha, 255)
            pygame.draw.line(screen, line_color, (x, 0), (x + line_length, 0), line_thickness)
            pygame.draw.line(screen, line_color, (x, HEIGHT - 1), (x + line_length, HEIGHT - 1), line_thickness)
        
        # Líneas laterales
        for i in range(0, HEIGHT, 120):
            y = (i + line_speed) % (HEIGHT + line_length) - line_length
            line_alpha = int(150 + 105 * math.sin((elapsed + i) / 200))
            line_color = (0, line_alpha, 255)
            pygame.draw.line(screen, line_color, (0, y), (0, y + line_length), line_thickness)
            pygame.draw.line(screen, line_color, (WIDTH - 1, y), (WIDTH - 1, y + line_length), line_thickness)
        
        # Efecto de scanlines retro (líneas horizontales)
        scanline_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(scanline_offset, HEIGHT, 4):
            scanline_surface.fill((0, 0, 0, 30), (0, y, WIDTH, 1))
        screen.blit(scanline_surface, (0, 0))
        
        # Efecto de viñeta (oscurecimiento en los bordes)
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        center_x_v, center_y_v = WIDTH // 2, HEIGHT // 2
        max_dist = math.sqrt(center_x_v**2 + center_y_v**2)
        for x in range(0, WIDTH, 2):
            for y in range(0, HEIGHT, 2):
                dist = math.sqrt((x - center_x_v)**2 + (y - center_y_v)**2)
                alpha = int(50 * (dist / max_dist))
                if alpha > 0:
                    vignette.fill((0, 0, 0, alpha), (x, y, 2, 2))
        screen.blit(vignette, (0, 0))
        
        pygame.display.flip()
    
    # Fade out mejorado con efecto de desvanecimiento
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    for alpha in range(0, 255, 8):
        fade_surface.set_alpha(alpha)
        fade_surface.fill(BLACK)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(8)

def show_main_menu():
    # Reproducir música de menú si existe
    try:
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # -1 = loop infinito
    except:
        pass  # Si no existe el archivo, continuar sin música
    
    # Estrellas para el fondo del menú (más estrellas)
    menu_stars = [Star() for _ in range(150)]
    
    # Partículas flotantes para efecto arcade
    menu_particles = []
    for _ in range(40):
        menu_particles.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'vx': random.uniform(-1.5, 1.5),
            'vy': random.uniform(-1.5, 1.5),
            'size': random.randint(2, 5),
            'color': random.choice([CYAN, YELLOW, GREEN, PURPLE, ORANGE]),
            'life': random.randint(50, 100),
            'glow': random.uniform(0, 2 * math.pi)
        })
    
    # Partículas de energía orbitales alrededor del título
    title_particles = []
    for _ in range(15):
        angle = random.uniform(0, 2 * math.pi)
        title_particles.append({
            'angle': angle,
            'radius': random.uniform(80, 120),
            'speed': random.uniform(0.01, 0.03),
            'size': random.randint(2, 4),
            'color': random.choice([CYAN, YELLOW])
        })
    
    # Variables para animación
    menu_time = 0
    selected_option = 0  # 0 = jugar, 1 = comandos, 2 = salir
    option_animations = [0.0, 0.0, 0.0]  # Animación para cada opción
    
    while True:
        clock.tick(60)
        menu_time += 1
        
        # Actualizar estrellas (más rápido)
        for star in menu_stars:
            star.update(2)
        
        # Actualizar partículas flotantes
        for particle in menu_particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.5
            particle['glow'] += 0.05
            # Rebotar en los bordes
            if particle['x'] < 0 or particle['x'] > WIDTH:
                particle['vx'] *= -1
            if particle['y'] < 0 or particle['y'] > HEIGHT:
                particle['vy'] *= -1
            if particle['life'] <= 0:
                particle['x'] = random.randint(0, WIDTH)
                particle['y'] = random.randint(0, HEIGHT)
                particle['life'] = random.randint(50, 100)
        
        # Actualizar partículas orbitales del título
        title_center_x, title_center_y = WIDTH // 2, HEIGHT // 6 + 30
        for particle in title_particles:
            particle['angle'] += particle['speed']
            particle['radius'] += math.sin(menu_time / 100 + particle['angle']) * 0.3
        
        # Actualizar animaciones de opciones
        for i in range(len(option_animations)):
            if i == selected_option:
                option_animations[i] += 0.15
            else:
                option_animations[i] = max(0, option_animations[i] - 0.1)
        
        # Dibujar fondo
        screen.fill(BLACK)
        
        # Dibujar estrellas
        for star in menu_stars:
            star.draw(screen)
        
        # Dibujar partículas flotantes con brillo
        for particle in menu_particles:
            if particle['life'] > 0:
                size = int(particle['size'] * (1 + 0.2 * math.sin(particle['glow'])))
                # Brillo exterior
                glow_size = size + 3
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                glow_alpha = int(80 * (particle['life'] / 100))
                glow_color = (*particle['color'], glow_alpha)
                pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
                screen.blit(glow_surface, (int(particle['x']) - glow_size, int(particle['y']) - glow_size))
                # Partícula principal
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
        
        # Título del menú con efectos épicos
        title_text = "SPACE SHOOTERS"
        title_y = HEIGHT // 6
        
        # Efecto de parpadeo mejorado
        blink = int(255 * (0.8 + 0.2 * math.sin(menu_time / 40)))
        blink_fast = int(255 * (0.7 + 0.3 * math.sin(menu_time / 15)))
        
        # Efecto de distorsión sutil
        wave_offset = int(3 * math.sin(menu_time / 60))
        
        # Múltiples capas de sombra para profundidad
        for layer in range(4, 0, -1):
            shadow_alpha = 60 + layer * 15
            for offset_x in range(-layer, layer + 1):
                for offset_y in range(-layer, layer + 1):
                    if offset_x != 0 or offset_y != 0:
                        shadow = arcade_font_medium.render(title_text, True, (0, 0, 0))
                        shadow_surf = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
                        shadow_surf.set_alpha(shadow_alpha)
                        shadow_surf.blit(shadow, (0, 0))
                        screen.blit(shadow_surf, 
                                  (WIDTH // 2 - shadow.get_width() // 2 + offset_x, 
                                   title_y + offset_y + wave_offset))
        
        # Dibujar partículas orbitales alrededor del título
        for particle in title_particles:
            x = title_center_x + particle['radius'] * math.cos(particle['angle'])
            y = title_center_y + particle['radius'] * math.sin(particle['angle'])
            size = particle['size'] + int(2 * math.sin(menu_time / 30 + particle['angle']))
            # Brillo
            glow_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*particle['color'], 120), 
                             (size * 1.5, size * 1.5), size * 1.5)
            screen.blit(glow_surface, (int(x) - size * 1.5, int(y) - size * 1.5))
            pygame.draw.circle(screen, particle['color'], (int(x), int(y)), size)
        
        # Capa exterior con efecto arcoíris
        hue = (menu_time / 3) % 360
        r = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue))))
        g = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue + 120))))
        b = int(255 * (0.5 + 0.5 * math.sin(math.radians(hue + 240))))
        neon_color = (r, g, b)
        
        # Brillo exterior pulsante
        for i in range(2):
            glow_alpha = int((80 - i * 30) * (0.5 + 0.5 * math.sin(menu_time / 30)))
            outer_glow = arcade_font_medium.render(title_text, True, neon_color)
            glow_surf = pygame.Surface(outer_glow.get_size(), pygame.SRCALPHA)
            glow_surf.set_alpha(glow_alpha)
            glow_surf.blit(outer_glow, (0, 0))
            offset = i * 2
            screen.blit(glow_surf, 
                      (WIDTH // 2 - outer_glow.get_width() // 2 - offset, 
                       title_y - offset + wave_offset))
        
        # Título principal
        title_surface = arcade_font_medium.render(title_text, True, neon_color)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 
                                   title_y + wave_offset))
        
        # Brillo interior intenso
        inner_glow = arcade_font_medium.render(title_text, True, (255, 255, 255))
        glow_surface = pygame.Surface(inner_glow.get_size(), pygame.SRCALPHA)
        glow_surface.set_alpha(int(blink_fast * 0.4))
        glow_surface.blit(inner_glow, (0, 0))
        screen.blit(glow_surface, (WIDTH // 2 - title_surface.get_width() // 2, 
                                   title_y + wave_offset))
        
        # Opciones del menú con botones estilizados
        play_y = HEIGHT // 2 - 40
        commands_y = HEIGHT // 2 + 10
        exit_y = HEIGHT // 2 + 60
        
        # Dibujar botones con efectos
        button_width = 250
        button_height = 50
        button_spacing = 70
        
        # Botón JUGAR
        play_button_x = WIDTH // 2 - button_width // 2
        play_button_y = play_y - button_height // 2
        
        # Efecto de hover/selected
        play_scale = 1.0 + 0.1 * math.sin(option_animations[0])
        play_glow_intensity = int(100 + 155 * math.sin(option_animations[0] * 2)) if selected_option == 0 else 50
        play_glow_intensity = max(0, min(255, play_glow_intensity))
        
        # Fondo del botón con efecto neón
        button_glow_size = int(button_width * play_scale), int(button_height * play_scale)
        glow_offset_x = (button_glow_size[0] - button_width) // 2
        glow_offset_y = (button_glow_size[1] - button_height) // 2
        
        # Brillo del botón
        if selected_option == 0:
            glow_surf = pygame.Surface(button_glow_size, pygame.SRCALPHA)
            glow_color = (0, play_glow_intensity, 255, play_glow_intensity // 2)
            pygame.draw.rect(glow_surf, glow_color, (0, 0, button_glow_size[0], button_glow_size[1]))
            screen.blit(glow_surf, (play_button_x - glow_offset_x, play_button_y - glow_offset_y))
        
        # Fondo del botón (sin border_radius para compatibilidad)
        button_bg_color = (20, 20, 40) if selected_option == 0 else (15, 15, 25)
        pygame.draw.rect(screen, button_bg_color, 
                        (play_button_x, play_button_y, button_width, button_height))
        pygame.draw.rect(screen, (0, play_glow_intensity, 255), 
                        (play_button_x, play_button_y, button_width, button_height), 3)
        
        # Texto del botón
        play_text = "> JUGAR <" if selected_option == 0 else "  JUGAR  "
        play_color = (255, 255, 0) if selected_option == 0 else (200, 200, 200)
        play_color = (int(play_color[0] * (0.9 + 0.1 * math.sin(option_animations[0] * 3))),
                      int(play_color[1] * (0.9 + 0.1 * math.sin(option_animations[0] * 3))),
                      int(play_color[2] * (0.9 + 0.1 * math.sin(option_animations[0] * 3))))
        
        # Sombra del texto (centrada en el botón)
        for i in range(3):
            play_shadow = small_font.render(play_text, True, (0, 0, 0))
            shadow_surf = pygame.Surface(play_shadow.get_size(), pygame.SRCALPHA)
            shadow_surf.set_alpha(100 - i * 30)
            shadow_surf.blit(play_shadow, (0, 0))
            shadow_x = play_button_x + (button_width - play_shadow.get_width()) // 2 + i
            shadow_y = play_button_y + (button_height - play_shadow.get_height()) // 2 + i
            screen.blit(shadow_surf, (shadow_x, shadow_y))
        
        play_surface = small_font.render(play_text, True, play_color)
        # Centrar texto dentro del botón (vertical y horizontal)
        text_x = play_button_x + (button_width - play_surface.get_width()) // 2
        text_y = play_button_y + (button_height - play_surface.get_height()) // 2
        screen.blit(play_surface, (text_x, text_y))
        
        # Botón SALIR
        exit_button_x = WIDTH // 2 - button_width // 2
        exit_button_y = exit_y - button_height // 2
        
        # Botón COMANDOS
        commands_button_x = WIDTH // 2 - button_width // 2
        commands_button_y = commands_y - button_height // 2
        
        commands_glow_intensity = int(100 + 155 * math.sin(option_animations[1] * 2)) if selected_option == 1 else 50
        commands_glow_intensity = max(0, min(255, commands_glow_intensity))
        
        # Brillo del botón
        if selected_option == 1:
            commands_glow_size = int(button_width * (1.0 + 0.1 * math.sin(option_animations[1]))), int(button_height * (1.0 + 0.1 * math.sin(option_animations[1])))
            commands_glow_offset_x = (commands_glow_size[0] - button_width) // 2
            commands_glow_offset_y = (commands_glow_size[1] - button_height) // 2
            commands_glow_surf = pygame.Surface(commands_glow_size, pygame.SRCALPHA)
            commands_glow_color = (255, 165, 0, commands_glow_intensity // 2)
            pygame.draw.rect(commands_glow_surf, commands_glow_color, 
                           (0, 0, commands_glow_size[0], commands_glow_size[1]))
            screen.blit(commands_glow_surf, (commands_button_x - commands_glow_offset_x, commands_button_y - commands_glow_offset_y))
        
        # Fondo del botón
        commands_bg_color = (40, 30, 20) if selected_option == 1 else (25, 20, 15)
        pygame.draw.rect(screen, commands_bg_color, 
                        (commands_button_x, commands_button_y, button_width, button_height))
        pygame.draw.rect(screen, (255, commands_glow_intensity // 2, 0), 
                        (commands_button_x, commands_button_y, button_width, button_height), 3)
        
        # Texto del botón
        commands_text_str = "> COMANDOS <" if selected_option == 1 else "  COMANDOS  "
        commands_color = (255, 200, 100) if selected_option == 1 else (180, 180, 180)
        commands_color = (int(commands_color[0] * (0.9 + 0.1 * math.sin(option_animations[1] * 3))),
                         int(commands_color[1] * (0.9 + 0.1 * math.sin(option_animations[1] * 3))),
                         int(commands_color[2] * (0.9 + 0.1 * math.sin(option_animations[1] * 3))))
        
        # Sombra del texto (centrada en el botón)
        for i in range(3):
            commands_shadow = small_font.render(commands_text_str, True, (0, 0, 0))
            shadow_surf = pygame.Surface(commands_shadow.get_size(), pygame.SRCALPHA)
            shadow_surf.set_alpha(100 - i * 30)
            shadow_surf.blit(commands_shadow, (0, 0))
            commands_shadow_x = commands_button_x + (button_width - commands_shadow.get_width()) // 2 + i
            commands_shadow_y = commands_button_y + (button_height - commands_shadow.get_height()) // 2 + i
            screen.blit(shadow_surf, (commands_shadow_x, commands_shadow_y))
        
        commands_surface = small_font.render(commands_text_str, True, commands_color)
        commands_text_x = commands_button_x + (button_width - commands_surface.get_width()) // 2
        commands_text_y = commands_button_y + (button_height - commands_surface.get_height()) // 2
        screen.blit(commands_surface, (commands_text_x, commands_text_y))
        
        # Botón SALIR
        exit_button_x = WIDTH // 2 - button_width // 2
        exit_button_y = exit_y - button_height // 2
        
        exit_glow_intensity = int(100 + 155 * math.sin(option_animations[2] * 2)) if selected_option == 2 else 50
        exit_glow_intensity = max(0, min(255, exit_glow_intensity))
        
        # Brillo del botón
        if selected_option == 2:
            exit_glow_size = int(button_width * (1.0 + 0.1 * math.sin(option_animations[2]))), int(button_height * (1.0 + 0.1 * math.sin(option_animations[2])))
            exit_glow_offset_x = (exit_glow_size[0] - button_width) // 2
            exit_glow_offset_y = (exit_glow_size[1] - button_height) // 2
            exit_glow_surf = pygame.Surface(exit_glow_size, pygame.SRCALPHA)
            exit_glow_color = (255, 0, 0, exit_glow_intensity // 2)
            pygame.draw.rect(exit_glow_surf, exit_glow_color, 
                           (0, 0, exit_glow_size[0], exit_glow_size[1]))
            screen.blit(exit_glow_surf, (exit_button_x - exit_glow_offset_x, exit_button_y - exit_glow_offset_y))
        
        # Fondo del botón (sin border_radius para compatibilidad)
        exit_bg_color = (40, 20, 20) if selected_option == 2 else (25, 15, 15)
        pygame.draw.rect(screen, exit_bg_color, 
                        (exit_button_x, exit_button_y, button_width, button_height))
        pygame.draw.rect(screen, (255, exit_glow_intensity // 2, 0), 
                        (exit_button_x, exit_button_y, button_width, button_height), 3)
        
        # Texto del botón
        exit_text_str = "> SALIR <" if selected_option == 2 else "  SALIR  "
        exit_color = (255, 100, 100) if selected_option == 2 else (180, 180, 180)
        exit_color = (int(exit_color[0] * (0.9 + 0.1 * math.sin(option_animations[2] * 3))),
                     int(exit_color[1] * (0.9 + 0.1 * math.sin(option_animations[2] * 3))),
                     int(exit_color[2] * (0.9 + 0.1 * math.sin(option_animations[2] * 3))))
        
        # Sombra del texto (centrada en el botón)
        for i in range(3):
            exit_shadow = small_font.render(exit_text_str, True, (0, 0, 0))
            shadow_surf = pygame.Surface(exit_shadow.get_size(), pygame.SRCALPHA)
            shadow_surf.set_alpha(100 - i * 30)
            shadow_surf.blit(exit_shadow, (0, 0))
            exit_shadow_x = exit_button_x + (button_width - exit_shadow.get_width()) // 2 + i
            exit_shadow_y = exit_button_y + (button_height - exit_shadow.get_height()) // 2 + i
            screen.blit(shadow_surf, (exit_shadow_x, exit_shadow_y))
        
        exit_surface = small_font.render(exit_text_str, True, exit_color)
        # Centrar texto dentro del botón (vertical y horizontal)
        exit_text_x = exit_button_x + (button_width - exit_surface.get_width()) // 2
        exit_text_y = exit_button_y + (button_height - exit_surface.get_height()) // 2
        screen.blit(exit_surface, (exit_text_x, exit_text_y))
        
        # Efectos de borde arcade mejorados
        border_thickness = 3
        border_glow = int(80 + 100 * math.sin(menu_time / 25))
        border_glow = max(0, min(255, border_glow))
        border_glow_color = (0, border_glow, 255)
        
        # Bordes superiores e inferiores con efecto de brillo
        pygame.draw.rect(screen, border_glow_color, (0, 0, WIDTH, border_thickness))
        pygame.draw.rect(screen, border_glow_color, (0, HEIGHT - border_thickness, WIDTH, border_thickness))
        
        # Bordes laterales
        pygame.draw.rect(screen, border_glow_color, (0, 0, border_thickness, HEIGHT))
        pygame.draw.rect(screen, border_glow_color, (WIDTH - border_thickness, 0, border_thickness, HEIGHT))
        
        # Líneas decorativas en las esquinas
        corner_length = 30
        corner_thickness = 2
        corner_color = (0, border_glow, 255)
        
        # Esquinas superiores
        pygame.draw.line(screen, corner_color, (0, 0), (corner_length, 0), corner_thickness)
        pygame.draw.line(screen, corner_color, (0, 0), (0, corner_length), corner_thickness)
        pygame.draw.line(screen, corner_color, (WIDTH, 0), (WIDTH - corner_length, 0), corner_thickness)
        pygame.draw.line(screen, corner_color, (WIDTH, 0), (WIDTH, corner_length), corner_thickness)
        
        # Esquinas inferiores
        pygame.draw.line(screen, corner_color, (0, HEIGHT), (corner_length, HEIGHT), corner_thickness)
        pygame.draw.line(screen, corner_color, (0, HEIGHT), (0, HEIGHT - corner_length), corner_thickness)
        pygame.draw.line(screen, corner_color, (WIDTH, HEIGHT), (WIDTH - corner_length, HEIGHT), corner_thickness)
        pygame.draw.line(screen, corner_color, (WIDTH, HEIGHT), (WIDTH, HEIGHT - corner_length), corner_thickness)
        
        # Efecto de scanlines sutil
        scanline_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        scanline_offset = (menu_time // 2) % 4
        for y in range(scanline_offset, HEIGHT, 4):
            scanline_surface.fill((0, 0, 0, 15), (0, y, WIDTH, 1))
        screen.blit(scanline_surface, (0, 0))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    selected_option = (selected_option - 1) % 3
                    option_animations[selected_option] = 0
                elif event.key == K_DOWN or event.key == K_s:
                    selected_option = (selected_option + 1) % 3
                    option_animations[selected_option] = 0
                elif event.key == K_RETURN:
                    pygame.mixer.music.stop()
                    if start_sound:
                        start_sound.play()
                    if selected_option == 0:
                        return True
                    elif selected_option == 1:
                        show_commands_menu()
                    else:
                        pygame.quit()
                        exit()
                elif event.key == K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()

def show_commands_menu():
    """Pantalla de comandos con toda la informacion de controles y scroll"""
    menu_stars = [Star() for _ in range(100)]
    menu_time = 0
    back_selected = False
    scroll_offset = 0
    scroll_speed = 3
    
    # Informacion de comandos mejorada
    commands_info = [
        ("MOVIMIENTO:", True, (255, 200, 100)),
        ("", False, (200, 200, 200)),
        ("W / Flecha Arriba    -  Mover arriba", False, (220, 220, 220)),
        ("S / Flecha Abajo    -  Mover abajo", False, (220, 220, 220)),
        ("A / Flecha Izquierda  -  Mover izquierda", False, (220, 220, 220)),
        ("D / Flecha Derecha   -  Mover derecha", False, (220, 220, 220)),
        ("", False, (200, 200, 200)),
        ("ACCIONES:", True, (255, 200, 100)),
        ("", False, (200, 200, 200)),
        ("ESPACIO  -  Disparar", False, (220, 220, 220)),
        ("M       -  Lanzar misil", False, (220, 220, 220)),
        ("", False, (200, 200, 200)),
        ("POWER-UPS:", True, (255, 200, 100)),
        ("", False, (200, 200, 200)),
        ("Recoge los power-ups que caen:", False, (240, 240, 240)),
        ("", False, (200, 200, 200)),
        ("Escudo (Cyan)        -  Proteccion temporal", False, (150, 255, 255)),
        ("Velocidad (Verde)    -  Movimiento rapido", False, (150, 255, 150)),
        ("Arma Rapida (Amarillo) -  Disparo rapido", False, (255, 255, 150)),
        ("Arma Dispersion (Purpura) -  Disparo multiple", False, (255, 150, 255)),
        ("Arma Laser (Rojo)    -  Disparo potente", False, (255, 150, 150)),
        ("Misiles (Naranja)    -  Explosiones de area", False, (255, 200, 100)),
        ("", False, (200, 200, 200)),
        ("OBJETIVO:", True, (255, 200, 100)),
        ("", False, (200, 200, 200)),
        ("Destruye enemigos para ganar puntos", False, (220, 220, 220)),
        ("Completa ondas para avanzar", False, (220, 220, 220)),
        ("Manten combos para bonus de puntos", False, (220, 220, 220)),
        ("Sobrevive el mayor tiempo posible!", False, (255, 255, 150))
    ]
    
    # Calcular altura total del contenido
    line_height = 28
    total_content_height = len(commands_info) * line_height
    
    while True:
        clock.tick(60)
        menu_time += 1
        
        # Actualizar estrellas
        for star in menu_stars:
            star.update(1)
        
        # Dibujar fondo
        screen.fill(BLACK)
        
        # Dibujar estrellas
        for star in menu_stars:
            star.draw(screen)
        
        # Titulo
        title_text = "COMANDOS"
        title_y = 50
        blink = int(255 * (0.8 + 0.2 * math.sin(menu_time / 30)))
        
        # Sombra del titulo
        for offset_x in range(-2, 3):
            for offset_y in range(-2, 3):
                if offset_x != 0 or offset_y != 0:
                    shadow = arcade_font_medium.render(title_text, True, (0, 0, 0))
                    screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + offset_x, 
                                       title_y + offset_y))
        
        # Titulo principal
        title_color = (255, 165, 0)
        title_surface = arcade_font_medium.render(title_text, True, title_color)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, title_y))
        
        # Caja de informacion mejorada
        box_x = 40
        box_y = 110
        box_width = WIDTH - 80
        box_height = HEIGHT - 250
        box_padding = 30
        
        # Crear superficie para el contenido scrolleable
        content_surface = pygame.Surface((box_width - box_padding * 2, total_content_height))
        content_surface.fill((15, 15, 25))
        
        # Dibujar texto en la superficie de contenido
        y_offset = 0
        for line_data in commands_info:
            line_text, is_title, color = line_data
            if line_text:
                if is_title:
                    # Titulos en tamaño más grande
                    text_surface = small_font.render(line_text, True, color)
                    # Sombra para títulos
                    shadow = small_font.render(line_text, True, (0, 0, 0))
                    content_surface.blit(shadow, (2, y_offset + 2))
                    content_surface.blit(text_surface, (0, y_offset))
                else:
                    # Texto normal
                    text_surface = tiny_font.render(line_text, True, color)
                    content_surface.blit(text_surface, (0, y_offset))
            y_offset += line_height
        
        # Fondo de la caja con efecto de profundidad
        # Sombra
        shadow_offset = 5
        pygame.draw.rect(screen, (0, 0, 0), (box_x + shadow_offset, box_y + shadow_offset, box_width, box_height))
        # Fondo principal
        pygame.draw.rect(screen, (15, 15, 25), (box_x, box_y, box_width, box_height))
        # Borde interior
        pygame.draw.rect(screen, (30, 30, 40), (box_x + 2, box_y + 2, box_width - 4, box_height - 4), 1)
        # Borde neón pulsante
        box_glow = int(100 + 100 * math.sin(menu_time / 40))
        box_glow = max(0, min(255, box_glow))
        pygame.draw.rect(screen, (255, box_glow // 2, 0), (box_x, box_y, box_width, box_height), 4)
        
        # Calcular área visible del contenido
        visible_height = box_height - box_padding * 2
        max_scroll = max(0, total_content_height - visible_height)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        # Dibujar contenido scrolleable
        clip_rect = pygame.Rect(box_x + box_padding, box_y + box_padding, box_width - box_padding * 2, visible_height)
        screen.set_clip(clip_rect)
        screen.blit(content_surface, (box_x + box_padding, box_y + box_padding - scroll_offset))
        screen.set_clip(None)
        
        # Indicadores de scroll (flechas)
        if scroll_offset > 0:
            # Flecha arriba
            arrow_y = box_y + 10
            arrow_points = [(WIDTH // 2, arrow_y), (WIDTH // 2 - 10, arrow_y + 10), (WIDTH // 2 + 10, arrow_y + 10)]
            pygame.draw.polygon(screen, (255, 200, 100), arrow_points)
        
        if scroll_offset < max_scroll:
            # Flecha abajo
            arrow_y = box_y + box_height - 20
            arrow_points = [(WIDTH // 2, arrow_y + 10), (WIDTH // 2 - 10, arrow_y), (WIDTH // 2 + 10, arrow_y)]
            pygame.draw.polygon(screen, (255, 200, 100), arrow_points)
        
        # Boton Volver al Menu Principal
        back_button_width = 350
        back_button_height = 50
        back_button_x = WIDTH // 2 - back_button_width // 2
        back_button_y = HEIGHT - 90
        
        back_glow_intensity = int(100 + 155 * math.sin(menu_time / 20)) if back_selected else 50
        back_glow_intensity = max(0, min(255, back_glow_intensity))
        
        # Brillo del boton
        if back_selected:
            back_glow_size = int(back_button_width * 1.1), int(back_button_height * 1.1)
            back_glow_offset_x = (back_glow_size[0] - back_button_width) // 2
            back_glow_offset_y = (back_glow_size[1] - back_button_height) // 2
            back_glow_surf = pygame.Surface(back_glow_size, pygame.SRCALPHA)
            back_glow_color = (0, back_glow_intensity, 255, back_glow_intensity // 2)
            pygame.draw.rect(back_glow_surf, back_glow_color, 
                           (0, 0, back_glow_size[0], back_glow_size[1]))
            screen.blit(back_glow_surf, (back_button_x - back_glow_offset_x, back_button_y - back_glow_offset_y))
        
        # Fondo del boton
        back_bg_color = (20, 20, 40) if back_selected else (15, 15, 25)
        pygame.draw.rect(screen, back_bg_color, 
                        (back_button_x, back_button_y, back_button_width, back_button_height))
        pygame.draw.rect(screen, (0, back_glow_intensity, 255), 
                        (back_button_x, back_button_y, back_button_width, back_button_height), 3)
        
        # Texto del boton
        back_text = "> VOLVER AL MENU PRINCIPAL <" if back_selected else "  VOLVER AL MENU PRINCIPAL  "
        back_color = (255, 255, 0) if back_selected else (200, 200, 200)
        back_surface = small_font.render(back_text, True, back_color)
        back_text_x = back_button_x + (back_button_width - back_surface.get_width()) // 2
        back_text_y = back_button_y + (back_button_height - back_surface.get_height()) // 2
        screen.blit(back_surface, (back_text_x, back_text_y))
        
        # Bordes arcade
        border_thickness = 3
        border_glow = int(80 + 100 * math.sin(menu_time / 25))
        border_glow = max(0, min(255, border_glow))
        border_glow_color = (0, border_glow, 255)
        
        pygame.draw.rect(screen, border_glow_color, (0, 0, WIDTH, border_thickness))
        pygame.draw.rect(screen, border_glow_color, (0, HEIGHT - border_thickness, WIDTH, border_thickness))
        pygame.draw.rect(screen, border_glow_color, (0, 0, border_thickness, HEIGHT))
        pygame.draw.rect(screen, border_glow_color, (WIDTH - border_thickness, 0, border_thickness, HEIGHT))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if back_selected:
                        return
                elif event.key == K_ESCAPE:
                    return
                elif event.key == K_UP or event.key == K_w:
                    if scroll_offset > 0:
                        scroll_offset = max(0, scroll_offset - scroll_speed * 5)
                    else:
                        back_selected = True
                elif event.key == K_DOWN or event.key == K_s:
                    if scroll_offset < max_scroll:
                        scroll_offset = min(max_scroll, scroll_offset + scroll_speed * 5)
                    else:
                        back_selected = False
            if event.type == MOUSEBUTTONDOWN:
                # Detectar clic en el boton
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (back_button_x <= mouse_x <= back_button_x + back_button_width and
                    back_button_y <= mouse_y <= back_button_y + back_button_height):
                    return
            # Scroll con rueda del mouse
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - event.y * scroll_speed * 10))
                    
def show_controls_message():
    message = small_font.render("Controles: WASD para mover, ESPACIO para disparar", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT - 40))
    pygame.display.flip()
    pygame.time.wait(2000)

def main_game():
    # Reproducir música de juego si existe
    try:
        pygame.mixer.music.load(game_music_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)  # -1 = loop infinito
    except:
        pass  # Si no existe el archivo, continuar sin música
    
    player = Player()
    player_group = pygame.sprite.Group()
    player_group.add(player)

    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    explosions = []
    particles = []
    stars = [Star() for _ in range(100)]
    
    score = 0
    running = True
    powerup_spawn_timer = 0
    enemy_spawn_timer = 0
    combo = 0
    combo_timer = 0
    wave = 1
    enemies_killed_this_wave = 0
    enemies_per_wave = 10
    wave_complete = False
    wave_message_timer = 0

    while running:
        clock.tick(FPS)
        dt = clock.get_time()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if player.shoot_cooldown <= 0:
                        bullet_speed = -5 - (score // 150)
                        
                        if player.weapon_type == "normal":
                            bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed))
                            player.shoot_cooldown = 15
                            if shoot_sound:
                                shoot_sound.play()
                            
                        elif player.weapon_type == "rapid":
                            bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed))
                            player.shoot_cooldown = 5
                            if shoot_sound:
                                shoot_sound.play()
                            
                        elif player.weapon_type == "spread":
                            for angle in [-20, -10, 0, 10, 20]:
                                bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed, YELLOW, (6, 12), angle))
                            player.shoot_cooldown = 20
                            if shoot_sound:
                                shoot_sound.play()
                            
                        elif player.weapon_type == "laser":
                            bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed * 2, RED, (8, 20)))
                            player.shoot_cooldown = 10
                            if shoot_sound:
                                shoot_sound.play()
                
                if event.key == K_m and player.missiles_available > 0 and player.missile_cooldown <= 0:
                    missiles.add(Missile(player.rect.centerx, player.rect.top))
                    player.missiles_available -= 1
                    player.missile_cooldown = 30
                    if missile_sound:
                        missile_sound.play()
                    elif shoot_sound:
                        shoot_sound.play()
                    
                if event.key == K_ESCAPE:
                    pygame.mixer.music.stop()
                    running = False
        
        # Sistema de ondas
        if enemies_killed_this_wave >= enemies_per_wave and len(enemies) == 0:
            wave += 1
            enemies_killed_this_wave = 0
            enemies_per_wave = 10 + (wave - 1) * 5
            wave_complete = True
            wave_message_timer = 180  # 3 segundos
            # Añadir bonus de puntos por completar onda
            score += wave * 50
            # Sonido de onda completada
            if wave_complete_sound:
                wave_complete_sound.play()
        
        # Spawn de enemigos basado en la onda
        if not wave_complete:
            enemy_spawn_timer += 1
            base_spawn_rate = max(60 - (wave * 5), 15)
            if enemy_spawn_timer >= base_spawn_rate:
                enemies.add(Enemy())
                enemy_spawn_timer = 0
        elif wave_message_timer > 0:
            wave_message_timer -= 1
            if wave_message_timer == 0:
                wave_complete = False
        
        # Spawn de power-ups
        powerup_spawn_timer += 1
        if powerup_spawn_timer >= 600:  # Cada 10 segundos aproximadamente
            power_types = ["shield", "speed", "rapid", "spread", "laser", "missile"]
            powerups.add(PowerUp(random.choice(power_types)))
            powerup_spawn_timer = 0
        
        player_group.update(score)
        bullets.update()
        missiles.update()
        enemies.update()
        powerups.update()
        
        # Colisiones balas-enemigos
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for enemy in hits:
            combo += 1
            combo_timer = 180  # 3 segundos para mantener combo
            base_points = 10
            combo_bonus = min(combo * 2, 50)  # Bonus máximo de 50
            points = base_points + combo_bonus
            score += points
            enemies_killed_this_wave += 1
            # Sonido de explosión (volumen reducido)
            if explosion_sound:
                explosion_sound.set_volume(0.3)  # Reducir volumen al 30%
                explosion_sound.play()
            # Crear partículas al destruir enemigo
            for _ in range(5):
                particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, YELLOW))
            if not wave_complete:
                enemies.add(Enemy())
        
        # Actualizar combo timer
        if combo_timer > 0:
            combo_timer -= 1
        else:
            combo = 0
        
        # Colisiones misiles-enemigos (explosión)
        missile_hits = pygame.sprite.groupcollide(missiles, enemies, True, False)
        for missile in missile_hits:
            explosion_radius = missile.explode()
            explosions.append(Explosion(missile.rect.centerx, missile.rect.centery, explosion_radius))
            # Sonido de explosión grande (volumen reducido)
            if explosion_sound:
                explosion_sound.set_volume(0.3)  # Reducir volumen al 30%
                explosion_sound.play()
            # Destruir enemigos en el radio de explosión
            for enemy in enemies:
                dx = enemy.rect.centerx - missile.rect.centerx
                dy = enemy.rect.centery - missile.rect.centery
                distance = math.sqrt(dx*dx + dy*dy)
                if distance <= explosion_radius:
                    score += 10
                    enemies_killed_this_wave += 1
                    # Crear partículas
                    for _ in range(8):
                        particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, ORANGE))
                    enemy.kill()
            if not wave_complete:
                enemies.add(Enemy())
        
        # Actualizar explosiones y partículas
        explosions = [e for e in explosions if e.update()]
        particles = [p for p in particles if p.update()]
        
        # Actualizar estrellas
        player_speed_factor = player.speed if player.speed_boost_active else player.base_speed
        for star in stars:
            star.update(player_speed_factor)
        
        # Colisiones jugador-powerups
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            if powerup.power_type == "shield":
                player.activate_shield(600)
                if shield_sound:
                    shield_sound.play()
                elif powerup_sound:
                    powerup_sound.play()
            elif powerup.power_type == "speed":
                player.activate_speed_boost(600)
                if powerup_sound:
                    powerup_sound.play()
            elif powerup.power_type == "rapid":
                player.activate_weapon("rapid", 600)
                if powerup_sound:
                    powerup_sound.play()
            elif powerup.power_type == "spread":
                player.activate_weapon("spread", 600)
                if powerup_sound:
                    powerup_sound.play()
            elif powerup.power_type == "laser":
                player.activate_weapon("laser", 600)
                if powerup_sound:
                    powerup_sound.play()
            elif powerup.power_type == "missile":
                player.add_missiles(3)
                if powerup_sound:
                    powerup_sound.play()
        
        # Colisiones jugador-enemigos
        hits_player = pygame.sprite.spritecollide(player, enemies, True)
        if hits_player:
            if player.shield_active:
                player.shield_active = False
                player.shield_time = 0
                if explosion_sound:
                    explosion_sound.set_volume(0.3)  # Reducir volumen al 30%
                    explosion_sound.play()
            else:
                player.lives -= 1
                if explosion_sound:
                    explosion_sound.set_volume(0.3)  # Reducir volumen al 30%
                    explosion_sound.play()
                if player.lives == 0:
                    pygame.mixer.music.stop()
                    running = False
        
        # Dibujado
        screen.fill(BLACK)
        
        # Dibujar estrellas de fondo
        for star in stars:
            star.draw(screen)
        
        player_group.draw(screen)
        player.draw_shield(screen)
        bullets.draw(screen)
        missiles.draw(screen)
        enemies.draw(screen)
        
        # Dibujar power-ups con efecto personalizado
        for powerup in powerups:
            powerup.draw(screen)
        
        # Dibujar explosiones y partículas
        for explosion in explosions:
            explosion.draw(screen)
        for particle in particles:
            particle.draw(screen)
        
        # UI
        lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        score_text = font.render(f"Puntuacion: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Wave indicator
        wave_text = small_font.render(f"ONDA {wave}", True, CYAN)
        screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 10))
        progress_text = tiny_font.render(f"{enemies_killed_this_wave}/{enemies_per_wave}", True, WHITE)
        screen.blit(progress_text, (WIDTH - progress_text.get_width() - 10, 40))
        
        # Wave complete message
        if wave_message_timer > 0:
            wave_complete_text = font.render(f"ONDA {wave - 1} COMPLETADA!", True, YELLOW)
            text_rect = wave_complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(wave_complete_text, text_rect)
        
        # Combo indicator
        if combo > 1:
            combo_text = small_font.render(f"COMBO x{combo}!", True, YELLOW)
            screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 50))
        
        # Indicadores de power-ups
        y_offset = 100
        if player.shield_active:
            shield_text = tiny_font.render(f"ESCUDO: {player.shield_time // 60}s", True, CYAN)
            screen.blit(shield_text, (10, y_offset))
            y_offset += 20
        
        if player.speed_boost_active:
            speed_text = tiny_font.render(f"VELOCIDAD: {player.speed_boost_time // 60}s", True, GREEN)
            screen.blit(speed_text, (10, y_offset))
            y_offset += 20
        
        if player.weapon_type != "normal":
            weapon_names = {"rapid": "RAPIDO", "spread": "DISPERSION", "laser": "LASER"}
            weapon_text = tiny_font.render(f"ARMA: {weapon_names[player.weapon_type]} ({player.weapon_time // 60}s)", True, YELLOW)
            screen.blit(weapon_text, (10, y_offset))
            y_offset += 20
        
        if player.missiles_available > 0:
            missile_text = tiny_font.render(f"MISILES: {player.missiles_available} (M)", True, ORANGE)
            screen.blit(missile_text, (10, y_offset))
        
        # Instrucciones
        controls_text = tiny_font.render("ESPACIO: Disparar | M: Misil", True, WHITE)
        screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 40))
        
        pygame.display.flip()

def run_game():
    # Mostrar pantalla de carga al iniciar
    show_splash_screen()
    
    while True:
        if show_main_menu():
            main_game()
        else:
            break
    pygame.quit()
    exit()

run_game()