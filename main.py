import pygame

pygame.init()
pygame.display.set_mode((800, 600))

FPS = 60
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(FPS)