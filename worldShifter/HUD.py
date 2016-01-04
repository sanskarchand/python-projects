#/usr/bin/env python

import pygame
from const import *

'''
HUD module
For the player's healthbar
'''
HIGH_COL = (0, 255, 0)
LOW_COL = (200, 255, 0)


class HealthBar(pygame.sprite.Sprite):

    def __init__(self, pos):

        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]

        self.w = 100
        self.h = 20

        self.total_health = MAX_PLAYER_HEALTH
        self.fill_width = 0

        self.out_rect = pygame.Rect(pos, (self.w, self.h))

    def set_colour(self, health):
        "sets the colour of the healthbar according to the health"
        if float(health/self.total_health) * 100 < 50: # 50% health
            return LOW_COL
        return HIGH_COL
    def update(self, health, mainS):

        per_centage = float(health/self.total_health) * 100
        self.fill_width = (per_centage/100) * self.w


        self.draw(mainS, health)

    def draw(self, mainS, health):
        pygame.draw.rect(mainS, BLACK, self.out_rect, 2)
        elseRect = pygame.Rect((self.x+2, self.y+2), (self.fill_width-2, self.h -2))
        pygame.draw.rect(mainS, self.set_colour( health), elseRect)


class itemHUD(pygame.sprite.Sprite):

    def __init__(self, image, textColour, pos):

        pygame.sprite.Sprite.__init__(self)

        self.pos = pos
        self.colour = textColour
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(topleft=pos)
        self.text_pos = (self.pos[0] + self.rect.width + 10, self.pos[1] + 5)
        self.font = pygame.font.SysFont("comicsansms", 32)
        self.text = None


    def calc_item_text(self, counter):

        self.text = self.font.render(str(counter), True, self.colour)

    def update(self, counterString, player, screen):

        self.calc_item_text(getattr(player, counterString))
        self.draw(screen)

    def draw(self, screen):

        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_pos)
