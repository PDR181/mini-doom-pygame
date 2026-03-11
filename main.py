import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Doom")

clock = pygame.time.Clock()

player_x = 150
player_y = 150
player_angle = 0

player_speed = 3
rotation_speed = 0.05

TILE_SIZE = 50

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCREEN_DIST = (WIDTH / 2) / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

MINIMAP_SCALE = 0.2

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

def cast_rays():
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
                depth *= math.cos(player_angle - ray_angle)

                wall_height = (TILE_SIZE / (depth + 0.0001)) * SCREEN_DIST

                color_value = max(20, 255 - depth // 2)
                color = (color_value, color_value, color_value)

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        ray * SCALE,
                        HEIGHT // 2 - wall_height // 2,
                        SCALE,
                        wall_height
                    )
                )
                break

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

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player_angle -= rotation_speed
    if keys[pygame.K_RIGHT]:
        player_angle += rotation_speed

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

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (60, 60, 60), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

    cast_rays()
    draw_minimap()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()