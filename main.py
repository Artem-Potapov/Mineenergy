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
        self.image = pygame.image.load(f"player.png").convert()
        self.rect = self.image.get_rect()

    def move_right(self, amount=16):
        self.rect.x += amount

    def move_left(self, amount=16):
        self.rect.x -= amount

    def move_down(self, amount=16):
        self.rect.y += amount

    def move_up(self, amount=16):
        self.rect.y -= amount

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
    if keys_active:
        print("scanning")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move_left(16)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move_right(16)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move_up(16)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move_down(16)
    else:
        print("not scanning")

    all_sprites.update()
    display.fill((0, 0, 0))
    all_sprites.draw(display)
    pygame.display.flip()

    clock.tick(FPS)