import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Doom")

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

player_x = 150
player_y = 150
player_angle = 0
player_pitch = 0

player_speed = 3
mouse_sensitivity = 0.003
player_health = 100
score = 0

TILE_SIZE = 50

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCREEN_DIST = (WIDTH / 2) / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

MINIMAP_SCALE = 0.2

shooting = False
shoot_timer = 0
SHOOT_DURATION = 8

enemy_speed = 1.2
enemy_damage = 10
enemy_damage_cooldown_frames = 30
enemy_hit_damage = 25

spawn_timer = 0
SPAWN_INTERVAL = 180
MAX_ENEMIES = 6

wave = 1
wave_timer = 0
WAVE_DURATION = 600

enemies = [
    {"x": 400, "y": 250, "health": 100, "max_health": 100, "alive": True, "cooldown": 0}
]

game_map = [
    "111111111111",
    "100000000001",
    "100011000001",
    "100000000001",
    "101000001001",
    "100000000001",
    "111111111111"
]

def wall_collision(x, y):
    map_x = int(x / TILE_SIZE)
    map_y = int(y / TILE_SIZE)

    if map_y < 0 or map_y >= len(game_map):
        return True
    if map_x < 0 or map_x >= len(game_map[0]):
        return True

    return game_map[map_y][map_x] == "1"

def cast_rays(horizon_y):
    start_angle = player_angle - HALF_FOV

    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * DELTA_ANGLE

        for depth in range(1, MAX_DEPTH):
            target_x = player_x + math.cos(ray_angle) * depth
            target_y = player_y + math.sin(ray_angle) * depth

            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)

            if row < 0 or row >= len(game_map) or col < 0 or col >= len(game_map[0]):
                break

            if game_map[row][col] == "1":
                corrected_depth = depth * math.cos(player_angle - ray_angle)
                wall_height = (TILE_SIZE / (corrected_depth + 0.0001)) * SCREEN_DIST

                color_value = max(20, 255 - corrected_depth // 2)
                color = (color_value, color_value, color_value)

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        ray * SCALE,
                        horizon_y - wall_height // 2,
                        SCALE,
                        wall_height
                    )
                )
                break

def move_enemies():
    global player_health

    for enemy in enemies:
        if not enemy["alive"]:
            continue

        dx = player_x - enemy["x"]
        dy = player_y - enemy["y"]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            move_x = (dx / distance) * enemy_speed
            move_y = (dy / distance) * enemy_speed

            new_enemy_x = enemy["x"] + move_x
            new_enemy_y = enemy["y"] + move_y

            if not wall_collision(new_enemy_x, enemy["y"]):
                enemy["x"] = new_enemy_x

            if not wall_collision(enemy["x"], new_enemy_y):
                enemy["y"] = new_enemy_y

        if enemy["cooldown"] > 0:
            enemy["cooldown"] -= 1

        if distance < 25 and enemy["cooldown"] == 0:
            player_health -= enemy_damage
            enemy["cooldown"] = enemy_damage_cooldown_frames

def spawn_enemy():
    alive_count = sum(1 for enemy in enemies if enemy["alive"])
    if alive_count >= MAX_ENEMIES:
        return

    spawn_points = [
        {"x": 400, "y": 250},
        {"x": 300, "y": 300},
        {"x": 500, "y": 200},
        {"x": 450, "y": 150},
        {"x": 200, "y": 250},
        {"x": 350, "y": 150},
    ]

    for point in spawn_points:
        too_close_to_enemy = False

        for enemy in enemies:
            if enemy["alive"]:
                dx = enemy["x"] - point["x"]
                dy = enemy["y"] - point["y"]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < 40:
                    too_close_to_enemy = True
                    break

        dx_player = player_x - point["x"]
        dy_player = player_y - point["y"]
        distance_player = math.sqrt(dx_player * dx_player + dy_player * dy_player)

        if distance_player < 80:
            continue

        if not wall_collision(point["x"], point["y"]) and not too_close_to_enemy:
            enemies.append({
                "x": point["x"],
                "y": point["y"],
                "health": 100,
                "max_health": 100,
                "alive": True,
                "cooldown": 0
            })
            break

def update_wave():
    global wave, wave_timer, SPAWN_INTERVAL, enemy_speed

    wave_timer += 1

    if wave_timer >= WAVE_DURATION:
        wave += 1
        wave_timer = 0

        SPAWN_INTERVAL = max(60, SPAWN_INTERVAL - 15)
        enemy_speed += 0.1

def draw_enemies(horizon_y):
    visible_enemies = []

    for enemy in enemies:
        if not enemy["alive"]:
            continue

        dx = enemy["x"] - player_x
        dy = enemy["y"] - player_y
        distance = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx) - player_angle

        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi

        if -HALF_FOV < angle < HALF_FOV and distance > 20:
            visible_enemies.append((distance, angle, enemy))

    visible_enemies.sort(reverse=True, key=lambda item: item[0])

    for distance, angle, enemy in visible_enemies:
        screen_x = (WIDTH // 2) + (angle / DELTA_ANGLE) * SCALE

        size = min(300, int(SCREEN_DIST / (distance + 0.0001) * 40))
        screen_y = horizon_y - size // 2

        enemy_rect = pygame.Rect(
            int(screen_x - size // 2),
            int(screen_y),
            size,
            size
        )

        pygame.draw.rect(screen, (200, 50, 50), enemy_rect)

        pygame.draw.rect(
            screen,
            (255, 220, 220),
            (
                int(screen_x - size // 4),
                int(screen_y + size // 5),
                size // 6,
                size // 6
            )
        )

        pygame.draw.rect(
            screen,
            (255, 220, 220),
            (
                int(screen_x + size // 10),
                int(screen_y + size // 5),
                size // 6,
                size // 6
            )
        )

        bar_width = size
        bar_height = 8
        bar_x = int(screen_x - size // 2)
        bar_y = int(screen_y - 15)

        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        current_bar_width = int((enemy["health"] / enemy["max_health"]) * bar_width)
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, current_bar_width, bar_height))

def draw_minimap():
    for row_index, row in enumerate(game_map):
        for col_index, tile in enumerate(row):
            color = (200, 200, 200) if tile == "1" else (40, 40, 40)

            pygame.draw.rect(
                screen,
                color,
                (
                    col_index * TILE_SIZE * MINIMAP_SCALE,
                    row_index * TILE_SIZE * MINIMAP_SCALE,
                    TILE_SIZE * MINIMAP_SCALE,
                    TILE_SIZE * MINIMAP_SCALE
                )
            )

    for enemy in enemies:
        if enemy["alive"]:
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (int(enemy["x"] * MINIMAP_SCALE), int(enemy["y"] * MINIMAP_SCALE)),
                4
            )

    pygame.draw.circle(
        screen,
        (255, 255, 0),
        (int(player_x * MINIMAP_SCALE), int(player_y * MINIMAP_SCALE)),
        4
    )

    line_x = player_x + math.cos(player_angle) * 30
    line_y = player_y + math.sin(player_angle) * 30

    pygame.draw.line(
        screen,
        (255, 0, 0),
        (player_x * MINIMAP_SCALE, player_y * MINIMAP_SCALE),
        (line_x * MINIMAP_SCALE, line_y * MINIMAP_SCALE),
        2
    )

def draw_crosshair():
    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    pygame.draw.line(screen, (255, 255, 255), (center_x - 10, center_y), (center_x + 10, center_y), 2)
    pygame.draw.line(screen, (255, 255, 255), (center_x, center_y - 10), (center_x, center_y + 10), 2)

def draw_weapon():
    weapon_width = 140
    weapon_height = 90

    weapon_x = WIDTH // 2 - weapon_width // 2
    weapon_y = HEIGHT - weapon_height - 20

    if shooting:
        weapon_y += 10

    pygame.draw.rect(screen, (80, 80, 80), (weapon_x, weapon_y, weapon_width, weapon_height))
    pygame.draw.rect(screen, (40, 40, 40), (weapon_x + 20, weapon_y + 20, 100, 50))

    barrel_width = 30
    barrel_height = 60
    barrel_x = WIDTH // 2 - barrel_width // 2
    barrel_y = weapon_y - 20

    pygame.draw.rect(screen, (120, 120, 120), (barrel_x, barrel_y, barrel_width, barrel_height))

    if shooting:
        flash_size = 20
        flash_x = WIDTH // 2
        flash_y = barrel_y - 10

        pygame.draw.circle(screen, (255, 220, 100), (flash_x, flash_y), flash_size)
        pygame.draw.circle(screen, (255, 255, 180), (flash_x, flash_y), flash_size // 2)

def draw_hud():
    health_text = font.render(f"Vida: {player_health}", True, (255, 255, 255))
    enemies_alive = sum(1 for enemy in enemies if enemy["alive"])
    enemy_text = font.render(f"Inimigos: {enemies_alive}", True, (255, 255, 255))
    score_text = font.render(f"Pontos: {score}", True, (255, 255, 255))
    wave_text = font.render(f"Wave: {wave}", True, (255, 255, 255))

    screen.blit(health_text, (10, HEIGHT - 35))
    screen.blit(enemy_text, (10, HEIGHT - 65))
    screen.blit(score_text, (10, HEIGHT - 95))
    screen.blit(wave_text, (10, HEIGHT - 125))

def shoot_enemy():
    global score

    visible_targets = []

    for enemy in enemies:
        if not enemy["alive"]:
            continue

        dx = enemy["x"] - player_x
        dy = enemy["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)
        enemy_angle = math.atan2(dy, dx) - player_angle

        while enemy_angle > math.pi:
            enemy_angle -= 2 * math.pi
        while enemy_angle < -math.pi:
            enemy_angle += 2 * math.pi

        aim_tolerance = 0.08

        if abs(enemy_angle) < aim_tolerance and distance < 500:
            visible_targets.append((distance, enemy))

    if visible_targets:
        visible_targets.sort(key=lambda item: item[0])
        _, enemy = visible_targets[0]

        enemy["health"] -= enemy_hit_damage
        if enemy["health"] <= 0:
            enemy["health"] = 0
            enemy["alive"] = False
            score += 100

def reset_game():
    global player_x, player_y, player_angle, player_pitch
    global player_health, score
    global shooting, shoot_timer
    global enemy_speed, spawn_timer, SPAWN_INTERVAL
    global wave, wave_timer
    global enemies

    player_x = 150
    player_y = 150
    player_angle = 0
    player_pitch = 0

    player_health = 100
    score = 0

    shooting = False
    shoot_timer = 0

    enemy_speed = 1.2
    spawn_timer = 0
    SPAWN_INTERVAL = 180

    wave = 1
    wave_timer = 0

    enemies = [
        {"x": 400, "y": 250, "health": 100, "max_health": 100, "alive": True, "cooldown": 0}
    ]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not shooting and player_health > 0:
                shooting = True
                shoot_timer = SHOOT_DURATION
                shoot_enemy()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and player_health <= 0:
                reset_game()

    if player_health > 0:
        mouse_dx, mouse_dy = pygame.mouse.get_rel()

        player_angle += mouse_dx * mouse_sensitivity
        player_pitch -= mouse_dy * mouse_sensitivity

        player_pitch = max(-0.5, min(0.5, player_pitch))

        keys = pygame.key.get_pressed()

        new_x = player_x
        new_y = player_y

        if keys[pygame.K_w]:
            new_x += math.cos(player_angle) * player_speed
            new_y += math.sin(player_angle) * player_speed

        if keys[pygame.K_s]:
            new_x -= math.cos(player_angle) * player_speed
            new_y -= math.sin(player_angle) * player_speed

        if keys[pygame.K_a]:
            new_x += math.cos(player_angle - math.pi / 2) * player_speed
            new_y += math.sin(player_angle - math.pi / 2) * player_speed

        if keys[pygame.K_d]:
            new_x += math.cos(player_angle + math.pi / 2) * player_speed
            new_y += math.sin(player_angle + math.pi / 2) * player_speed

        if not wall_collision(new_x, new_y):
            player_x = new_x
            player_y = new_y

        move_enemies()
        update_wave()

        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_enemy()
            spawn_timer = 0
    else:
        pygame.mouse.get_rel()

    if shooting:
        shoot_timer -= 1
        if shoot_timer <= 0:
            shooting = False

    horizon_offset = int(player_pitch * 200)
    horizon_y = HEIGHT // 2 + horizon_offset

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, horizon_y))
    pygame.draw.rect(screen, (60, 60, 60), (0, horizon_y, WIDTH, HEIGHT - horizon_y))

    cast_rays(horizon_y)
    draw_enemies(horizon_y)
    draw_minimap()
    draw_crosshair()
    draw_weapon()
    draw_hud()

    if player_health <= 0:
        game_over_text = font.render("GAME OVER", True, (255, 50, 50))
        restart_text = font.render("Pressione R para reiniciar", True, (255, 255, 255))

        screen.blit(game_over_text, (WIDTH // 2 - 70, HEIGHT // 2 - 30))
        screen.blit(restart_text, (WIDTH // 2 - 130, HEIGHT // 2 + 10))

    pygame.display.update()
    clock.tick(60)

pygame.event.set_grab(False)
pygame.mouse.set_visible(True)
pygame.quit()
sys.exit()