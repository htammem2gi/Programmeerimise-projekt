import pygame
import sys
import json

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Point and Click Escape Room)
font = pygame.font.Font(                        

# Põhivärvid ja taust
WHITE = (255, 255, 255)
background = pygame.Surface(screen.get_size())
background.fill(WHITE)

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
