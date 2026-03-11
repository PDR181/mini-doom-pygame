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

player_x = 150
player_y = 150
player_angle = 0
player_pitch = 0

player_speed = 3
mouse_sensitivity = 0.003

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

enemy_x = 400
enemy_y = 250
enemy_alive = True
enemy_size = 20

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

def draw_enemy(horizon_y):
    if not enemy_alive:
        return

    dx = enemy_x - player_x
    dy = enemy_y - player_y

    distance = math.sqrt(dx * dx + dy * dy)

    enemy_angle = math.atan2(dy, dx) - player_angle

    while enemy_angle > math.pi:
        enemy_angle -= 2 * math.pi
    while enemy_angle < -math.pi:
        enemy_angle += 2 * math.pi

    if -HALF_FOV < enemy_angle < HALF_FOV and distance > 20:
        screen_x = (WIDTH // 2) + (enemy_angle / DELTA_ANGLE) * SCALE

        size = min(300, int(SCREEN_DIST / (distance + 0.0001) * 40))
        screen_y = horizon_y - size // 2

        pygame.draw.rect(
            screen,
            (200, 50, 50),
            (
                int(screen_x - size // 2),
                int(screen_y),
                size,
                size
            )
        )

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

    if enemy_alive:
        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (int(enemy_x * MINIMAP_SCALE), int(enemy_y * MINIMAP_SCALE)),
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

def shoot_enemy():
    global enemy_alive

    if not enemy_alive:
        return

    dx = enemy_x - player_x
    dy = enemy_y - player_y

    distance = math.sqrt(dx * dx + dy * dy)
    enemy_angle = math.atan2(dy, dx) - player_angle

    while enemy_angle > math.pi:
        enemy_angle -= 2 * math.pi
    while enemy_angle < -math.pi:
        enemy_angle += 2 * math.pi

    aim_tolerance = 0.08

    if abs(enemy_angle) < aim_tolerance and distance < 500:
        enemy_alive = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not shooting:
                shooting = True
                shoot_timer = SHOOT_DURATION
                shoot_enemy()

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
    draw_enemy(horizon_y)
    draw_minimap()
    draw_crosshair()
    draw_weapon()

    pygame.display.update()
    clock.tick(60)

pygame.event.set_grab(False)
pygame.mouse.set_visible(True)
pygame.quit()
sys.exit()