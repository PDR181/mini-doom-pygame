import pygame
import sys
import math
import random

pygame.init()

try:
    pygame.mixer.init()
    audio_enabled = True
except:
    audio_enabled = False

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Doom")

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

player_x = 96
player_y = 96
player_angle = 0
player_pitch = 0

player_speed = 3
mouse_sensitivity = 0.003
player_health = 100
score = 0
game_won = False
game_started = False
game_paused = False
damage_flash = 0
hit_feedback = 0

if audio_enabled:
    try:
        shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        shoot_sound.set_volume(0.5)
        print("shoot.wav carregado com sucesso")
    except Exception as e:
        print("Erro ao carregar shoot.wav:", e)
        shoot_sound = None

    try:
        hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
        hit_sound.set_volume(0.2)
        print("hit.wav carregado com sucesso")
    except Exception as e:
        print("Erro ao carregar hit.wav:", e)
        hit_sound = None
else:
    print("Audio desabilitado: mixer nao iniciou")
    shoot_sound = None
    hit_sound = None
    

TILE_SIZE = 64

wall_texture = pygame.image.load(
    "assets/textures/wall.png"
).convert()
wall_texture = pygame.transform.scale(
    wall_texture,
    (32, 32))
enemy_sprite = pygame.image.load(
    "assets/sprites/enemy_normal.png"
).convert_alpha()

pistol_sprite = pygame.image.load(
    "assets/sprites/weapons/pistol.png"
).convert_alpha()

shotgun_sprite = pygame.image.load(
    "assets/sprites/weapons/shotgun.png"
).convert_alpha()

shotgun_sprite = pygame.transform.scale(
    shotgun_sprite,
    (320, 320)
)

rifle_sprite = pygame.image.load(
    "assets/sprites/weapons/rifle.png"
).convert_alpha()

rifle_sprite = pygame.transform.scale(
    rifle_sprite,
    (320, 320)
)

pistol_sprite = pygame.transform.scale(
    pistol_sprite,
    (320, 320)
)

ammo_sprite = pygame.image.load(
    "assets/sprites/pickups/ammo.png"
).convert_alpha()

ammo_sprite = pygame.transform.scale(
    ammo_sprite,
    (48, 48)
)

medkit_sprite = pygame.image.load(
    "assets/sprites/pickups/medkit.png"
).convert_alpha()

medkit_sprite = pygame.transform.scale(
    medkit_sprite,
    (48, 48)
)

FOV = math.pi / 4.2
HALF_FOV = FOV / 2
NUM_RAYS = 80
MAX_DEPTH = 500
DELTA_ANGLE = FOV / NUM_RAYS
SCREEN_DIST = ((WIDTH / 2) / math.tan(HALF_FOV)) * 0.8
SCALE = WIDTH // NUM_RAYS

MINIMAP_SCALE = 0.14

shooting = False
shoot_timer = 0
mouse_held = False
SHOOT_DURATION = 8

MAX_AMMO = 30
ammo = MAX_AMMO

reloading = False
reload_timer = 0
RELOAD_DURATION = 40
weapon_cooldown = 0
WEAPON_COOLDOWN_TIME = 15

current_weapon = "pistol"

weapons = {
    "pistol": {
        "damage": 25,
        "cooldown": 4,
        "ammo": 12,
        "color": (80, 80, 80),
        "automatic": False
    },

    "rifle": {
        "damage": 10,
        "cooldown": 4,
        "ammo": 30,
        "color": (60, 60, 60),
        "automatic": True
    },

    "shotgun": {
        "damage": 18,
        "cooldown": 40,
        "ammo": 6,
        "color": (120, 70, 40),
        "automatic": False,
        "pellets": 6,
        "spread": 0.12
    }
}

MAX_AMMO = weapons[current_weapon]["ammo"]
ammo = MAX_AMMO

owned_weapons = ["pistol", "rifle", "shotgun"]

enemy_hit_damage = 25

# """ spawn_timer = 0
# SPAWN_INTERVAL = 180
# MAX_ENEMIES = 6

# wave = 1
# wave_timer = 0
# WAVE_DURATION = 600

game_map = [
    "11111111111111111111",
    "10000000100000000001",
    "10111100100111110001",
    "10000100000010000001",
    "10100111110010111001",
    "10000000010010000001",
    "10111111010011111001",
    "10000001000000001001",
    "10111101111111101001",
    "10000000000000100001",
    "10111111111110101101",
    "10000000000000100001",
    "10111111101111111001",
    "10000000100000000001",
    "10111100111111111001",
    "10000100000000000001",
    "10110111111111111001",
    "10000000000000000001",
    "10001111111111111001",
    "11111111111111111111"
]

def create_enemy(x, y, enemy_type):
    if enemy_type == "fast":
        return {
            "x": x,
            "y": y,
            "health": 60,
            "max_health": 60,
            "alive": True,
            "cooldown": 0,
            "dropped_loot": False,
            "type": "fast",
            "speed": 2.0,
            "damage": 8,
            "color": (255, 180, 60),
            "size_multiplier": 0.8
        }

    if enemy_type == "tank":
        return {
            "x": x,
            "y": y,
            "health": 180,
            "max_health": 180,
            "alive": True,
            "cooldown": 0,
            "dropped_loot": False,
            "type": "tank",
            "speed": 0.8,
            "damage": 15,
            "color": (120, 60, 200),
            "size_multiplier": 1.25
        }

    return {
        "x": x,
        "y": y,
        "health": 100,
        "max_health": 100,
        "alive": True,
        "cooldown": 0,
        "dropped_loot": False,
        "type": "normal",
        "speed": 1.2,
        "damage": 10,
        "color": (200, 50, 50),
        "size_multiplier": 1.0
    }

enemies = [

    # Entrada
    create_enemy(320, 128, "normal"),

    # Corredores
    create_enemy(512, 192, "normal"),
    create_enemy(640, 256, "fast"),

    # Storage
    create_enemy(768, 384, "normal"),
    create_enemy(832, 448, "fast"),

    # Laboratório
    create_enemy(512, 640, "tank"),
    create_enemy(704, 640, "normal"),

    # Containment
    create_enemy(960, 768, "fast"),
    create_enemy(1024, 832, "tank"),

    # Core Chamber
    create_enemy(1088, 960, "tank"),
]

pickups = []

enemy_projectiles = []

weapon_pickups = []

core_zone = {
    "x": 1088,
    "y": 960,
    "radius": 80
}

def wall_collision(x, y):
    map_x = int(x / TILE_SIZE)
    map_y = int(y / TILE_SIZE)

    if map_y < 0 or map_y >= len(game_map):
        return True
    if map_x < 0 or map_x >= len(game_map[0]):
        return True

    return game_map[map_y][map_x] == "1"

def can_see_enemy(enemy_x, enemy_y):
    dx = enemy_x - player_x
    dy = enemy_y - player_y

    distance = math.sqrt(dx * dx + dy * dy)

    steps = int(distance / 2)

    if steps <= 0:
        return True

    for i in range(steps):
        check_x = player_x + (dx / steps) * i
        check_y = player_y + (dy / steps) * i

        if wall_collision(check_x, check_y):
            return False

    return True

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
                wall_height = min(
                    HEIGHT * 0.9,
                    (TILE_SIZE / (corrected_depth + 0.0001)) * (SCREEN_DIST * 0.45)
                )

                color_value = max(20, 255 - corrected_depth // 2)
                color = (color_value, color_value, color_value)

                if abs(math.cos(ray_angle)) > abs(math.sin(ray_angle)):
                    texture_x = int(target_y % TILE_SIZE)
                else:
                    texture_x = int(target_x % TILE_SIZE)

                slice_width = 1

                texture_column = wall_texture.subsurface(
                    (texture_x % 30),
                    0,
                    slice_width,
                    32
                )

                texture_column = pygame.transform.scale(
                    texture_column,
                    (max(2, SCALE + 1), int(wall_height))
                )

                shade = max(40, 255 - int(corrected_depth * 0.15))

                # texture_column.fill(
                #     (shade, shade, shade),
                #     special_flags=pygame.BLEND_MULT
                # )

                screen.blit(
                    texture_column,
                    (
                        ray * SCALE,
                        horizon_y - wall_height // 2
                    )
                )

                # darkness = pygame.Surface((max(1, SCALE), int(wall_height)))
                # fog_alpha = min(220, int(corrected_depth * 0.7))

                # darkness.set_alpha(fog_alpha)
                # darkness.fill((0, 0, 0))

                # screen.blit(
                #     darkness,
                #     (
                #         ray * SCALE,
                #         horizon_y - wall_height // 2
                #     )
                # )

def move_enemies():
    global player_health, damage_flash

    for enemy in enemies:
        if not enemy["alive"]:
            continue

        dx = player_x - enemy["x"]
        dy = player_y - enemy["y"]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            attack_distance = 220

        if distance > attack_distance:
            move_x = (dx / distance) * enemy["speed"]
            move_y = (dy / distance) * enemy["speed"]

            new_enemy_x = enemy["x"] + move_x
            new_enemy_y = enemy["y"] + move_y

            if not wall_collision(new_enemy_x, enemy["y"]):
                enemy["x"] = new_enemy_x

            if not wall_collision(enemy["x"], new_enemy_y):
                enemy["y"] = new_enemy_y

        if enemy["cooldown"] > 0:
            enemy["cooldown"] -= 1

        if distance < 260 and enemy["cooldown"] == 0:
            if can_see_enemy(enemy["x"], enemy["y"]):
                enemy_shoot(enemy)
                enemy["cooldown"] = 90

def enemy_shoot(enemy):
    if not can_see_enemy(enemy["x"], enemy["y"]):
        return

    dx = player_x - enemy["x"]
    dy = player_y - enemy["y"]

    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        return

    speed = 4

    enemy_projectiles.append({
        "x": enemy["x"],
        "y": enemy["y"],
        "dx": (dx / distance) * speed,
        "dy": (dy / distance) * speed,
        "damage": enemy["damage"]
    })


def update_enemy_projectiles():
    global player_health, damage_flash

    to_remove = []

    for projectile in enemy_projectiles:
        projectile["x"] += projectile["dx"]
        projectile["y"] += projectile["dy"]

        if wall_collision(projectile["x"], projectile["y"]):
            to_remove.append(projectile)
            continue

        dx = projectile["x"] - player_x
        dy = projectile["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 20:
            player_health -= projectile["damage"]
            damage_flash = 10
            to_remove.append(projectile)

    for projectile in to_remove:
        if projectile in enemy_projectiles:
            enemy_projectiles.remove(projectile)

def draw_enemy_projectiles(horizon_y):
    for projectile in enemy_projectiles:
        dx = projectile["x"] - player_x
        dy = projectile["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        angle = math.atan2(dy, dx) - player_angle

        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        if -HALF_FOV < angle < HALF_FOV and distance > 10:
            screen_x = (WIDTH // 2) + (angle / DELTA_ANGLE) * SCALE

            size = int(SCREEN_DIST / (distance + 0.0001) * 4)

            screen_y = horizon_y - size // 2

            outer_size = max(2, size + 1)
            inner_size = max(1, size // 2)

            # brilho externo
            pygame.draw.circle(
                screen,
                (255, 40, 40),
                (int(screen_x), int(screen_y)),
                outer_size + 4
            )

            # camada média
            pygame.draw.circle(
                screen,
                (255, 120, 120),
                (int(screen_x), int(screen_y)),
                outer_size
            )

            # núcleo
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(screen_x), int(screen_y)),
                inner_size
            )

            # rastro
            trail_x = int(screen_x - projectile["dx"] * 3)
            trail_y = int(screen_y - projectile["dy"] * 3)

            pygame.draw.line(
                screen,
                (255, 80, 80),
                (trail_x, trail_y),
                (int(screen_x), int(screen_y)),
                3
            )
# def choose_enemy_type():
#     if wave >= 6:
#         return random.choice(["normal", "fast", "tank"])
#     if wave >= 4:
#         return random.choice(["normal", "fast", "tank", "fast"])
#     if wave >= 2:
#         return random.choice(["normal", "normal", "fast"])
#     return "normal"

# def spawn_enemy():
#     alive_count = sum(1 for enemy in enemies if enemy["alive"])

#     if alive_count >= MAX_ENEMIES:
#         return

#     spawn_points = [
#         {"x": 400, "y": 250},
#         {"x": 300, "y": 300},
#         {"x": 500, "y": 200},
#         {"x": 450, "y": 150},
#         {"x": 200, "y": 250},
#         {"x": 350, "y": 150},
#     ]

#     for point in spawn_points:
#         too_close_to_enemy = False

#         for enemy in enemies:
#             if enemy["alive"]:
#                 dx = enemy["x"] - point["x"]
#                 dy = enemy["y"] - point["y"]
#                 distance = math.sqrt(dx * dx + dy * dy)

#                 if distance < 40:
#                     too_close_to_enemy = True
#                     break

#         dx_player = player_x - point["x"]
#         dy_player = player_y - point["y"]

#         distance_player = math.sqrt(
#             dx_player * dx_player + dy_player * dy_player
#         )

#         if distance_player < 80:
#             continue

#         if not wall_collision(point["x"], point["y"]) and not too_close_to_enemy:
#             enemy_type = choose_enemy_type()
#             enemies.append(create_enemy(point["x"], point["y"], enemy_type))
#             break


def spawn_pickup(x, y):
    pickup_type = random.choice(["ammo", "medkit"])

    pickups.append({
        "x": x,
        "y": y,
        "type": pickup_type
    })

    # spawn_points = [
    #     {"x": 400, "y": 250},
    #     {"x": 300, "y": 300},
    #     {"x": 500, "y": 200},
    #     {"x": 450, "y": 150},
    #     {"x": 200, "y": 250},
    #     {"x": 350, "y": 150},
    # ]

    # for point in spawn_points:
    #     too_close_to_enemy = False

    #     for enemy in enemies:
    #         if enemy["alive"]:
    #             dx = enemy["x"] - point["x"]
    #             dy = enemy["y"] - point["y"]
    #             distance = math.sqrt(dx * dx + dy * dy)

    #             if distance < 40:
    #                 too_close_to_enemy = True
    #                 break

    #     dx_player = player_x - point["x"]
    #     dy_player = player_y - point["y"]
    #     distance_player = math.sqrt(dx_player * dx_player + dy_player * dy_player)

    #     if distance_player < 80:
    #         continue

    #     if not wall_collision(point["x"], point["y"]) and not too_close_to_enemy:
    #         enemy_type = choose_enemy_type()
    #         enemies.append(create_enemy(point["x"], point["y"], enemy_type))
    #         break

# def update_wave():
#     global wave, wave_timer, SPAWN_INTERVAL

#     wave_timer += 1

#     if wave_timer >= WAVE_DURATION:
#         wave += 1
#         wave_timer = 0
#         SPAWN_INTERVAL = max(60, SPAWN_INTERVAL - 15)

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

        if (
            -HALF_FOV < angle < HALF_FOV
            and distance > 20
            and can_see_enemy(enemy["x"], enemy["y"])
        ):
            visible_enemies.append((distance, angle, enemy))

    visible_enemies.sort(reverse=True, key=lambda item: item[0])

    for distance, angle, enemy in visible_enemies:
        screen_x = (WIDTH // 2) + (angle / DELTA_ANGLE) * SCALE

        base_size = int(SCREEN_DIST / (distance + 0.0001) * 40)
        size = min(320, int(base_size * enemy["size_multiplier"]))
        screen_y = horizon_y - size // 2

        enemy_sprite_scaled = pygame.transform.scale(
            enemy_sprite,
            (size, size)
        )

        screen.blit(
            enemy_sprite_scaled,
            (
                int(screen_x - size // 2),
                int(screen_y)
            )
        )

        bar_width = size
        bar_height = 8
        bar_x = int(screen_x - size // 2)
        bar_y = int(screen_y - 15)

        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        current_bar_width = int((enemy["health"] / enemy["max_health"]) * bar_width)
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, current_bar_width, bar_height))

def draw_pickups(horizon_y):
    for pickup in pickups:
        dx = pickup["x"] - player_x
        dy = pickup["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        angle = math.atan2(dy, dx) - player_angle

        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        if -HALF_FOV < angle < HALF_FOV and distance > 20:
            screen_x = (WIDTH // 2) + (angle / DELTA_ANGLE) * SCALE

            size = int(SCREEN_DIST / (distance + 0.0001) * 10)

            screen_y = horizon_y - size // 2 + 40

            pickup_size = max(18, size * 2)

            if pickup["type"] == "ammo":

                sprite = ammo_sprite

                screen.blit(
                    sprite,
                    (
                        int(screen_x - pickup_size // 2),
                        int(screen_y - pickup_size // 2)
                    )
                )

            elif pickup["type"] == "medkit":

                sprite = medkit_sprite

                screen.blit(
                    sprite,
                    (
                        int(screen_x - pickup_size // 2),
                        int(screen_y - pickup_size // 2)
                    )
                )

def update_pickups():
    global ammo, player_health

    collected = []

    for pickup in pickups:
        dx = pickup["x"] - player_x
        dy = pickup["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 30:
            if pickup["type"] == "ammo":
                ammo = min(MAX_AMMO, ammo + 6)

            elif pickup["type"] == "medkit":
                player_health = min(100, player_health + 25)

            collected.append(pickup)

    for pickup in collected:
        pickups.remove(pickup)

def draw_weapon_pickups(horizon_y):
    for pickup in weapon_pickups:
        dx = pickup["x"] - player_x
        dy = pickup["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        angle = math.atan2(dy, dx) - player_angle

        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        if -HALF_FOV < angle < HALF_FOV and distance > 20:
            screen_x = (WIDTH // 2) + (angle / DELTA_ANGLE) * SCALE

            size = int(SCREEN_DIST / (distance + 0.0001) * 10)

            screen_y = horizon_y - size // 2 + 40

            color = (255, 220, 50)

            if pickup["weapon"] == "shotgun":
                color = (255, 120, 50)

            pygame.draw.rect(
                screen,
                color,
                (
                    int(screen_x - size // 2),
                    int(screen_y),
                    size,
                    size // 2
                )
            )

def update_weapon_pickups():
    global current_weapon

    collected = []

    for pickup in weapon_pickups:
        dx = pickup["x"] - player_x
        dy = pickup["y"] - player_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 40:
            weapon_name = pickup["weapon"]

            if weapon_name not in owned_weapons:
                owned_weapons.append(weapon_name)

            current_weapon = weapon_name

            collected.append(pickup)

    for pickup in collected:
        weapon_pickups.remove(pickup)

def update_core_zone():
    global game_won

    dx = player_x - core_zone["x"]
    dy = player_y - core_zone["y"]

    distance = math.sqrt(dx * dx + dy * dy)

    if distance < core_zone["radius"]:
        game_won = True

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
                enemy["color"],
                (int(enemy["x"] * MINIMAP_SCALE), int(enemy["y"] * MINIMAP_SCALE)),
                4
            )
    
    pygame.draw.circle(
    screen,
    (255, 0, 255),
    (
        int(core_zone["x"] * MINIMAP_SCALE),
        int(core_zone["y"] * MINIMAP_SCALE)
    ),
    6
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

    color = (0, 255, 0) if hit_feedback > 0 else (255, 255, 255)

    pygame.draw.line(screen, color, (center_x - 10, center_y), (center_x + 10, center_y), 2)
    pygame.draw.line(screen, color, (center_x, center_y - 10), (center_x, center_y + 10), 2)

def draw_weapon():
    weapon_x = WIDTH // 2 - 160
    weapon_y = HEIGHT - 260

    if shooting:
        weapon_y += 12

    if reloading:
        weapon_y += 35

    if current_weapon == "pistol":
        screen.blit(
            pistol_sprite,
            (weapon_x, weapon_y)
        )

    elif current_weapon == "rifle":
        screen.blit(
            rifle_sprite,
            (weapon_x, weapon_y)
        )

    elif current_weapon == "shotgun":
        screen.blit(
            shotgun_sprite,
            (weapon_x, weapon_y)
        )

    if shooting:
        flash_x = WIDTH // 2
        flash_y = weapon_y + 40

        pygame.draw.circle(
            screen,
            (255, 180, 60),
            (flash_x, flash_y),
            28
        )

        pygame.draw.circle(
            screen,
            (255, 255, 220),
            (flash_x, flash_y),
            14
        )

def draw_hud():
    ambient_overlay = pygame.Surface((WIDTH, HEIGHT))
    ambient_overlay.set_alpha(18)
    ambient_overlay.fill((120, 0, 0))

    screen.blit(ambient_overlay, (0, 0))
    health_text = font.render(f"Vida: {player_health}", True, (255, 255, 255))
    score_text = font.render(f"Pontos: {score}", True, (255, 255, 255))
    #wave_text = font.render(f"Wave: {wave}", True, (255, 255, 255))
    ammo_text = font.render(f"Municao: {ammo}/{MAX_AMMO}", True, (255, 255, 255))
    weapon_text = font.render(f"Arma: {current_weapon.upper()}", True, (255, 255, 255))

    hud_surface = pygame.Surface((WIDTH, 70))
    hud_surface.set_alpha(170)
    hud_surface.fill((10, 10, 10))

    screen.blit(hud_surface, (0, HEIGHT - 70))

    pygame.draw.line(
        screen,
        (120, 0, 0),
        (0, HEIGHT - 70),
        (WIDTH, HEIGHT - 70),
        3
    )

    screen.blit(health_text, (30, HEIGHT - 48))
    screen.blit(ammo_text, (250, HEIGHT - 48))
    screen.blit(score_text, (470, HEIGHT - 48))
    screen.blit(weapon_text, (650, HEIGHT - 48))

    
def shoot_enemy():
    global score, hit_feedback

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

        if current_weapon == "shotgun":

            total_damage = (
                weapons[current_weapon]["damage"] *
                weapons[current_weapon]["pellets"]
            )

            enemy["health"] -= total_damage

        else:
            enemy["health"] -= weapons[current_weapon]["damage"]
        hit_feedback = 6

        if hit_sound:
            hit_sound.play()

        if enemy["health"] <= 0:
            enemy["health"] = 0
            enemy["alive"] = False
            score += 100

        if not enemy["dropped_loot"]:
            if random.random() < 0.4:
                spawn_pickup(enemy["x"], enemy["y"])

            enemy["dropped_loot"] = True

def reset_game():
    global player_x, player_y, player_angle, player_pitch
    global player_health, score, game_won
    global game_started, game_paused
    global damage_flash, hit_feedback
    global shooting, shoot_timer
    global enemies
    global pickups
    global weapon_pickups
    global enemy_projectiles
    global ammo, reloading, reload_timer
    global weapon_cooldown
    global mouse_held

    player_x = 96
    player_y = 96
    player_angle = 0
    player_pitch = 0

    player_health = 100
    score = 0
    game_won = False
    game_started = False
    game_paused = False
    damage_flash = 0
    hit_feedback = 0

    shooting = False
    shoot_timer = 0
    mouse_held = False
    ammo = MAX_AMMO
    reloading = False
    reload_timer = 0
    weapon_cooldown = 0

    pickups = []

    enemy_projectiles = []

    weapon_pickups = []

    
    enemies = [

    # Entrada
    create_enemy(320, 128, "normal"),

    # Corredores
    create_enemy(512, 192, "normal"),
    create_enemy(640, 256, "fast"),

    # Storage
    create_enemy(768, 384, "normal"),
    create_enemy(832, 448, "fast"),

    # Laboratório
    create_enemy(512, 640, "tank"),
    create_enemy(704, 640, "normal"),

    # Containment
    create_enemy(960, 768, "fast"),
    create_enemy(1024, 832, "tank"),

    # Core Chamber
    create_enemy(1088, 960, "tank"),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_held = True

                if not weapons[current_weapon]["automatic"]:
                    if not shooting and player_health > 0 and ammo > 0 and not reloading and weapon_cooldown <= 0:
                        shooting = True
                        shoot_timer = SHOOT_DURATION

                        if shoot_sound:
                            shoot_sound.play()

                        ammo -= 1
                        weapon_cooldown = weapons[current_weapon]["cooldown"]

                        shoot_enemy()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_held = False

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_ESCAPE and game_started:
                game_paused = not game_paused
            
            if game_paused:

                if event.key == pygame.K_r:
                    reset_game()

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if not game_started:
                if event.key == pygame.K_RETURN:
                    game_started = True

            if event.key == pygame.K_r and (player_health <= 0 or game_won):
                reset_game()
            if event.key == pygame.K_r and ammo < MAX_AMMO and not reloading and player_health > 0:
                reloading = True
                reload_timer = RELOAD_DURATION
            
            if event.key == pygame.K_1 and "pistol" in owned_weapons:
                current_weapon = "pistol"
                MAX_AMMO = weapons[current_weapon]["ammo"]

                if ammo > MAX_AMMO:
                    ammo = MAX_AMMO

            if event.key == pygame.K_2 and "rifle" in owned_weapons:
                current_weapon = "rifle"
                MAX_AMMO = weapons[current_weapon]["ammo"]

                if ammo > MAX_AMMO:
                    ammo = MAX_AMMO

            if event.key == pygame.K_3 and "shotgun" in owned_weapons:
                current_weapon = "shotgun"
                MAX_AMMO = weapons[current_weapon]["ammo"]

                if ammo > MAX_AMMO:
                    ammo = MAX_AMMO

    if player_health > 0 and game_started and not game_won and not game_paused:
        mouse_dx, mouse_dy = pygame.mouse.get_rel()

        player_angle += mouse_dx * mouse_sensitivity
        player_pitch -= mouse_dy * mouse_sensitivity

        player_pitch = max(-0.5, min(0.5, player_pitch))

        keys = pygame.key.get_pressed()

        new_x = player_x
        new_y = player_y

        if weapons[current_weapon]["automatic"]:
            if mouse_held and ammo > 0 and not reloading and weapon_cooldown <= 0:
                shooting = True
                shoot_timer = SHOOT_DURATION

                if shoot_sound:
                    shoot_sound.play()

                ammo -= 1
                weapon_cooldown = weapons[current_weapon]["cooldown"]

                shoot_enemy()

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
        update_enemy_projectiles()
        update_pickups()
        update_weapon_pickups()
        update_core_zone()
        #update_wave()

        # spawn_timer += 1
        # if spawn_timer >= SPAWN_INTERVAL:
        #     spawn_enemy()
        #     spawn_timer = 0
    else:
        pygame.mouse.get_rel()

    if shooting:
        shoot_timer -= 1
        if shoot_timer <= 0:
            shooting = False

    if damage_flash > 0:
        damage_flash -= 1

    if hit_feedback > 0:
        hit_feedback -= 1
    
    if reloading:
        reload_timer -= 1

        if reload_timer <= 0:
            ammo = MAX_AMMO
            reloading = False
    
    if weapon_cooldown > 0:
        weapon_cooldown -= 1
    
    horizon_offset = int(player_pitch * 200)
    horizon_y = HEIGHT // 2 + horizon_offset

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, horizon_y))
    
    for y in range(horizon_y, HEIGHT):

        distance_factor = (y - horizon_y) / (HEIGHT - horizon_y + 0.0001)

        brightness = max(
            8,
            int(110 - distance_factor * 95)
        )

        pygame.draw.line(
            screen,
            (
            brightness // 2,
            brightness // 4,
            brightness // 5
        ),
            (0, y),
            (WIDTH, y)
        )

        if y % 10 == 0:
            pygame.draw.line(
                screen,
                (brightness + 15, brightness // 2, brightness // 3),
                (0, y),
                (WIDTH, y),
                1
            )

    cast_rays(horizon_y)
    draw_enemies(horizon_y)
    draw_enemy_projectiles(horizon_y)
    draw_pickups(horizon_y)
    draw_weapon_pickups(horizon_y)
    draw_minimap()
    draw_crosshair()
    draw_weapon()
    draw_hud()

    if damage_flash > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(40)
        overlay.fill((255, 0, 0))
        screen.blit(overlay, (0, 0))

    if hit_feedback > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(20)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))

    if player_health <= 0:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont("arial", 56, bold=True)

        game_over_title = title_font.render(
            "SYSTEM FAILURE",
            True,
            (255, 50, 50)
        )

        subtitle_text = font.render(
            "Hellcore containment lost.",
            True,
            (220, 220, 220)
        )

        restart_text = font.render(
            "Pressione R para reiniciar",
            True,
            (255, 255, 255)
        )

        quit_text = font.render(
            "Pressione Q para sair",
            True,
            (180, 180, 180)
        )

        screen.blit(
            game_over_title,
            (WIDTH // 2 - 220, HEIGHT // 2 - 120)
        )

        screen.blit(
            subtitle_text,
            (WIDTH // 2 - 140, HEIGHT // 2 - 40)
        )

        screen.blit(
            restart_text,
            (WIDTH // 2 - 140, HEIGHT // 2 + 30)
        )

        screen.blit(
            quit_text,
            (WIDTH // 2 - 100, HEIGHT // 2 + 70)
        )

    if game_won:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont("arial", 56, bold=True)

        victory_title = title_font.render(
            "MISSION COMPLETE",
            True,
            (255, 60, 60)
        )

        victory_subtitle = font.render(
            "Hellcore containment restored.",
            True,
            (220, 220, 220)
        )

        score_text = font.render(
            f"Pontuacao Final: {score}",
            True,
            (255, 255, 255)
        )

        restart_text = font.render(
            "Pressione R para jogar novamente",
            True,
            (200, 200, 200)
        )

        screen.blit(victory_title, (WIDTH // 2 - 220, HEIGHT // 2 - 120))
        screen.blit(victory_subtitle, (WIDTH // 2 - 170, HEIGHT // 2 - 40))
        screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
        screen.blit(restart_text, (WIDTH // 2 - 170, HEIGHT // 2 + 80))

    if not game_started:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont("arial", 52, bold=True)

        title = title_font.render("HELLCORE", True, (255, 50, 50))
        subtitle = font.render("Containment Breach", True, (200, 200, 200))

        start_text = font.render("Pressione ENTER para iniciar", True, (255, 255, 255))

        controls_1 = font.render("WASD - mover", True, (180, 180, 180))
        controls_2 = font.render("Mouse - mirar", True, (180, 180, 180))
        controls_3 = font.render("R - recarregar", True, (180, 180, 180))

        screen.blit(title, (WIDTH // 2 - 140, HEIGHT // 2 - 140))
        screen.blit(subtitle, (WIDTH // 2 - 110, HEIGHT // 2 - 90))

        screen.blit(start_text, (WIDTH // 2 - 150, HEIGHT // 2))

        screen.blit(controls_1, (WIDTH // 2 - 80, HEIGHT // 2 + 70))
        screen.blit(controls_2, (WIDTH // 2 - 80, HEIGHT // 2 + 100))
        screen.blit(controls_3, (WIDTH // 2 - 80, HEIGHT // 2 + 130))

    if game_paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont("arial", 52, bold=True)

        pause_title = title_font.render(
            "PAUSED",
            True,
            (255, 60, 60)
        )

        continue_text = font.render(
            "ESC - continuar",
            True,
            (255, 255, 255)
        )

        restart_text = font.render(
            "R - reiniciar",
            True,
            (255, 255, 255)
        )

        quit_text = font.render(
            "Q - sair",
            True,
            (255, 255, 255)
        )

        screen.blit(
            pause_title,
            (WIDTH // 2 - 110, HEIGHT // 2 - 120)
        )

        screen.blit(
            continue_text,
            (WIDTH // 2 - 90, HEIGHT // 2 - 30)
        )

        screen.blit(
            restart_text,
            (WIDTH // 2 - 90, HEIGHT // 2 + 10)
        )

        screen.blit(
            quit_text,
            (WIDTH // 2 - 90, HEIGHT // 2 + 50)
        )

    pygame.display.update()
    clock.tick(60)

pygame.event.set_grab(False)
pygame.mouse.set_visible(True)
pygame.quit()
sys.exit()