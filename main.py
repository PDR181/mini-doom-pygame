import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Doom")

clock = pygame.time.Clock()

player_x = 400
player_y = 300
player_angle = 0
player_speed = 3
rotation_speed = 0.05

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # rotação
    if keys[pygame.K_LEFT]:
        player_angle -= rotation_speed
    if keys[pygame.K_RIGHT]:
        player_angle += rotation_speed

    # movimento para frente e trás
    if keys[pygame.K_w]:
        player_x += math.cos(player_angle) * player_speed
        player_y += math.sin(player_angle) * player_speed

    if keys[pygame.K_s]:
        player_x -= math.cos(player_angle) * player_speed
        player_y -= math.sin(player_angle) * player_speed

    screen.fill((30,30,30))

    pygame.draw.circle(screen,(255,255,0),(int(player_x),int(player_y)),10)

    # linha mostrando direção
    line_x = player_x + math.cos(player_angle) * 40
    line_y = player_y + math.sin(player_angle) * 40

    pygame.draw.line(screen,(255,0,0),(player_x,player_y),(line_x,line_y),3)

    pygame.display.update()

    clock.tick(60)

pygame.quit()
sys.exit()