import pygame
import random
import sys

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Mini Metal Slug - Advanced Defense")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 120, 255)
GRAY = (60, 60, 60)
GREEN = (0, 255, 0) 
YELLOW = (255, 255, 0)

GROUND_Y = HEIGHT - 50

# 폰트
pygame.font.init() 
font = pygame.font.SysFont("arial", 24)

# 난이도/무기 관련 전역 변수
BASE_ENEMY_HEALTH = 8       
HEALTH_BONUS_PER_LEVEL = 3  
BASE_ENEMY_SPEED = 1       
SPEED_BONUS_PER_LEVEL = 0.5 
SCORE_FOR_LEVEL_UP = 50    

BASE_DAMAGE = 10                  
DAMAGE_BONUS_PER_LEVEL = 2      
BASE_SHOOT_DELAY = 250            
DELAY_REDUCTION_PER_LEVEL = 15  
BASE_UPGRADE_COST = 150         
UPGRADE_COST_INCREASE = 50      

# 보스 관련 변수
BOSS_LEVEL_INTERVAL = 3       
BASE_BOSS_HEALTH = 150        
BOSS_HEALTH_BONUS = 50        
BOSS_DAMAGE = 20              
BOSS_SHOOT_DELAY = 1000       
BOSS_SPEED = 1.0              

# 탱크형 적 관련 변수
TANK_ENEMY_HEALTH = 30       
TANK_ENEMY_SPEED = 0.5       
TANK_SCORE = 30              

# 배경 이미지 로드 
try:
    bg = pygame.image.load("metal map3.jpg").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
except pygame.error:
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(BLACK)

# 플레이어 이미지 로드 
try:
    player_img = pygame.image.load("tank2.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (60, 60))
except pygame.error:
    player_img = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.rect(player_img, BLUE, (0, 0, 60, 60))

# 적이미지 로드 
try:
    enemy_img = pygame.image.load("boss2.png").convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (70, 60)) 
except pygame.error:
    enemy_img = pygame.Surface((70, 60), pygame.SRCALPHA)
    pygame.draw.rect(enemy_img, RED, (0, 0, 70, 60))


# 적 총알
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=10):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -5 
        self.damage = damage 

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

# 플레이어 
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
        self.weapon_level = 0
        self.shoot_delay = BASE_SHOOT_DELAY 
        self.last_shot = pygame.time.get_ticks()
        self.health = 100
        self.max_health = 100
        self.dead = False
        self.invulnerable_time = 0 
        self.last_hit = pygame.time.get_ticks()

    def update(self):
        if self.dead: return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                bullet = Bullet(self.rect.centerx, self.rect.centery - 10, self.weapon_level)
                all_sprites.add(bullet)
                bullets.add(bullet)
                self.last_shot = now
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        now = pygame.time.get_ticks()
        if now - self.last_hit < self.invulnerable_time:
            self.image.set_alpha(100) if now // 100 % 2 == 0 else self.image.set_alpha(255) 
        else:
             self.image.set_alpha(255) 

    def get_upgrade_cost(self):
        return BASE_UPGRADE_COST + (self.weapon_level * UPGRADE_COST_INCREASE)

    def upgrade_weapon(self):
        self.weapon_level += 1
        self.shoot_delay = max(50, BASE_SHOOT_DELAY - (self.weapon_level * DELAY_REDUCTION_PER_LEVEL))
        
    def hit(self, damage, invulnerable_time=1500):
        now = pygame.time.get_ticks()
        if now - self.last_hit > self.invulnerable_time: 
            self.health -= damage
            self.last_hit = now
            self.invulnerable_time = invulnerable_time
            if self.health <= 0:
                self.health = 0
                self.dead = True
                
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
    def __init__(self, x, y, weapon_level):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8
        self.damage = BASE_DAMAGE + (weapon_level * DAMAGE_BONUS_PER_LEVEL) 

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.kill()
            
# 일반 적
class Enemy(pygame.sprite.Sprite):
    def __init__(self, current_level): 
        super().__init__()
        self.image = enemy_img 

        self.rect = self.image.get_rect(
            bottomleft=(random.randint(WIDTH + 20, WIDTH + 100), GROUND_Y)
        )
        
        self.health = BASE_ENEMY_HEALTH + (current_level * HEALTH_BONUS_PER_LEVEL)
        self.max_health = self.health 

        min_speed = BASE_ENEMY_SPEED + (current_level * SPEED_BONUS_PER_LEVEL)
        max_speed = min_speed + 1.5 
        self.speed = random.uniform(min_speed, max_speed)
        
        self.shoot_delay = 1500 
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x -= self.speed 
        
        # 💥 [수정됨] 적이 왼쪽 경계를 통과해도 스스로 kill()하지 않습니다.
        #           메인 루프에서 game_over 조건을 확인합니다.

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if self.rect.left < WIDTH:
                enemy_bullet = EnemyBullet(self.rect.centerx - 40, self.rect.centery) 
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)
                self.last_shot = now
                
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True, 10 
        return False, 0 
        
    def draw_health_bar(self, surface):
        BAR_WIDTH = 40
        BAR_HEIGHT = 5
        fill = (self.health / self.max_health) * BAR_WIDTH
        outline_rect = pygame.Rect(self.rect.x + (self.rect.width - BAR_WIDTH) // 2, self.rect.y - 10, BAR_WIDTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(self.rect.x + (self.rect.width - BAR_WIDTH) // 2, self.rect.y - 10, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, outline_rect) 
        pygame.draw.rect(surface, GREEN, fill_rect)

# 탱크형 적
class TankEnemy(pygame.sprite.Sprite):
    def __init__(self, current_level): 
        super().__init__()
        self.image = enemy_img 
        self.image = pygame.transform.scale(self.image, (80, 70)) 
        self.image.fill(YELLOW, special_flags=pygame.BLEND_MULT) 

        self.rect = self.image.get_rect(
            bottomleft=(random.randint(WIDTH + 50, WIDTH + 150), GROUND_Y)
        )
        
        self.health = TANK_ENEMY_HEALTH + (current_level // 2) * HEALTH_BONUS_PER_LEVEL
        self.max_health = self.health 
        self.speed = TANK_ENEMY_SPEED
        self.score_value = TANK_SCORE 
        
        self.shoot_delay = 3000 
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x -= self.speed 
        
        # 💥 [수정됨] 적이 왼쪽 경계를 통과해도 스스로 kill()하지 않습니다.
        #           메인 루프에서 game_over 조건을 확인합니다.
        
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if self.rect.left < WIDTH:
                enemy_bullet = EnemyBullet(self.rect.centerx - 40, self.rect.centery, damage=5) 
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)
                self.last_shot = now
                
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True, self.score_value 
        return False, 0 
        
    def draw_health_bar(self, surface):
        BAR_WIDTH = 40
        BAR_HEIGHT = 5
        fill = (self.health / self.max_health) * BAR_WIDTH
        outline_rect = pygame.Rect(self.rect.x + (self.rect.width - BAR_WIDTH) // 2, self.rect.y - 10, BAR_WIDTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(self.rect.x + (self.rect.width - BAR_WIDTH) // 2, self.rect.y - 10, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, outline_rect) 
        pygame.draw.rect(surface, GREEN, fill_rect)


# 보스 
class Boss(pygame.sprite.Sprite):
    def __init__(self, current_level): 
        super().__init__()
        self.image = enemy_img 
        self.image = pygame.transform.scale(self.image, (100, 90)) 

        self.rect = self.image.get_rect(
            bottomleft=(WIDTH + 50, GROUND_Y)
        )
        
        boss_stage_num = current_level // BOSS_LEVEL_INTERVAL
        self.health = BASE_BOSS_HEALTH + (boss_stage_num * BOSS_HEALTH_BONUS)
        self.max_health = self.health 

        self.speed = BOSS_SPEED 
        self.shoot_delay = BOSS_SHOOT_DELAY
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        stop_x = WIDTH - self.rect.width - 50 
        
        if self.rect.x > stop_x:
            self.rect.x -= self.speed
        
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if self.rect.left < WIDTH:
                boss_bullet = EnemyBullet(self.rect.centerx - 50, self.rect.centery, damage=BOSS_DAMAGE) 
                all_sprites.add(boss_bullet)
                enemy_bullets.add(boss_bullet)
                self.last_shot = now
                
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True, 100 
        return False, 0 
        
    def draw_health_bar(self, surface):
        BAR_WIDTH = 80 
        BAR_HEIGHT = 10
        fill = (self.health / self.max_health) * BAR_WIDTH
        outline_rect = pygame.Rect(self.rect.x + (self.rect.width - BAR_WIDTH) // 2, self.rect.y - 15, BAR_WIDTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(self.rect.x + (self.rect.width - BAR_WIDTH) // 2, self.rect.y - 15, fill, BAR_HEIGHT)
        
        pygame.draw.rect(surface, (255, 0, 0), outline_rect, 2) 
        pygame.draw.rect(surface, YELLOW, fill_rect)


# 폭발 클래스 
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = []
        for size in range(10, 40, 5):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
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


# 그룹 및 초기화 
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

enemy_timer = 0
score = 0
game_over = False 

current_level = 0
next_level_score = SCORE_FOR_LEVEL_UP 

boss_active = False 
boss_spawned_for_level = -1 

game_over_font = pygame.font.SysFont("arial", 72, bold=True)
game_over_text = game_over_font.render("GAME OVER", True, RED)
game_over_rect = game_over_font.render("GAME OVER", True, RED).get_rect(center=(WIDTH // 2, HEIGHT // 2))

# 메인 루프
while True:
    current_upgrade_cost = player.get_upgrade_cost()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            if score >= current_upgrade_cost:
                score -= current_upgrade_cost
                player.upgrade_weapon()
            
    if game_over:
        if any(pygame.key.get_pressed()):
             pygame.quit()
             sys.exit()
        
    if not game_over:
        
        # 레벨업 로직
        if score >= next_level_score:
            current_level += 1
            next_level_score += SCORE_FOR_LEVEL_UP 
            print(f"Level UP! Current Stage: {current_level + 1}")

        # 보스 스폰 로직
        is_boss_level = (current_level > 0 and (current_level + 1) % BOSS_LEVEL_INTERVAL == 0)
        
        if is_boss_level and not boss_active and boss_spawned_for_level != current_level:
            for enemy in enemies:
                enemy.kill() 
                
            boss = Boss(current_level)
            all_sprites.add(boss)
            enemies.add(boss) 
            
            boss_active = True
            boss_spawned_for_level = current_level
            print(f"BOSS spawned for Stage {current_level + 1}!")
            
        
        # 일반/탱크 적 스폰 로직 
        if not boss_active:
            enemy_timer += 1
            if enemy_timer > 30: 
                if random.random() < 0.7:
                    enemy = Enemy(current_level) 
                else:
                    enemy = TankEnemy(current_level)
                    
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_timer = 0

        # 업데이트
        all_sprites.update()
        
        # 💥 [핵심] 적 통과로 인한 게임 오버 체크
        for enemy in enemies:
            # Boss 인스턴스가 아니면서 (일반 적/탱크 적), 화면의 오른쪽 끝이 0보다 작을 때 (화면을 통과했을 때)
            if not isinstance(enemy, Boss) and enemy.rect.right < 0:
                print("Enemy passed! Game Over.")
                game_over = True
                break
                
        # 보스 사망 체크
        if boss_active and len(enemies) == 0:
            boss_active = False
            print("Boss Defeated! Proceeding to next stage waves.")


        # 충돌 (총알 vs 적) - 체력 기반 처리
        hits = pygame.sprite.groupcollide(bullets, enemies, True, False) 
        for bullet, hit_list in hits.items():
            for hit in hit_list:
                is_dead, kill_score = hit.take_damage(bullet.damage)
                if is_dead: 
                    explosion = Explosion(hit.rect.center)
                    all_sprites.add(explosion)
                    score += kill_score 
            
        # 충돌 (적 총알 vs 플레이어)
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            player.hit(hit.damage) 
            
        # 플레이어 사망 체크
        if player.dead:
            game_over = True


    # 화면 그리기
    screen.blit(bg, (0, 0)) 
    pygame.draw.rect(screen, GRAY, (0, GROUND_Y, WIDTH, 50)) 

    all_sprites.draw(screen)
    
    # 적들의 체력 바 그리기
    if not game_over:
        for enemy in enemies:
            enemy.draw_health_bar(screen)

    # 플레이어 체력바 그리기
    if not game_over:
        player.draw_health_bar(screen)

    # 점수 및 정보 표시
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    stage_text = font.render(f"Stage: {current_level + 1} (Next Level: {next_level_score})", True, WHITE)
    screen.blit(stage_text, (10, 30))
    
    upgrade_text = font.render(
        f"[Z] UPGRADE Wpn Lv.{player.weapon_level} -> {player.weapon_level + 1} | Cost: {current_upgrade_cost}", 
        True, 
        (0, 255, 255) if score >= current_upgrade_cost else RED
    )
    screen.blit(upgrade_text, (WIDTH - 450, 10))
    
    # 게임 오버 화면
    if game_over:
        screen.blit(game_over_text, game_over_rect)
        restart_text = font.render("Press any key to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        screen.blit(restart_text, restart_rect)


    pygame.display.flip()
    clock.tick(60)