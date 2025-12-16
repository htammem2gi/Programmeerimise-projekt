""" 
Heleri & Adele – 2D point-and-click põgenemismäng (Pygame)

Kuidas mäng töötab (lühidalt):
 - Näed klassiruumi tausta (pildid/background.png)
 - Klikid objektidel (arvutid, gloobus, raamatud, vihik...)
 - Iga objekt avab küsimuse (koodijupp + 4 valikut)
 - Õige vastus annab ühe tähe uksekoodist
 - Kui kõik tähed koos, kliki uksel ja sisesta kood

Kontrollid:
 - Hiireklikk: vali objekt / vali vastus / kliki uksel
 - 1-4: vali vastus klaviatuurilt
 - ESC: sulge küsimus / mine tagasi
 - F3: debug (näitab klikialasid ja prindib koordinaate)
 - R: reset (kustutab salvestuse)

Failid:
 - kusimused.json (küsimused + objektide asukohad)
 - salvestus.json (luuakse automaatselt; progress)
 - pildid/ (pildid)
 - fondid, muusika/DeterminationMonoWebRegular-Z5oq.ttf (valikuline font)
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

import pygame


# -------------------- Seaded --------------------

AKNA_LAIUS, AKNA_KORGUS = 800, 600
FPS = 60

# --- Elud / vead ---
MAKS_VEAD = 3
X_FLASH_MS = 650  # kui kaua punane X vilgub pärast viga

KUSIMUSTE_FAIL = "kusimused.json"
SALVESTUS_FAIL = "salvestus.json"

TAUST_FAIL = os.path.join("pildid", "background.png")
FONDI_FAIL = os.path.join("fondid, muusika", "DeterminationMonoWebRegular-Z5oq.ttf")

# Ukse klikiala (800x600 ekraanil)
UKSE_RECT = pygame.Rect(690, 145, 90, 330)


# -------------------- Andmemudel --------------------


@dataclass
class Kusimus:
    objekt: str
    nimi: str
    x: int
    y: int
    pilt: Optional[str]
    skaala: float
    kysimus: str
    kood: str
    valikud: list[str]
    oige_vastus: int  # indeks 0..3
    taht: str


class KlikitavObjekt:
    def __init__(self, kusimus: Kusimus, pilt_pind: Optional[pygame.Surface], jarjekord: int):
        self.kusimus = kusimus
        self.jarjekord = jarjekord
        self.lahendatud = False

        self.pilt_pind = pilt_pind
        if self.pilt_pind is not None:
            if abs(self.kusimus.skaala - 1.0) > 1e-6:
                uus_w = max(1, int(self.pilt_pind.get_width() * self.kusimus.skaala))
                uus_h = max(1, int(self.pilt_pind.get_height() * self.kusimus.skaala))
                self.pilt_pind = pygame.transform.smoothscale(self.pilt_pind, (uus_w, uus_h))
            self.rect = self.pilt_pind.get_rect(topleft=(self.kusimus.x, self.kusimus.y))
        else:
            # kui pilt puudub, loome nähtamatu ala
            self.rect = pygame.Rect(self.kusimus.x, self.kusimus.y, 120, 120)

    def joonista(self, ekraan: pygame.Surface, debug: bool, hiir_peal: bool):
        if self.pilt_pind is not None:
            ekraan.blit(self.pilt_pind, self.rect.topleft)

        if debug:
            varv = (0, 200, 0) if not self.lahendatud else (120, 120, 120)
            pygame.draw.rect(ekraan, varv, self.rect, 2)
            if hiir_peal:
                pygame.draw.rect(ekraan, (255, 255, 255), self.rect, 1)


# -------------------- Failiabi --------------------


def lae_pilt(tee: str) -> Optional[pygame.Surface]:
    if not tee:
        return None
    if not os.path.exists(tee):
        return None
    try:
        return pygame.image.load(tee).convert_alpha()
    except pygame.error:
        return None


def lae_taust() -> pygame.Surface:
    if os.path.exists(TAUST_FAIL):
        try:
            img = pygame.image.load(TAUST_FAIL).convert()
            return pygame.transform.smoothscale(img, (AKNA_LAIUS, AKNA_KORGUS))
        except pygame.error:
            pass
    # varutaust
    varu = pygame.Surface((AKNA_LAIUS, AKNA_KORGUS))
    varu.fill((30, 34, 40))
    return varu


def lae_font(suurus: int) -> pygame.font.Font:
    if os.path.exists(FONDI_FAIL):
        try:
            return pygame.font.Font(FONDI_FAIL, suurus)
        except pygame.error:
            pass
    return pygame.font.SysFont(None, suurus)


def murra_tekst(font: pygame.font.Font, tekst: str, max_laius: int) -> list[str]:
    sonad = tekst.split(" ")
    read: list[str] = []
    rida = ""
    for s in sonad:
        kandidaat = (rida + " " + s).strip()
        if font.size(kandidaat)[0] <= max_laius:
            rida = kandidaat
        else:
            if rida:
                read.append(rida)
            rida = s
    if rida:
        read.append(rida)
    return read


def loe_kusimused() -> list[Kusimus]:
    if not os.path.exists(KUSIMUSTE_FAIL):
        raise FileNotFoundError(
            f"Ei leidnud faili '{KUSIMUSTE_FAIL}'.\n"
            "Tee see fail (näidis on README-s) või kopeeri minu antud näidis."
        )

    with open(KUSIMUSTE_FAIL, "r", encoding="utf-8") as f:
        andmed = json.load(f)

    kusimused: list[Kusimus] = []
    for r in andmed:
        # lubame pilditeed kahel kujul:
        #  1) "arvuti.png" (automaatne pildid/)
        #  2) "pildid/arvuti.png" (otse)
        pilt = r.get("pilt")
        if pilt and not os.path.exists(pilt):
            kandidaadi_tee = os.path.join("pildid", pilt)
            if os.path.exists(kandidaadi_tee):
                pilt = kandidaadi_tee

        kusimused.append(
            Kusimus(
                objekt=r["objekt"],
                nimi=r.get("nimi", r["objekt"]),
                x=int(r["x"]),
                y=int(r["y"]),
                pilt=pilt,
                skaala=float(r.get("skaala", 1.0)),
                kysimus=r["küsimus"],
                kood=r.get("kood", ""),
                valikud=list(r.get("valikud", [])),
                oige_vastus=int(r.get("õige_vastus", 0)),
                taht=str(r.get("täht", "")),
            )
        )
    return kusimused


def lae_salvestus() -> dict:
    if not os.path.exists(SALVESTUS_FAIL):
        return {"lahendatud": [], "vead": 0}
    try:
        with open(SALVESTUS_FAIL, "r", encoding="utf-8") as f:
            data = json.load(f)
            # tagurpidi ühilduvus: vanas salvestuses polnud "vead"
            if "lahendatud" not in data:
                data["lahendatud"] = []
            if "vead" not in data:
                data["vead"] = 0
            return data
    except Exception:
        return {"lahendatud": [], "vead": 0}


def salvesta_salvestus(andmed: dict) -> None:
    with open(SALVESTUS_FAIL, "w", encoding="utf-8") as f:
        json.dump(andmed, f, ensure_ascii=False, indent=2)


def joonista_sydamed(ekraan: pygame.Surface, vead: int):
    """Joonistab elud (3 südant) ülariba paremasse serva."""

    def sydame_keskkoht(i: int) -> tuple[int, int]:
        # i=0 kõige parempoolsem
        x = AKNA_LAIUS - 26 - i * 30
        y = 24
        return x, y

    def joonista_sydame_kuju(kesk: tuple[int, int], varv: tuple[int, int, int]):
        x, y = kesk
        r = 8
        # kaks "mulli" + kolmnurk = lihtne süda
        pygame.draw.circle(ekraan, varv, (x - r, y - 3), r)
        pygame.draw.circle(ekraan, varv, (x + r, y - 3), r)
        pygame.draw.polygon(ekraan, varv, [(x - 2 * r, y - 2), (x + 2 * r, y - 2), (x, y + 2 * r)])

    elud = max(0, MAKS_VEAD - vead)
    for i in range(MAKS_VEAD):
        varv = (220, 60, 60) if i < elud else (120, 120, 120)
        joonista_sydame_kuju(sydame_keskkoht(i), varv)


# -------------------- UI --------------------


def joonista_varjund(ekraan: pygame.Surface):
    kiht = pygame.Surface((AKNA_LAIUS, AKNA_KORGUS), pygame.SRCALPHA)
    kiht.fill((0, 0, 0, 180))
    ekraan.blit(kiht, (0, 0))


def joonista_nupp(ekraan: pygame.Surface, font: pygame.font.Font, tekst: str, rect: pygame.Rect, hiir_peal: bool):
    taust = (70, 85, 105) if hiir_peal else (55, 65, 80)
    pygame.draw.rect(ekraan, taust, rect, border_radius=10)
    pygame.draw.rect(ekraan, (210, 210, 210), rect, 2, border_radius=10)
    s = font.render(tekst, True, (240, 240, 240))
    ekraan.blit(s, (rect.x + 12, rect.y + (rect.height - s.get_height()) // 2))


def main() -> None:
    pygame.init()
    ekraan = pygame.display.set_mode((AKNA_LAIUS, AKNA_KORGUS))
    pygame.display.set_caption("Heleri & Adele – Põgenemismäng")
    kell = pygame.time.Clock()

    font = lae_font(22)
    font_suur = lae_font(28)
    font_kood = pygame.font.SysFont("consolas", 18)

    taust = lae_taust()

    kusimused = loe_kusimused()

    objektid: list[KlikitavObjekt] = []
    for i, k in enumerate(kusimused):
        pilt = lae_pilt(k.pilt) if k.pilt else None
        objektid.append(KlikitavObjekt(k, pilt, jarjekord=i))

    # uksekood: tähtede jada JSON-is olevas järjekorras
    oodatav_kood = "".join([k.taht for k in kusimused])
    kood_nahtav = ["_"] * len(kusimused)

    # salvestus
    salvestus = lae_salvestus()
    lahendatud_id = set(salvestus.get("lahendatud", []))
    vead = int(salvestus.get("vead", 0))
    punane_x_lopp = 0  # pygame.time.get_ticks() millis
    for obj in objektid:
        if obj.kusimus.objekt in lahendatud_id:
            obj.lahendatud = True
            kood_nahtav[obj.jarjekord] = obj.kusimus.taht

    debug = False
    olek = "tuba"  # tuba | kusimus | lukk | voit | kaotus
    aktiivne: Optional[KlikitavObjekt] = None
    sisestatud_kood = ""
    teade = ""
    teade_lopp = 0

    def salvesta_progress() -> None:
        """Salvestab lahendatud objektid + vead."""
        salvesta_salvestus({"lahendatud": sorted(lahendatud_id), "vead": vead})

    def registreeri_viga(sonum: str = "Viga!"):
        nonlocal vead, olek, aktiivne, sisestatud_kood, punane_x_lopp
        vead += 1
        punane_x_lopp = pygame.time.get_ticks() + X_FLASH_MS
        naita_teadet(f"{sonum} (vead: {vead}/{MAKS_VEAD})", 1300)
        salvesta_progress()
        if vead >= MAKS_VEAD:
            olek = "kaotus"
            aktiivne = None
            sisestatud_kood = ""

    def naita_teadet(tekst: str, ms: int = 1500):
        nonlocal teade, teade_lopp
        teade = tekst
        teade_lopp = pygame.time.get_ticks() + ms

    def koik_lahendatud() -> bool:
        return all(o.lahendatud for o in objektid)

    while True:
        hiir = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F3:
                    debug = not debug
                    naita_teadet("DEBUG: " + ("SEES" if debug else "VÄLJAS"), 900)

                if ev.key == pygame.K_r:
                    # reset
                    if os.path.exists(SALVESTUS_FAIL):
                        os.remove(SALVESTUS_FAIL)
                    for o in objektid:
                        o.lahendatud = False
                    kood_nahtav = ["_"] * len(kusimused)
                    lahendatud_id.clear()
                    vead = 0
                    punane_x_lopp = 0
                    olek = "tuba"
                    aktiivne = None
                    sisestatud_kood = ""
                    naita_teadet("Reset tehtud.")

                if ev.key == pygame.K_ESCAPE:
                    if olek in ("kusimus", "lukk"):
                        olek = "tuba"
                        aktiivne = None
                        sisestatud_kood = ""
                    elif olek in ("voit", "kaotus"):
                        pygame.quit()
                        sys.exit()
                    else:
                        pygame.quit()
                        sys.exit()

                if olek == "kusimus" and aktiivne is not None:
                    if pygame.K_1 <= ev.key <= pygame.K_4:
                        valik = ev.key - pygame.K_1
                        if valik < len(aktiivne.kusimus.valikud):
                            # kontroll
                            if valik == aktiivne.kusimus.oige_vastus:
                                if not aktiivne.lahendatud:
                                    aktiivne.lahendatud = True
                                    kood_nahtav[aktiivne.jarjekord] = aktiivne.kusimus.taht
                                    lahendatud_id.add(aktiivne.kusimus.objekt)
                                    salvesta_progress()
                                naita_teadet(f"Õige! Täht: {aktiivne.kusimus.taht}")
                                olek = "tuba"
                                aktiivne = None
                            else:
                                registreeri_viga("Vale vastus")

                if olek == "lukk":
                    if ev.key == pygame.K_BACKSPACE:
                        sisestatud_kood = sisestatud_kood[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if sisestatud_kood.upper() == oodatav_kood.upper():
                            olek = "voit"
                        else:
                            registreeri_viga("Vale kood")
                            sisestatud_kood = ""
                    else:
                        if ev.unicode and ev.unicode.isprintable():
                            if len(sisestatud_kood) < len(oodatav_kood) + 4:
                                sisestatud_kood += ev.unicode

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if debug:
                    print("Klikk:", hiir, "olek:", olek)

                if olek == "tuba":
                    # uks
                    if UKSE_RECT.collidepoint(hiir):
                        if not koik_lahendatud():
                            naita_teadet(f"Uks on lukus. Tee kõik ülesanded ({kood_nahtav.count('_')}/{len(kood_nahtav)} puudu).")
                        else:
                            olek = "lukk"
                            sisestatud_kood = ""
                        continue

                    # objekt
                    for o in objektid:
                        if o.rect.collidepoint(hiir):
                            aktiivne = o
                            if o.lahendatud:
                                naita_teadet("See on juba lahendatud.")
                                aktiivne = None
                            else:
                                olek = "kusimus"
                            break

                elif olek == "kusimus" and aktiivne is not None:
                    # nupud
                    paneel = pygame.Rect(110, 70, 580, 460)
                    nupu_w = paneel.width - 40
                    nupu_h = 44
                    alg_y = paneel.bottom - (nupu_h + 12) * 4 - 18
                    for i in range(4):
                        nupp = pygame.Rect(paneel.x + 20, alg_y + i * (nupu_h + 12), nupu_w, nupu_h)
                        if nupp.collidepoint(hiir):
                            if i == aktiivne.kusimus.oige_vastus:
                                if not aktiivne.lahendatud:
                                    aktiivne.lahendatud = True
                                    kood_nahtav[aktiivne.jarjekord] = aktiivne.kusimus.taht
                                    lahendatud_id.add(aktiivne.kusimus.objekt)
                                    salvesta_progress()
                                naita_teadet(f"Õige! Täht: {aktiivne.kusimus.taht}")
                                olek = "tuba"
                                aktiivne = None
                            else:
                                registreeri_viga("Vale vastus")
                            break

        # -------------------- Joonistamine --------------------

        ekraan.blit(taust, (0, 0))

        # uks
        if debug:
            pygame.draw.rect(ekraan, (255, 255, 0), UKSE_RECT, 2)

        # objektid
        for o in objektid:
            o.joonista(ekraan, debug, o.rect.collidepoint(hiir))

        # ülariba
        pygame.draw.rect(ekraan, (18, 18, 22), pygame.Rect(0, 0, AKNA_LAIUS, 48))
        pygame.draw.line(ekraan, (80, 80, 80), (0, 48), (AKNA_LAIUS, 48), 2)
        ekraan.blit(font.render("Kood: " + " ".join(kood_nahtav), True, (240, 240, 240)), (14, 12))
        joonista_sydamed(ekraan, vead)

        # teade
        if teade and pygame.time.get_ticks() < teade_lopp:
            kast = pygame.Rect(14, AKNA_KORGUS - 52, AKNA_LAIUS - 28, 40)
            pygame.draw.rect(ekraan, (0, 0, 0), kast, border_radius=10)
            pygame.draw.rect(ekraan, (220, 220, 220), kast, 2, border_radius=10)
            ekraan.blit(font.render(teade, True, (240, 240, 240)), (kast.x + 12, kast.y + 10))

        # küsimuse aken
        if olek == "kusimus" and aktiivne is not None:
            joonista_varjund(ekraan)
            paneel = pygame.Rect(110, 70, 580, 460)
            pygame.draw.rect(ekraan, (25, 28, 34), paneel, border_radius=14)
            pygame.draw.rect(ekraan, (220, 220, 220), paneel, 2, border_radius=14)

            # pealkiri
            ekraan.blit(font_suur.render(aktiivne.kusimus.nimi, True, (245, 245, 245)), (paneel.x + 18, paneel.y + 12))

            # küsimus
            read = murra_tekst(font, aktiivne.kusimus.kysimus, paneel.width - 36)
            y = paneel.y + 54
            for r in read:
                ekraan.blit(font.render(r, True, (235, 235, 235)), (paneel.x + 18, y))
                y += 24

            # koodiblokk
            kood_rect = pygame.Rect(paneel.x + 18, y + 6, paneel.width - 36, 165)
            pygame.draw.rect(ekraan, (15, 16, 20), kood_rect, border_radius=10)
            pygame.draw.rect(ekraan, (90, 90, 90), kood_rect, 2, border_radius=10)
            ky = kood_rect.y + 10
            for r in aktiivne.kusimus.kood.split("\n")[:8]:
                ekraan.blit(font_kood.render(r, True, (210, 245, 210)), (kood_rect.x + 10, ky))
                ky += 20

            # valikud
            nupu_w = paneel.width - 40
            nupu_h = 44
            alg_y = paneel.bottom - (nupu_h + 12) * 4 - 18
            for i in range(4):
                nupp = pygame.Rect(paneel.x + 20, alg_y + i * (nupu_h + 12), nupu_w, nupu_h)
                tekst = aktiivne.kusimus.valikud[i] if i < len(aktiivne.kusimus.valikud) else "-"
                joonista_nupp(ekraan, font, f"{i+1}) {tekst}", nupp, nupp.collidepoint(hiir))

            ekraan.blit(font.render("ESC = tagasi", True, (200, 200, 200)), (paneel.x + 18, paneel.bottom - 28))

        # luku aken
        if olek == "lukk":
            joonista_varjund(ekraan)
            paneel = pygame.Rect(180, 190, 440, 220)
            pygame.draw.rect(ekraan, (25, 28, 34), paneel, border_radius=14)
            pygame.draw.rect(ekraan, (220, 220, 220), paneel, 2, border_radius=14)

            ekraan.blit(font_suur.render("Ukse lukk", True, (245, 245, 245)), (paneel.x + 18, paneel.y + 12))
            ekraan.blit(font.render(f"Sisesta kood ({len(oodatav_kood)} märki) ja ENTER.", True, (220, 220, 220)), (paneel.x + 18, paneel.y + 60))

            sis = pygame.Rect(paneel.x + 18, paneel.y + 100, paneel.width - 36, 52)
            pygame.draw.rect(ekraan, (15, 16, 20), sis, border_radius=10)
            pygame.draw.rect(ekraan, (90, 90, 90), sis, 2, border_radius=10)
            ekraan.blit(font_suur.render(sisestatud_kood, True, (245, 245, 245)), (sis.x + 10, sis.y + 10))
            ekraan.blit(font.render("ESC = tagasi", True, (200, 200, 200)), (paneel.x + 18, paneel.bottom - 28))

        # võit
        if olek == "voit":
            joonista_varjund(ekraan)
            t1 = font_suur.render("🎉 Põgenesid!", True, (255, 255, 255))
            t2 = font.render("ESC = sulge mäng", True, (220, 220, 220))
            ekraan.blit(t1, t1.get_rect(center=(AKNA_LAIUS // 2, 270)))
            ekraan.blit(t2, t2.get_rect(center=(AKNA_LAIUS // 2, 310)))

        # kaotus
        if olek == "kaotus":
            joonista_varjund(ekraan)
            t1 = font_suur.render("💥 Süda murdus…", True, (255, 255, 255))
            t2 = font.render(f"Sul sai {MAKS_VEAD} viga täis.", True, (220, 220, 220))
            t3 = font.render("R = proovi uuesti | ESC = sulge", True, (220, 220, 220))
            ekraan.blit(t1, t1.get_rect(center=(AKNA_LAIUS // 2, 255)))
            ekraan.blit(t2, t2.get_rect(center=(AKNA_LAIUS // 2, 295)))
            ekraan.blit(t3, t3.get_rect(center=(AKNA_LAIUS // 2, 330)))

        # punane X (vilgub pärast viga)
        if pygame.time.get_ticks() < punane_x_lopp:
            cx, cy = AKNA_LAIUS // 2, AKNA_KORGUS // 2
            pikkus = 70
            pygame.draw.line(ekraan, (230, 50, 50), (cx - pikkus, cy - pikkus), (cx + pikkus, cy + pikkus), 12)
            pygame.draw.line(ekraan, (230, 50, 50), (cx + pikkus, cy - pikkus), (cx - pikkus, cy + pikkus), 12)

        pygame.display.flip()
        kell.tick(FPS)


if __name__ == "__main__":
    main()
