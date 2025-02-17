import pygame
import random
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
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/DurrrSpaceShip.png")
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.base_speed = 3  # Velocidad reducida al inicio
        self.normal_speed = 5  # Velocidad normal tras 500 puntos
        self.speed = self.base_speed
        self.lives = 3

    def update(self, score):
        if score >= 500:
            self.speed = self.normal_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, slow_shoot):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -5 if slow_shoot else -7  # Disparos más lentos al inicio

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/Asteroid Brown.png")
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

def show_start_screen():
    start_image = pygame.image.load("./images/1-dc990692.png")
    start_image = pygame.transform.scale(start_image, (WIDTH, HEIGHT))

  
    alpha = 0
    screen.fill(BLACK)
    pygame.display.flip()
    start_sound.play()  

    while alpha < 255:
        alpha += 5
        start_image.set_alpha(alpha)
        screen.fill(BLACK)
        screen.blit(start_image, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)

    pygame.time.wait(4000) 

def show_controls_message():
    message = small_font.render("Controles: WASD para mover, ESPACIO para disparar", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT - 40))
    pygame.display.flip()
    pygame.time.wait(2000)

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

def main_game():
    player = Player()
    player_group = pygame.sprite.Group()
    player_group.add(player)

    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    initial_enemy_count = 3  # Menos enemigos al inicio
    for _ in range(initial_enemy_count):
        enemy = Enemy(True)
        enemies.add(enemy)

    score = 0
    running = True
    shoot_cooldown = 500  # Disparos menos frecuentes al inicio
    last_shot = pygame.time.get_ticks()

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_SPACE:
                now = pygame.time.get_ticks()
                if now - last_shot > shoot_cooldown:
                    bullet = Bullet(player.rect.centerx, player.rect.top, score < 500)
                    bullets.add(bullet)
                    shoot_sound.play()
                    last_shot = now

        if score >= 500:
            shoot_cooldown = 250  # Velocidad normal de disparo tras 500 puntos
            if len(enemies) < 7:  # Generar más enemigos tras 500 puntos
                enemies.add(Enemy(False))

        player.update(score)
        bullets.update()
        enemies.update()

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for _ in hits:
            score += 10
            enemies.add(Enemy(score < 500))

        hits_player = pygame.sprite.spritecollide(player, enemies, True)
        if hits_player:
            player.lives -= 1
            if player.lives == 0:
                return

        screen.fill(BLACK)
        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)

        lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        score_text = font.render(f"Puntuación: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

def run_game():
    show_start_screen()  
    while True:
        if show_main_menu():
            main_game()
        else:
            break

run_game()
pygame.quit()