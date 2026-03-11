import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Doom")

clock = pygame.time.Clock()

# posição do jogador
player_x = 400
player_y = 300
player_speed = 5

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # teclas pressionadas
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    # fundo
    screen.fill((30,30,30))

    # jogador
    pygame.draw.circle(screen,(255,255,0),(player_x,player_y),10)

    pygame.display.update()

    clock.tick(60)

pygame.quit()
sys.exit()