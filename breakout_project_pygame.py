
import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (15, 15, 20)
RED = (220, 70, 70)
GREEN = (70, 220, 120)
BLUE = (80, 120, 255)
YELLOW = (255, 220, 70)
PURPLE = (180, 90, 255)
ORANGE = (255, 160, 60)

MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
VICTORY = "victory"

class Paddle:
    def __init__(self):
        self.width = 120
        self.height = 18
        self.rect = pygame.Rect(WIDTH // 2 - self.width // 2, HEIGHT - 60, self.width, self.height)
        self.speed = 8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=8)

class Ball:
    def __init__(self):
        self.radius = 10
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = random.choice([-5, 5])
        self.speed_y = -5

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.speed_x *= -1

        if self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

class Brick:
    def __init__(self, x, y, color, hp=1):
        self.rect = pygame.Rect(x, y, 90, 30)
        self.color = color
        self.hp = hp

    def hit(self):
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)

class PowerUp:
    TYPES = ["expand", "life", "slow"]

    def __init__(self, x, y):
        self.kind = random.choice(self.TYPES)
        self.rect = pygame.Rect(x, y, 24, 24)
        self.speed = 4

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        color = GREEN if self.kind == "life" else YELLOW if self.kind == "expand" else PURPLE
        pygame.draw.rect(screen, color, self.rect, border_radius=6)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Breakout Deluxe")
        self.clock = pygame.time.Clock()
        self.big_font = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 32)
        self.state = MENU
        self.difficulty = 1
        self.level = 1
        self.score = 0
        self.lives = 3
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.powerups = []
        self.create_level()

    def create_level(self):
        self.bricks.clear()
        colors = [RED, ORANGE, GREEN, BLUE, PURPLE]
        rows = min(4 + self.level, 8)
        cols = 8
        start_x = (WIDTH - (cols * 100)) // 2

        for row in range(rows):
            for col in range(cols):
                hp = 1 if self.level < 3 else random.randint(1, 2)
                brick = Brick(
                    start_x + col * 100,
                    80 + row * 40,
                    colors[row % len(colors)],
                    hp
                )
                self.bricks.append(brick)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.level = 1
        self.score = 0
        self.lives = 3
        self.paddle = Paddle()
        self.ball = Ball()

        if difficulty == 1:
            self.ball.speed_x = random.choice([-4, 4])
            self.ball.speed_y = -4
        elif difficulty == 2:
            self.ball.speed_x = random.choice([-6, 6])
            self.ball.speed_y = -6
        else:
            self.ball.speed_x = random.choice([-8, 8])
            self.ball.speed_y = -8

        self.powerups.clear()
        self.create_level()
        self.state = PLAYING

    def apply_powerup(self, powerup):
        if powerup.kind == "expand":
            self.paddle.rect.width = min(self.paddle.rect.width + 40, 220)
        elif powerup.kind == "life":
            self.lives += 1
        elif powerup.kind == "slow":
            self.ball.speed_x *= 0.8
            self.ball.speed_y *= 0.8

    def update(self):
        self.paddle.update()
        self.ball.update()

        if self.ball.rect.colliderect(self.paddle.rect):
            hit_pos = (self.ball.x - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
            self.ball.speed_x = hit_pos * 7
            self.ball.speed_y = -abs(self.ball.speed_y)
            self.ball.y = self.paddle.rect.top - self.ball.radius

        for brick in self.bricks[:]:
            if self.ball.rect.colliderect(brick.rect):
                self.ball.speed_y *= -1
                destroyed = brick.hit()

                if destroyed:
                    self.bricks.remove(brick)
                    self.score += 100

                    if random.random() < 0.15:
                        self.powerups.append(PowerUp(brick.rect.centerx, brick.rect.centery))

                break

        for powerup in self.powerups[:]:
            powerup.update()

            if powerup.rect.colliderect(self.paddle.rect):
                self.apply_powerup(powerup)
                self.powerups.remove(powerup)

            elif powerup.rect.top > HEIGHT:
                self.powerups.remove(powerup)

        if self.ball.y > HEIGHT:
            self.lives -= 1

            if self.lives <= 0:
                self.state = GAME_OVER
            else:
                self.ball.reset()

        if not self.bricks:
            self.level += 1

            if self.level > 5:
                self.state = VICTORY
            else:
                self.ball.reset()
                self.create_level()

    def draw_hud(self):
        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (20, 20))
        self.screen.blit(self.font.render(f"Lives: {self.lives}", True, WHITE), (20, 55))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE), (20, 90))

    def draw_menu(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.big_font.render("Breakout Deluxe", True, WHITE), (250, 180))
        self.screen.blit(self.font.render("1 - Easy", True, WHITE), (390, 320))
        self.screen.blit(self.font.render("2 - Normal", True, WHITE), (380, 360))
        self.screen.blit(self.font.render("3 - Hard", True, WHITE), (390, 400))

    def draw_game(self):
        self.screen.fill(BLACK)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)

        for brick in self.bricks:
            brick.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        self.draw_hud()

    def draw_end(self, title):
        self.screen.fill(BLACK)
        self.screen.blit(self.big_font.render(title, True, WHITE), (300, 220))
        self.screen.blit(self.font.render(f"Final Score: {self.score}", True, WHITE), (370, 320))
        self.screen.blit(self.font.render("Press R to Restart", True, WHITE), (350, 380))

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.state == MENU:
                        if event.key == pygame.K_1:
                            self.start_game(1)
                        elif event.key == pygame.K_2:
                            self.start_game(2)
                        elif event.key == pygame.K_3:
                            self.start_game(3)

                    elif self.state in (GAME_OVER, VICTORY):
                        if event.key == pygame.K_r:
                            self.state = MENU

            if self.state == PLAYING:
                self.update()

            if self.state == MENU:
                self.draw_menu()
            elif self.state == PLAYING:
                self.draw_game()
            elif self.state == GAME_OVER:
                self.draw_end("Game Over")
            elif self.state == VICTORY:
                self.draw_end("You Win")

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    Game().run()
