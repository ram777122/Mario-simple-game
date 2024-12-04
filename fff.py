import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario Adventure")

# Game settings
GRAVITY = 0.5
JUMP_STRENGTH = -15
MOVE_SPEED = 5
SCROLL_THRESHOLD = 300

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

class ScrollManager:
    def __init__(self):
        self.world_shift = 0

    def update(self, player_x):
        if player_x > SCROLL_THRESHOLD:
            shift = player_x - SCROLL_THRESHOLD
            self.world_shift += shift
            return shift
        return 0

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (50, 70))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

    def move(self, keys, platforms):
        if keys[pygame.K_LEFT]: self.velocity_x = -MOVE_SPEED
        elif keys[pygame.K_RIGHT]: self.velocity_x = MOVE_SPEED
        else: self.velocity_x = 0
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
        self.velocity_y += GRAVITY
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True

    def update(self, scroll_amount):
        self.rect.x -= scroll_amount

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, scroll_amount):
        self.rect.x -= scroll_amount

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (20, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_y = y
        self.bounce_amplitude = 10
        self.bounce_speed = 2

    def update(self, scroll_amount):
        self.rect.x -= scroll_amount
        self.rect.y = self.base_y + self.bounce_amplitude * math.sin(pygame.time.get_ticks() * self.bounce_speed / 1000)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.move_speed = 2
        self.direction = 1

    def update(self, scroll_amount):
        self.rect.x -= scroll_amount
        self.rect.x += self.move_speed * self.direction
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1

class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (100, 60))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.drift_speed = random.uniform(0.5, 1)

    def update(self, scroll_amount):
        self.rect.x -= scroll_amount + self.drift_speed
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

class Game:
    def __init__(self):
        self.background_image = pygame.image.load("background_sea.png")
        self.ground_image = pygame.image.load("platform_grass.png")
        self.player_image = pygame.image.load("mario.png")
        self.coin_image = pygame.image.load("coin.png")
        self.enemy_image = pygame.image.load("enemy.png")
        self.cloud_image = pygame.image.load("cloud.png")

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()

        self.player = Player(100, 500, self.player_image)
        self.all_sprites.add(self.player)

        for i in range(0, 5000, 200):
            platform = Platform(i, 550, 200, 50, self.ground_image)
            self.platforms.add(platform)
            self.all_sprites.add(platform)

        for i in range(300, 3000, 400):
            coin = Coin(i, 500, self.coin_image)
            self.coins.add(coin)
            self.all_sprites.add(coin)

        for i in range(500, 3000, 600):
            enemy = Enemy(i, 500, self.enemy_image)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        for i in range(5):
            cloud = Cloud(random.randint(0, SCREEN_WIDTH), random.randint(50, 200), self.cloud_image)
            self.clouds.add(cloud)
            self.all_sprites.add(cloud)

        self.scroll_manager = ScrollManager()
        self.clock = pygame.time.Clock()
        self.running = True
        self.coins_collected = 0
        self.font = pygame.font.SysFont("Arial", 30)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            self.player.move(keys, self.platforms)

            scroll_amount = self.scroll_manager.update(self.player.rect.x)
            self.all_sprites.update(scroll_amount)

            collected_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
            self.coins_collected += len(collected_coins)
            if pygame.sprite.spritecollideany(self.player, self.enemies):
                self.game_over()

            if self.coins_collected >= 20:
                self.display_congratulations()

            SCREEN.fill(WHITE)
            self.draw_background(scroll_amount)
            self.all_sprites.draw(SCREEN)
            self.display_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def draw_background(self, scroll_amount):
        background_width = self.background_image.get_width()
        scaled_bg = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(0, SCREEN_WIDTH, SCREEN_WIDTH):
            SCREEN.blit(scaled_bg, (i - scroll_amount, 0))

    def display_ui(self):
        coin_text = self.font.render(f"Coins: {self.coins_collected}", True, WHITE)
        SCREEN.blit(coin_text, (10, 10))

    def display_congratulations(self):
        congrat_text = self.font.render("Congratulations! You collected 20 coins!", True, GREEN)
        SCREEN.fill(BLACK)
        SCREEN.blit(congrat_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        self.running = False

    def game_over(self):
        game_over_text = self.font.render("Game Over!", True, WHITE)
        SCREEN.fill(BLACK)
        SCREEN.blit(game_over_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        self.running = False


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
