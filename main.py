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

    if not wall_collision(new_x, new_y):
        player_x = new_x
        player_y = new_y

    screen.fill((30, 30, 30))

    for row_index, row in enumerate(game_map):
        for col_index, tile in enumerate(row):
            if tile == "1":
                pygame.draw.rect(
                    screen,
                    (200, 200, 200),
                    (
                        col_index * TILE_SIZE,
                        row_index * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                )

    pygame.draw.circle(screen, (255, 255, 0), (int(player_x), int(player_y)), 8)

    line_x = player_x + math.cos(player_angle) * 40
    line_y = player_y + math.sin(player_angle) * 40

    pygame.draw.line(screen, (255, 0, 0), (player_x, player_y), (line_x, line_y), 3)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()