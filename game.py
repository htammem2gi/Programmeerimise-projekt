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

# Taust - praegu lihtsalt ühtlane, hiljem saab pildi lisada
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((30, 34, 40))

clock = pygame.time.Clock()

class objekt:
    def __init__(self, nimi, rect, küsimus = None, valikud = None, vastus = None, osa_koodist = None):
        self.nimi = objekti_nimi
        self.rect = rect #asukoht
        self.küsimus = küsimus
        self.valikud = valikud
        self.vastus = vastus
        self.osa_koodist = osa_koodist

objektid = [] # veel mõtlemisel

aktiivne_objekt = None
kogutud_kood = ""
sisestatud_vastus = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Klikiti objetkil: {objekti_nimi}", event.pos)

    # rendering
    screen.blit(background, (0, 0))

    # Näidistekst, et fonti ka kasutataks
    text_surf = font.render("Tere! Kliki aknas.", True, (220, 220, 220))
    screen.blit(text_surf, (20, 20))

    pygame.display.flip()
    clock.tick(60)  # kuni 60 kaadrit sekundis

pygame.quit()
sys.exit()
