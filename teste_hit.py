import pygame
import time

pygame.init()
pygame.mixer.init()

sound = pygame.mixer.Sound("assets/sounds/hit.wav")

print("Hit carregado")
sound.play()

time.sleep(3)