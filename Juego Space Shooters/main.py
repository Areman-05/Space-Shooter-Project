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
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/DurrrSpaceShip.png")
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.lives = 3
        self.score = 0
        self.update_stats()

    def update_stats(self):
        if self.score < 150:
            self.speed = 3
            self.shoot_delay = 500
        elif self.score < 250:
            self.speed = 4
            self.shoot_delay = 400
        elif self.score < 400:
            self.speed = 5
            self.shoot_delay = 300
        elif self.score < 600:
            self.speed = 6
            self.shoot_delay = 200
        else:
            self.speed = 7
            self.shoot_delay = 150

    def update(self):
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
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, slow_mode=True):
        super().__init__()
        self.image = pygame.image.load("./images/Asteroid Brown.png")
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.base_speed = random.randint(3, 6)
        self.slow_speed = random.randint(1, 3)
        self.speed = self.slow_speed if slow_mode else self.base_speed
    
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
    slow_mode = True
    player = Player(slow_mode)
    player_group = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    for _ in range(3):
        enemies.add(Enemy(slow_mode))
    
    score = 0
    running = True
    show_controls_message()

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_SPACE:
                bullets.add(Bullet(player.rect.centerx, player.rect.top, slow_mode))
                shoot_sound.play()
        
        if score >= 500 and slow_mode:
            slow_mode = False
            player.speed = player.base_speed
            for enemy in enemies:
                enemy.speed = enemy.base_speed
            for bullet in bullets:
                bullet.speed = bullet.base_speed

        player_group.update()
        bullets.update()
        enemies.update()

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for _ in hits:
            score += 10
            enemies.add(Enemy(slow_mode))

        screen.fill(BLACK)
        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)

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