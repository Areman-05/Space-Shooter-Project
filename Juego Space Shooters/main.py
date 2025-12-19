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
    """Pantalla de carga arcade con efectos visuales"""
    clock_splash = pygame.time.Clock()
    splash_duration = 3000  # 3 segundos
    start_time = pygame.time.get_ticks()
    
    # Crear estrellas para el fondo
    splash_stars = [Star() for _ in range(150)]
    
    # Partículas para efecto arcade
    splash_particles = []
    for _ in range(30):
        splash_particles.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'size': random.randint(2, 5),
            'color': random.choice([CYAN, YELLOW, GREEN, PURPLE]),
            'life': random.randint(30, 60)
        })
    
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
        
        # Actualizar estrellas
        for star in splash_stars:
            star.update(2)
        
        # Actualizar partículas
        for particle in splash_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                particle['x'] = random.randint(0, WIDTH)
                particle['y'] = random.randint(0, HEIGHT)
                particle['life'] = random.randint(30, 60)
        
        # Dibujar fondo
        screen.fill(BLACK)
        
        # Dibujar imagen de fondo si existe (con transparencia)
        if background_image:
            alpha = int(50 + 30 * math.sin(elapsed / 200))
            bg_surface = background_image.copy()
            bg_surface.set_alpha(alpha)
            screen.blit(bg_surface, (0, 0))
        
        # Dibujar estrellas
        for star in splash_stars:
            star.draw(screen)
        
        # Dibujar partículas
        for particle in splash_particles:
            if particle['life'] > 0:
                size = particle['size'] + int(2 * math.sin(elapsed / 100))
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
        
        # Efecto de parpadeo arcade
        blink = int(255 * (0.7 + 0.3 * math.sin(elapsed / 150)))
        
        # Título principal "SPACE SHOOTERS" con efecto arcade
        title_text = "SPACE SHOOTERS"
        
        # Crear efecto de texto neón con múltiples capas
        title_y = HEIGHT // 3
        
        # Sombra negra (fondo)
        for offset_x in range(-3, 4):
            for offset_y in range(-3, 4):
                if offset_x != 0 or offset_y != 0:
                    shadow = arcade_font_large.render(title_text, True, (0, 0, 0))
                    screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + offset_x, 
                                       title_y + offset_y))
        
        # Capa exterior (brillo)
        outer_glow = arcade_font_large.render(title_text, True, (blink, blink, 255))
        screen.blit(outer_glow, (WIDTH // 2 - outer_glow.get_width() // 2, title_y))
        
        # Capa principal (color neón)
        neon_color = (0, blink, blink)
        main_text = arcade_font_large.render(title_text, True, neon_color)
        screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2, title_y))
        
        # Capa interior (brillo intenso)
        inner_glow = arcade_font_large.render(title_text, True, (255, 255, 255))
        inner_surface = pygame.Surface(inner_glow.get_size(), pygame.SRCALPHA)
        inner_surface.set_alpha(int(blink * 0.5))
        inner_surface.blit(inner_glow, (0, 0))
        screen.blit(inner_surface, (WIDTH // 2 - main_text.get_width() // 2, title_y))
        
        # Efecto de "carga" animado
        loading_text = "CARGANDO"
        dots = "." * (int(elapsed / 300) % 4)
        loading_full = loading_text + dots
        
        # Sombra para texto de carga
        loading_shadow = small_font.render(loading_full, True, (0, 0, 0))
        screen.blit(loading_shadow, (WIDTH // 2 - loading_shadow.get_width() // 2 + 2, 
                                    HEIGHT // 2 + 100 + 2))
        
        # Texto de carga con efecto parpadeante
        loading_alpha = int(150 + 105 * math.sin(elapsed / 200))
        loading_color = (loading_alpha, loading_alpha, loading_alpha)
        loading_surface = small_font.render(loading_full, True, loading_color)
        screen.blit(loading_surface, (WIDTH // 2 - loading_surface.get_width() // 2, 
                                     HEIGHT // 2 + 100))
        
        # Barra de carga animada
        bar_width = 300
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = HEIGHT // 2 + 150
        
        # Fondo de la barra
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Barra de progreso
        progress = min(elapsed / splash_duration, 1.0)
        progress_width = int(bar_width * progress)
        
        # Efecto de gradiente en la barra
        for i in range(progress_width):
            color_intensity = int(255 * (1 - i / bar_width))
            color = (0, color_intensity, 255)
            pygame.draw.line(screen, color, 
                           (bar_x + i, bar_y), 
                           (bar_x + i, bar_y + bar_height))
        
        # Brillo en la barra
        if progress_width > 0:
            glow_width = min(20, progress_width)
            for i in range(glow_width):
                alpha = int(255 * (1 - i / glow_width))
                glow_surface = pygame.Surface((1, bar_height), pygame.SRCALPHA)
                glow_surface.fill((255, 255, 255, alpha))
                screen.blit(glow_surface, (bar_x + progress_width - i, bar_y))
        
        # Efectos de líneas arcade en los bordes
        line_thickness = 3
        line_length = 50
        line_speed = elapsed / 10
        
        # Líneas superiores
        for i in range(0, WIDTH, 100):
            x = (i + line_speed) % (WIDTH + line_length) - line_length
            pygame.draw.line(screen, CYAN, (x, 0), (x + line_length, 0), line_thickness)
            pygame.draw.line(screen, CYAN, (x, HEIGHT - 1), (x + line_length, HEIGHT - 1), line_thickness)
        
        # Líneas laterales
        for i in range(0, HEIGHT, 100):
            y = (i + line_speed) % (HEIGHT + line_length) - line_length
            pygame.draw.line(screen, CYAN, (0, y), (0, y + line_length), line_thickness)
            pygame.draw.line(screen, CYAN, (WIDTH - 1, y), (WIDTH - 1, y + line_length), line_thickness)
        
        pygame.display.flip()
    
    # Fade out
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    for alpha in range(0, 255, 10):
        fade_surface.set_alpha(alpha)
        fade_surface.fill(BLACK)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)

def show_main_menu():
    # Reproducir música de menú si existe
    try:
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # -1 = loop infinito
    except:
        pass  # Si no existe el archivo, continuar sin música
    
    # Estrellas para el fondo del menú
    menu_stars = [Star() for _ in range(100)]
    
    # Variables para animación
    menu_time = 0
    selected_option = 0  # 0 = jugar, 1 = salir
    
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
        
        # Título del menú con efecto arcade
        title_text = "SPACE SHOOTERS"
        title_y = HEIGHT // 6
        
        # Efecto de parpadeo para el título
        blink = int(255 * (0.8 + 0.2 * math.sin(menu_time / 30)))
        
        # Sombra del título
        for offset_x in range(-2, 3):
            for offset_y in range(-2, 3):
                if offset_x != 0 or offset_y != 0:
                    shadow = arcade_font_medium.render(title_text, True, (0, 0, 0))
                    screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + offset_x, 
                                       title_y + offset_y))
        
        # Título principal con efecto neón
        neon_color = (0, blink, 255)
        title_surface = arcade_font_medium.render(title_text, True, neon_color)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, title_y))
        
        # Brillo interior
        inner_glow = arcade_font_medium.render(title_text, True, (255, 255, 255))
        glow_surface = pygame.Surface(inner_glow.get_size(), pygame.SRCALPHA)
        glow_surface.set_alpha(int(blink * 0.3))
        glow_surface.blit(inner_glow, (0, 0))
        screen.blit(glow_surface, (WIDTH // 2 - title_surface.get_width() // 2, title_y))
        
        # Opciones del menú
        play_text = "> JUGAR <" if selected_option == 0 else "  JUGAR  "
        exit_text = "> SALIR <" if selected_option == 1 else "  SALIR  "
        
        # Efecto de parpadeo para la opción seleccionada
        if selected_option == 0:
            option_color = (255, 255, 0) if int(menu_time / 10) % 2 == 0 else (200, 200, 0)
        else:
            option_color = WHITE
        
        play_surface = small_font.render(play_text, True, option_color)
        play_y = HEIGHT // 2 - 30
        
        # Sombra para texto de jugar
        play_shadow = small_font.render(play_text, True, (0, 0, 0))
        screen.blit(play_shadow, (WIDTH // 2 - play_surface.get_width() // 2 + 2, play_y + 2))
        screen.blit(play_surface, (WIDTH // 2 - play_surface.get_width() // 2, play_y))
        
        if selected_option == 1:
            option_color = (255, 255, 0) if int(menu_time / 10) % 2 == 0 else (200, 200, 0)
        else:
            option_color = WHITE
        
        exit_surface = small_font.render(exit_text, True, option_color)
        exit_y = HEIGHT // 2 + 30
        
        # Sombra para texto de salir
        exit_shadow = small_font.render(exit_text, True, (0, 0, 0))
        screen.blit(exit_shadow, (WIDTH // 2 - exit_surface.get_width() // 2 + 2, exit_y + 2))
        screen.blit(exit_surface, (WIDTH // 2 - exit_surface.get_width() // 2, exit_y))
        
        # Instrucciones
        inst_text = "Flechas Arriba/Abajo: Navegar | Enter: Seleccionar"
        inst_surface = tiny_font.render(inst_text, True, (150, 150, 150))
        screen.blit(inst_surface, (WIDTH // 2 - inst_surface.get_width() // 2, HEIGHT - 40))
        
        # Efectos de borde arcade
        border_thickness = 2
        border_color = CYAN
        border_glow = int(50 + 50 * math.sin(menu_time / 20))
        border_glow_color = (0, border_glow, border_glow)
        
        # Bordes superiores e inferiores
        pygame.draw.rect(screen, border_glow_color, (0, 0, WIDTH, border_thickness))
        pygame.draw.rect(screen, border_glow_color, (0, HEIGHT - border_thickness, WIDTH, border_thickness))
        
        # Bordes laterales
        pygame.draw.rect(screen, border_glow_color, (0, 0, border_thickness, HEIGHT))
        pygame.draw.rect(screen, border_glow_color, (WIDTH - border_thickness, 0, border_thickness, HEIGHT))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    selected_option = 0
                elif event.key == K_DOWN or event.key == K_s:
                    selected_option = 1
                elif event.key == K_RETURN:
                    pygame.mixer.music.stop()
                    if start_sound:
                        start_sound.play()
                    if selected_option == 0:
                        return True
                    else:
                        pygame.quit()
                        exit()
                elif event.key == K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
                    
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
            # Sonido de explosión
            if explosion_sound:
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
            # Sonido de explosión grande
            if explosion_sound:
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
                    explosion_sound.play()
            else:
                player.lives -= 1
                if explosion_sound:
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
        screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 20))
        
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