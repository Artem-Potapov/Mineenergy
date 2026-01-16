import collections
import math
from abc import ABC, abstractmethod
from typing import List, overload, Sequence, Literal

import pygame
import os
import sys

from generate_terrain import generate_terrain
from util import manhattan_distance, manhattan_distance_blocks

script_directory = os.path.dirname(os.path.realpath(__file__))

pygame.init()
display = pygame.display.set_mode((640, 640))
#one block is 40px

FPS = 60
running = True
clock = pygame.time.Clock()


class GridPixel(ABC):
    def __init__(self, surf: pygame.surface.Surface,
                 rect: pygame.rect.Rect,
                 ore: bool,
                 ore_type: Literal["COAL", "IRON", "GOLD", "DIAMOND"] | None):
        self.surface: pygame.surface.Surface = surf
        self.rect: pygame.rect.Rect = rect
        self.ore = False
        self.ore_type = None

    @abstractmethod
    def mine(self) -> int:  # 0 - block is not broken, 1 - is broken
        raise NotImplementedError

    @abstractmethod
    def highlight(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def unhighlight(self) -> None:
        raise NotImplementedError


class EmptyGridPixel(GridPixel):
    def __init__(self, surf: pygame.surface.Surface,
                 rect: pygame.rect.Rect):
        super().__init__(surf, rect, False, None)

    def mine(self) -> int:
        return 0  #you can't mine emptiness...

    def highlight(self) -> None:
        self.surface.get_offset()

    def unhighlight(self) -> None:
        raise NotImplementedError


class OreGridPixel(GridPixel, ABC):
    def __init__(self, surf: pygame.surface.Surface,
                 rect: pygame.rect.Rect,
                 ore_type: Literal["COAL", "IRON", "GOLD", "DIAMOND"]):
        super().__init__(surf, rect, True, ore_type)


class OreGridCoal(OreGridPixel):
    def __init__(self, surf: pygame.surface.Surface,
                 rect: pygame.rect.Rect):
        super().__init__(surf, rect, "COAL")

    def mine(self) -> int:
        pass

    def highlight(self) -> None:
        pass

    def unhighlight(self) -> None:
        pass


class OreGridIron(OreGridPixel):
    def __init__(self, surf: pygame.surface.Surface,
                 rect: pygame.rect.Rect):
        super().__init__(surf, rect, "IRON")

    def mine(self) -> int:
        pass

    def highlight(self) -> None:
        pass

    def unhighlight(self) -> None:
        pass


class Grid:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        # noinspection PyTypeChecker
        self._grid: List[List[GridPixel]] = [[... for i in range(w)] for j in range(h)]
        _terrain = generate_terrain(w, h, n_clusters=16)
        for i in range(self.height):
            for j in range(self.width):
                if _terrain[i][j] == "C":
                    _surf = pygame.surface.Surface((40, 40)).convert()
                    _fill = (255, 255, 255)
                    pix = OreGridCoal(_surf, _surf.get_rect())
                else:
                    _surf = pygame.surface.Surface((40, 40)).convert()
                    _fill = (0, i * j, 255 - i * j)
                    pix = EmptyGridPixel(_surf, _surf.get_rect())
                rect = pix.surface.get_rect()
                rect.x = j * 40
                rect.y = i * 40
                print(i, j)
                pix.surface.fill(_fill)
                self._grid[i][j] = pix

    def update(self):
        for i in range(self.height):
            for j in range(self.width):
                display.blit(self._grid[i][j].surface, (j * 40, i * 40))

    @overload
    def light_up(self, x_index: int, y_index: int, /):
        ...

    @overload
    def light_up(self, index: Sequence[int], /):
        ...

    def light_up(self, arg1: Sequence[int] | int, arg2: int | None = None, /) -> None:
        if isinstance(arg1, Sequence):
            x_index, y_index = arg1[0], arg1[1]
        else:
            x_index, y_index = arg1, arg2
        self._grid[y_index][x_index].highlight()

    @overload
    def light_down(self, x_index: int, y_index: int, /):
        ...

    @overload
    def light_down(self, index: Sequence[int], /):
        ...

    def light_down(self, arg1: Sequence[int] | int, arg2: int | None = None, /) -> None:
        if isinstance(arg1, Sequence):
            x_index, y_index = arg1[0], arg1[1]
        else:
            x_index, y_index = arg1, arg2
        self._grid[y_index][x_index].unhighlight()


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
        self.speed = 4

    def move_right(self):
        self.rect.x += self.speed
        self.center = self.rect.center

    def move_left(self):
        self.rect.x -= self.speed
        self.center = self.rect.center

    def move_down(self):
        self.rect.y += self.speed
        self.center = self.rect.center

    def move_up(self):
        self.rect.y -= self.speed

    def abs_rotate(self, amount: float):
        self.rotation = amount
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def rotate(self, amount: float):
        self.rotation = (self.rotation + amount) % 360  # Value will reapeat after 359. This prevents angle to overflow.
        self.abs_rotate(self.rotation)


class Pickaxe(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.swing_radius = 5
        # note, radius of the texture is |OB|, where B is the far end of the pickaxe, for a 40*40 player, 20px pickaxe and it sticking out at -13px from the center, radius is 42.0595

    def swing(self):
        ...
        math.dist()


all_sprites = pygame.sprite.Group()

player = Player()

all_sprites.add(player)

keys_active = 0
grid = Grid(16, 16)
lit_block = [0, 0]

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
                mouse_pos = pygame.mouse.get_pos()
                theta = math.atan2(-(mouse_pos[1] - player.center[1]), mouse_pos[0] - player.center[0])
                theta = math.degrees(theta)
                player.abs_rotate(theta)
                block_center_pos = [40 * (mouse_pos[0] // 40), 40 * (mouse_pos[1] // 40)]
                print(f"m_dist: {manhattan_distance(player.center, mouse_pos)}")
                print(f"m_dist_blocks: {manhattan_distance_blocks(player.center, mouse_pos)}")
                print(f"dist: {math.dist(player.center, mouse_pos)}")
                print(f"dist_blocks: {math.dist(player.center, mouse_pos) // 40}")
                if math.dist(player.center, mouse_pos) // 40 <= 2:
                    #note: there is an issue where because we're doing center math far edges don't count but closer ones do
                    new_lit_block = [mouse_pos[0] // 40, mouse_pos[1] // 40]
                    if lit_block != new_lit_block:
                        grid.light_down(lit_block)
                        lit_block = new_lit_block
                    grid.light_up(mouse_pos[0] // 40, mouse_pos[1] // 40)
                else:
                    grid.light_down(lit_block)

    if keys_active:
        #print("scanning")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move_right()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move_down()

    all_sprites.update()
    display.fill((0, 0, 0))
    grid.update()
    all_sprites.draw(display)
    pygame.display.flip()

    clock.tick(FPS)
