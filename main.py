import pygame
import os
import sys

script_directory = os.path.dirname(os.path.realpath(__file__))

pygame.init()
display = pygame.display.set_mode((800, 600))

FPS = 60
running = True
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(f"player.png").convert()

        self.rect = self.image.get_rect()

        display.blit(self.image, (0,0 ))

player = Player()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()

    clock.tick(FPS)

    #test