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
GREEN = (0, 255, 0) # 체력바를 위한 초록색 추가

GROUND_Y = HEIGHT - 50

# 폰트
pygame.font.init() # 폰트 시스템을 다시 확실히 초기화합니다.
font = pygame.font.SysFont("arial", 24)

# 배경 이미지 (간단히 색상 블록으로 표현)
# 주의: 이 파일("metal map3.jpg")이 현재 실행 디렉토리에 있어야 합니다.
try:
    bg = pygame.image.load("metal map3.jpg").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
except pygame.error:
    print("Warning: 'metal map3.jpg' not found. Using black screen.")
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(BLACK)


# 플레이어 이미지
# 주의: 이 파일("tank2.png")이 현재 실행 디렉토리에 있어야 합니다.
try:
    player_img = pygame.image.load("tank2.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (60, 60))
except pygame.error:
    print("Warning: 'tank2.png' not found. Using blue box.")
    player_img = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.rect(player_img, BLUE, (0, 0, 60, 60))


# 적이미지
# 주의: 이 파일("boss2.png")이 현재 실행 디렉토리에 있어야 합니다.
try:
    enemy_img = pygame.image.load("boss2.png").convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (120, 100))
except pygame.error:
    print("Warning: 'boss2.png' not found. Using red box.")
    enemy_img = pygame.Surface((120, 100), pygame.SRCALPHA)
    pygame.draw.rect(enemy_img, RED, (0, 0, 120, 100))


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
        
        # --- [추가] 체력 및 사망 상태 ---
        self.health = 100
        self.max_health = 100
        self.dead = False
        self.invulnerable_time = 0 # 무적 시간
        self.last_hit = pygame.time.get_ticks()

    def update(self):
        if self.dead: # 사망 시 움직임 멈춤
            return
            
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
        
        # --- [추가] 무적 상태 깜빡임 처리 ---
        now = pygame.time.get_ticks()
        if now - self.last_hit < self.invulnerable_time:
            if now // 100 % 2 == 0:
                self.image.set_alpha(100) # 반투명하게
            else:
                self.image.set_alpha(255) # 원래대로
        else:
             self.image.set_alpha(255) # 무적 시간이 끝나면 완전히 보이게

    # --- [추가] 피격 처리 메서드 ---
    def hit(self, damage, invulnerable_time=1500):
        now = pygame.time.get_ticks()
        if now - self.last_hit > self.invulnerable_time: # 무적 시간이 아니면
            self.health -= damage
            self.last_hit = now
            self.invulnerable_time = invulnerable_time
            if self.health <= 0:
                self.health = 0
                self.dead = True
                
    # --- [추가] 체력바 그리기 메서드 (Player 클래스 외부에 작성하는 것이 더 깔끔할 수 있으나, 편의상 여기에 추가) ---
    def draw_health_bar(self, surface):
        BAR_WIDTH = 60
        BAR_HEIGHT = 8
        fill = (self.health / self.max_health) * BAR_WIDTH
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 15, BAR_WIDTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 15, fill, BAR_HEIGHT)
        
        pygame.draw.rect(surface, GREEN, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)

# 총알 (플레이어)
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
            
# --- [추가] 적 총알 ---
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -5 # 왼쪽으로 이동 (플레이어를 향해)
        self.damage = 10 # 플레이어에게 줄 피해량

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

# 적
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(
            midbottom=(random.randint(WIDTH + 20, WIDTH + 100), GROUND_Y)
        )
        self.speed = random.randint(1, 2)
        
        # --- [추가] 적 공격 관련 속성 ---
        self.shoot_delay = 1500 # 1.5초마다 발사
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
        
        # --- [추가] 적 공격 로직 ---
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            # 적이 화면 안에 있을 때만 발사
            if self.rect.left < WIDTH:
                enemy_bullet = EnemyBullet(self.rect.centerx - 40, self.rect.centery)
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)
                self.last_shot = now

# 폭발
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = []
        # 폭발 이미지를 실제 이미지로 대체하면 더 좋겠지만, 여기서는 색상 블록으로 진행합니다.
        for size in range(10, 40, 5):
            frame = pygame.Surface((size, size), pygame.SRCALPHA) # 투명 배경
            pygame.draw.circle(frame, RED, (size // 2, size // 2), size // 2)
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
enemy_bullets = pygame.sprite.Group() # --- [추가] 적 총알 그룹 ---

player = Player()
all_sprites.add(player)

# 변수
enemy_timer = 0
score = 0
bg_x = 0  # 배경 스크롤 위치
game_over = False # --- [추가] 게임 오버 상태 변수 ---

# 게임 오버 텍스트 렌더링
game_over_font = pygame.font.SysFont("arial", 72, bold=True)
game_over_text = game_over_font.render("GAME OVER", True, RED)
game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# 메인 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    # --- [추가] 게임 오버 상태일 때 루프 종료 또는 재시작 로직 추가 가능 ---
    if game_over:
        # 키를 누르면 종료
        if any(pygame.key.get_pressed()):
             # 간단히 종료하도록 설정 (재시작 로직을 추가할 수도 있음)
             pygame.quit()
             sys.exit()
        
    if not game_over:
        # 배경 스크롤
        bg_x -= 2
        if bg_x <= -WIDTH:
            bg_x = 0

        # 적 생성
        enemy_timer += 1
        # 적 생성 빈도를 좀 더 느슨하게 조정할 수 있음. 
        # (예: 50 -> 70 정도로)
        if enemy_timer > 70: 
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
            
        # --- [추가] 충돌 (적 총알 vs 플레이어) ---
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            player.hit(hit.damage) # 플레이어 체력 감소 및 무적 시간 적용
            
        # --- [추가] 플레이어 사망 체크 ---
        if player.dead:
            game_over = True


    # 화면 그리기
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + WIDTH, 0))
    pygame.draw.rect(screen, GRAY, (0, GROUND_Y, WIDTH, 50))  # 땅

    all_sprites.draw(screen)

    # --- [추가] 플레이어 체력바 그리기 ---
    if not game_over:
        player.draw_health_bar(screen)

    # 점수 표시
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # --- [추가] 게임 오버 화면 ---
    if game_over:
        screen.blit(game_over_text, game_over_rect)
        restart_text = font.render("Press any key to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        screen.blit(restart_text, restart_rect)


    pygame.display.flip()
    clock.tick(60)