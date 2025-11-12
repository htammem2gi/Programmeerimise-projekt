import pygame
import sys
import json  # võib jääda, kuigi hetkel ei kasuta

pygame.init()

# Aken
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Point and Click Escape Room")  # parandatud jutumärgid

# Font – kasutan süsteemifonti, et poleks .ttf faili vaja
FONT_SIZE = 24
font = pygame.font.SysFont(None, FONT_SIZE)

# Lihtne taust (ühtlane värv). Kui sul on pilt, vaata allpool kommentaari.
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((20, 24, 28))

clock = pygame.time.Clock()

# Mängu peatsükkel
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("Klikiti asukohas:", event.pos)

    # Joonistamine
    screen.blit(background, (0, 0))

    # Näidistekst, et fonti ka kasutataks
    text_surf = font.render("Tere! Kliki aknas.", True, (220, 220, 220))
    screen.blit(text_surf, (20, 20))

    pygame.display.flip()
    clock.tick(60)  # kuni 60 kaadrit sekundis

pygame.quit()
sys.exit()
