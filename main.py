import math

import pygame
import os
import sys

script_directory = os.path.dirname(os.path.realpath(__file__))

pygame.init()
display = pygame.display.set_mode((640, 640))
#one block is 40px

FPS = 15
running = True
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load(f"player.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.width = self.rect.width // 2
        self.height = self.rect.height // 2
        self.rotation: float = 0
        self.center = self.rect.center

    def move_right(self, amount=16):
        self.rect.x += amount
        self.center = self.rect.center

    def move_left(self, amount=16):
        self.rect.x -= amount
        self.center = self.rect.center

    def move_down(self, amount=16):
        self.rect.y += amount
        self.center = self.rect.center

    def move_up(self, amount=16):
        self.rect.y -= amount

    def abs_rotate(self, amount: float):
        self.rotation = amount
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def rotate(self, amount: float):
        self.rotation = (self.rotation + amount) % 360  # Value will reapeat after 359. This prevents angle to overflow.
        self.abs_rotate(self.rotation)




all_sprites = pygame.sprite.Group()

player = Player()

all_sprites.add(player)

keys_active = 0

while running:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.KEYDOWN:
                keys_active += 1
            case pygame.KEYUP:
                keys_active -= 1
            case pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                theta = math.atan2(-(pos[1] - player.center[1]), pos[0] - player.center[0])
                theta = math.degrees(theta)
                player.abs_rotate(theta)
    if keys_active:
        #print("scanning")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move_left(16)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move_right(16)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move_up(16)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move_down(16)



    all_sprites.update()
    display.fill((0, 0, 0))
    all_sprites.draw(display)
    pygame.display.flip()

    clock.tick(FPS)