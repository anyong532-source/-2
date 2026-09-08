
import pygame
import random
import math

# 초기화
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Knight - High Damage Version")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
DARK_RED = (120, 20, 20)
BLUE = (50, 100, 220)
DARK_BLUE = (30, 30, 80)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# 스킬 목록 (15종) - 설명 및 수치 강화
SKILL_LIST = [
    {"name": "공격력 대폭 증가", "type": "atk", "desc": "공격력이 50% 강력해집니다."},
    {"name": "초고속 공격", "type": "atk_speed", "desc": "공격 쿨타임이 대폭 감소합니다."},
    {"name": "이동 속도 증가", "type": "speed", "desc": "이동 속도가 20% 증가합니다."},
    {"name": "최대 체력 증가", "type": "max_hp", "desc": "최대 체력이 50 증가하고 회복합니다."},
    {"name": "체력 재생", "type": "regen", "desc": "초당 체력을 회복합니다."},
    {"name": "흡혈", "type": "vamp", "desc": "적 처치 시 체력을 회복합니다."},
    {"name": "치명타 확률", "type": "crit", "desc": "치명타 확률이 25% 증가합니다."},
    {"name": "거대 공격 범위", "type": "range", "desc": "공격 범위가 50% 확대됩니다."},
    {"name": "방어력 증가", "type": "def", "desc": "받는 피해가 감소합니다."},
    {"name": "다중 공격", "type": "multi", "desc": "공격 시 검기가 추가로 발생합니다."},
    {"name": "화염 검기", "type": "fire", "desc": "적에게 강력한 지속 화염 피해를 줍니다."},
    {"name": "빙결 검기", "type": "frost", "desc": "적이 잠시 둔화됩니다."},
    {"name": "경험치 획득 증가", "type": "exp", "desc": "경험치 획득량이 35% 증가합니다."},
    {"name": "자석 범위 증가", "type": "magnet", "desc": "경험치/아이템 끌어당기는 범위 증가."},
    {"name": "가시 갑옷", "type": "thorns", "desc": "피격 시 주변 적에게 강한 반사 피해를 줍니다."}
]

# 잔상 이펙트 클래스 (보스 돌진 붉은 안개)
class Afterimage:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.alpha = 180

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            s.fill((*self.color, self.alpha))
            surface.blit(s, (self.x - self.size//2, self.y - self.size//2))
            self.alpha -= 12

# 플레이어
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 24
        self.speed = 3.0
        self.hp = 100
        self.max_hp = 100
        self.damage = 40  # [수정] 기본 공격력 25 -> 40 상향
        self.attack_cooldown = 0
        self.max_cooldown = 15
        self.level = 1
        self.exp = 0
        self.max_exp = 100
        self.range_mult = 1.0

    def move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x = max(self.size, min(WIDTH - self.size, self.x + dx * self.speed))
        self.y = max(self.size, min(HEIGHT - self.size, self.y + dy * self.speed))

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x - self.size//2, self.y - self.size//2, self.size, self.size))
        pygame.draw.rect(surface, RED, (self.x - 4, self.y - self.size//2 - 4, 8, 4))

# 몬스터 & 보스 늑대
class Monster:
    def __init__(self, x, y, hp, speed, size, color, is_boss=False):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.size = size
        self.color = color
        self.is_boss = is_boss
        
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_target = (0, 0)

    def update(self, player, afterimages):
        if self.is_boss:
            self.dash_timer += 1
            if self.dash_timer > 180 and not self.is_dashing:
                self.is_dashing = True
                self.dash_timer = 0
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.dash_target = (dx / dist, dy / dist)

            if self.is_dashing:
                self.x += self.dash_target[0] * 8
                self.y += self.dash_target[1] * 8
                afterimages.append(Afterimage(self.x, self.y, self.size, DARK_RED))
                
                if self.dash_timer > 20:
                    self.is_dashing = False
                    self.dash_timer = 0
            else:
                self.move_towards(player.x, player.y)
        else:
            self.move_towards(player.x, player.y)

    def move_towards(self, tx, ty):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x - self.size//2, self.y - self.size//2, self.size, self.size))
        bar_w = self.size
        bar_h = 4
        fill = max(0, (self.hp / self.max_hp)) * bar_w
        pygame.draw.rect(surface, GRAY, (self.x - bar_w//2, self.y - self.size//2 - 8, bar_w, bar_h))
        pygame.draw.rect(surface, RED, (self.x - bar_w//2, self.y - self.size//2 - 8, fill, bar_h))

# 공격 Slash
class AttackSlash:
    def __init__(self, x, y, target_x, target_y, radius_mult=1.0):
        self.x = x
        self.y = y
        self.duration = 8
        self.radius = int(30 * radius_mult)
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy) or 1
        self.slash_x = x + (dx / dist) * 35
        self.slash_y = y + (dy / dist) * 35

    def draw(self, surface):
        if self.duration > 0:
            pygame.draw.circle(surface, WHITE, (int(self.slash_x), int(self.slash_y)), self.radius, 3)
            self.duration -= 1

# 게임 초기 상태
player = Player()
monsters = []
slashes = []
afterimages = []

wave = 1
kills = 0
kills_required = 10
boss_spawned = False
game_paused_for_levelup = False
selected_skills = []

def get_random_skills():
    return random.sample(SKILL_LIST, 3)

def spawn_monster(is_boss=False):
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top': x, y = random.randint(0, WIDTH), -30
    elif side == 'bottom': x, y = random.randint(0, WIDTH), HEIGHT + 30
    elif side == 'left': x, y = -30, random.randint(0, HEIGHT)
    else: x, y = WIDTH + 30, random.randint(0, HEIGHT)

    if is_boss:
        return Monster(x, y, hp=500 + (wave * 100), speed=1.5, size=52, color=DARK_RED, is_boss=True)
    else:
        return Monster(x, y, hp=20 + (wave * 5), speed=random.uniform(1.2, 2.0), size=20, color=GREEN)

# 메인 게임 루프
running = True
font = pygame.font.SysFont(None, 26)
large_font = pygame.font.SysFont(None, 36)

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_paused_for_levelup:
            if event.type == pygame.KEYDOWN:
                chosen = None
                if event.key == pygame.K_1: chosen = selected_skills[0]
                elif event.key == pygame.K_2: chosen = selected_skills[1]
                elif event.key == pygame.K_3: chosen = selected_skills[2]

                if chosen:
                    # [수정] 스킬 데미지 및 성능 수치 강화
                    if chosen["type"] == "atk": player.damage *= 1.5  # 공격력 +50%
                    elif chosen["type"] == "atk_speed": player.max_cooldown = max(2, player.max_cooldown - 3) # 공속 상향
                    elif chosen["type"] == "speed": player.speed += 0.6
                    elif chosen["type"] == "max_hp": 
                        player.max_hp += 50
                        player.hp = min(player.max_hp, player.hp + 50)
                    elif chosen["type"] == "range": player.range_mult += 0.5 # 범위 +50%
                    
                    game_paused_for_levelup = False
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if player.attack_cooldown == 0:
                player.attack_cooldown = player.max_cooldown
                mx, my = pygame.mouse.get_pos()
                slashes.append(AttackSlash(player.x, player.y, mx, my, player.range_mult))
                
                for m in monsters:
                    dist_to_click = math.hypot(m.x - mx, m.y - my)
                    dist_to_player = math.hypot(m.x - player.x, m.y - player.y)
                    if dist_to_click < (50 * player.range_mult) or dist_to_player < (50 * player.range_mult):
                        m.hp -= player.damage  # 강화된 데미지 적용

    if game_paused_for_levelup:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = large_font.render("LEVEL UP! Select a Skill (Press 1, 2, 3)", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        for idx, skill in enumerate(selected_skills):
            box_rect = pygame.Rect(WIDTH//2 - 200, 200 + idx * 90, 400, 70)
            pygame.draw.rect(screen, GRAY, box_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, box_rect, 2, border_radius=8)

            txt = font.render(f"{idx+1}. {skill['name']} - {skill['desc']}", True, WHITE)
            screen.blit(txt, (box_rect.x + 15, box_rect.y + 25))

        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    player.move(keys)

    if wave % 5 == 0:
        if not boss_spawned and len(monsters) == 0:
            monsters.append(spawn_monster(is_boss=True))
            boss_spawned = True
    else:
        if len(monsters) < 5 + wave:
            monsters.append(spawn_monster(is_boss=False))

    for ai in afterimages[:]:
        if ai.alpha <= 0:
            afterimages.remove(ai)

    for m in monsters[:]:
        m.update(player, afterimages)
        
        if math.hypot(m.x - player.x, m.y - player.y) < (m.size // 2 + player.size // 2):
            player.hp -= 1.0 if m.is_boss else 0.3

        if m.hp <= 0:
            monsters.remove(m)
            kills += 1
            player.exp += 35
            
            if player.exp >= player.max_exp:
                player.level += 1
                player.exp -= player.max_exp
                player.max_exp = int(player.max_exp * 1.3)
                selected_skills = get_random_skills()
                game_paused_for_levelup = True

            if m.is_boss:
                boss_spawned = False
                kills = kills_required

    if kills >= kills_required:
        wave += 1
        kills = 0
        kills_required = 10 + (wave * 2)

    bg_color = (30, 30, 30) if wave % 5 != 0 else (50, 20, 20)
    screen.fill(bg_color)

    for ai in afterimages:
        ai.draw(screen)

    for slash in slashes[:]:
        slash.draw(screen)
        if slash.duration <= 0: slashes.remove(slash)

    for m in monsters:
        m.draw(screen)

    player.draw(screen)

    # UI
    hp_text = font.render(f"HP: {int(player.hp)}/{player.max_hp}", True, WHITE)
    wave_text = font.render(f"WAVE: {wave}", True, WHITE)
    kill_text = font.render(f"KILLS: {kills}/{kills_required}", True, WHITE)
    level_text = font.render(f"LVL: {player.level} (EXP: {player.exp}/{player.max_exp})", True, GOLD)
    dmg_text = font.render(f"ATK DMG: {int(player.damage)}", True, RED)

    screen.blit(hp_text, (20, 20))
    screen.blit(wave_text, (20, 45))
    screen.blit(kill_text, (20, 70))
    screen.blit(level_text, (20, 95))
    screen.blit(dmg_text, (20, 120))

    if wave % 5 == 0:
        boss_warning = font.render("!! BOSS WOLF APPROACHING !!", True, RED)
        screen.blit(boss_warning, (WIDTH // 2 - 130, 20))

    if player.hp <= 0:
        over_text = large_font.render("GAME OVER", True, RED)
        screen.blit(over_text, (WIDTH // 2 - 80, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()

pygame.quit()
