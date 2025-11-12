import pygame
import random
import sys

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Mini Metal Slug - Scroll & Explosion Version")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 120, 255)
GRAY = (60, 60, 60)

GROUND_Y = HEIGHT - 50

# 폰트
font = pygame.font.SysFont("arial", 24)

# 배경 이미지 (간단히 색상 블록으로 표현)
bg = pygame.image.load("metal map3.jpg").convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

# 플레이어 이미지
player_img = pygame.image.load("tank2.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 60))  #

# 적이미지
enemy_img = pygame.image.load("boss2.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (120, 100))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(midbottom=(100, GROUND_Y))
        self.speed = 5
        self.jump_power = -12
        self.gravity = 0.6
        self.vel_y = 0
        self.on_ground = True
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()

        # 이동
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # 점프
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        # 중력
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        # 총알 발사
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                bullet = Bullet(self.rect.centerx, self.rect.centery - 10)
                all_sprites.add(bullet)
                bullets.add(bullet)
                self.last_shot = now

        # 화면 제한
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

# 총알
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.kill()

# 적
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 50))
        self.image = enemy_img
        self.rect = self.image.get_rect(
            midbottom=(random.randint(WIDTH + 20, WIDTH + 100), GROUND_Y)
        )
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# 폭발
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = []
        for size in range(10, 40, 5):
            frame = pygame.Surface((size, size))
            frame.fill(RED)
            self.frames.append(frame)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1
            if self.index < len(self.frames):
                self.image = self.frames[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)
            else:
                self.kill()

# 그룹
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# 변수
enemy_timer = 0
score = 0
bg_x = 0  # 배경 스크롤 위치

# 메인 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 배경 스크롤
    bg_x -= 2
    if bg_x <= -WIDTH:
        bg_x = 0

    # 적 생성
    enemy_timer += 1
    if enemy_timer > 50:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_timer = 0

    # 업데이트
    all_sprites.update()

    # 충돌 (총알 vs 적)
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        explosion = Explosion(hit.rect.center)
        all_sprites.add(explosion)
        score += 10

    # 화면 그리기
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + WIDTH, 0))
    pygame.draw.rect(screen, GRAY, (0, GROUND_Y, WIDTH, 50))  # 땅

    all_sprites.draw(screen)

    # 점수 표시
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
