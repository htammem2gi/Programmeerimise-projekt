import pygame
import sys
import json

with open("questions.json, "r", encoding = "utf-8") as f:
    andmed = json.load(f)

pygame.init()

# Ekraani seadistamine
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Point and Click seiklus")

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
