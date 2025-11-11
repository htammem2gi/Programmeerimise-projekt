import pygame
import sys
import json

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Point and Click Escape Room)
font = pygame.font.Font(DeterminationMonoWebRegular-Z5oq.ttf, suurus)               

background = 

# Mängu peatsükkel
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("Klikiti asukohas:", event.pos)

    screen.blit(background, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
