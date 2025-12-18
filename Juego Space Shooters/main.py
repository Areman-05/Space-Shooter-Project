import pygame
import random
import math
from pygame.locals import *

pygame.init()
pygame.mixer.init()

shoot_sound = pygame.mixer.Sound("./sounds/alienshoot1.wav")
start_sound = pygame.mixer.Sound("./sounds/start.ogg")

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

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/DurrrSpaceShip.png")
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
        self.image = pygame.image.load("./images/Asteroid Brown.png")
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

def show_main_menu():
    while True:
        screen.fill(BLACK)
        title_text = font.render("Space Shooter", True, YELLOW)
        play_text = small_font.render("Presiona Enter para Jugar", True, WHITE)
        exit_text = small_font.render("Presiona Esc para Salir", True, WHITE)
        
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 1.5))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return True
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
                    
def show_controls_message():
    message = small_font.render("Controles: WASD para mover, ESPACIO para disparar", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT - 40))
    pygame.display.flip()
    pygame.time.wait(2000)

def main_game():
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
                            shoot_sound.play()
                            
                        elif player.weapon_type == "rapid":
                            bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed))
                            player.shoot_cooldown = 5
                            shoot_sound.play()
                            
                        elif player.weapon_type == "spread":
                            for angle in [-20, -10, 0, 10, 20]:
                                bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed, YELLOW, (6, 12), angle))
                            player.shoot_cooldown = 20
                            shoot_sound.play()
                            
                        elif player.weapon_type == "laser":
                            bullets.add(Bullet(player.rect.centerx, player.rect.top, bullet_speed * 2, RED, (8, 20)))
                            player.shoot_cooldown = 10
                            shoot_sound.play()
                
                if event.key == K_m and player.missiles_available > 0 and player.missile_cooldown <= 0:
                    missiles.add(Missile(player.rect.centerx, player.rect.top))
                    player.missiles_available -= 1
                    player.missile_cooldown = 30
                    shoot_sound.play()
                    
                if event.key == K_ESCAPE:
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
            elif powerup.power_type == "speed":
                player.activate_speed_boost(600)
            elif powerup.power_type == "rapid":
                player.activate_weapon("rapid", 600)
            elif powerup.power_type == "spread":
                player.activate_weapon("spread", 600)
            elif powerup.power_type == "laser":
                player.activate_weapon("laser", 600)
            elif powerup.power_type == "missile":
                player.add_missiles(3)
        
        # Colisiones jugador-enemigos
        hits_player = pygame.sprite.spritecollide(player, enemies, True)
        if hits_player:
            if player.shield_active:
                player.shield_active = False
                player.shield_time = 0
            else:
                player.lives -= 1
                if player.lives == 0:
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
    while True:
        if show_main_menu():
            main_game()
        else:
            break
    pygame.quit()
    exit()

run_game()
