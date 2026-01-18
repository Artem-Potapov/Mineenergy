import collections
import math
from abc import ABC, abstractmethod
from idlelib.macosx import hideTkConsole
from typing import List, overload, Sequence, Literal, Dict, LiteralString

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
all_sprites = pygame.sprite.Group()
util_sprites = pygame.sprite.GroupSingle()


class Highlighter(pygame.sprite.DirtySprite):
    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.image.load("highlight.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hide()

    def show(self, alpha: int=255) -> None:
        self.image.set_alpha(alpha)

    def hide(self) -> None:
        self.image.set_alpha(0)

    def move(self, point: Sequence[int], *, center: bool=False) -> None:
        x, y = point[0], point[1]

        if center:
            self.rect.center = (x, y)
            return
        self.rect.x = x
        self.rect.y = y

class GridPixel(ABC):
    def __init__(self, surf: pygame.surface.Surface,
                 ore: bool,
                 ore_type: Literal["COAL", "IRON", "GOLD", "DIAMOND"] | None,
                 *, highlighter: Highlighter):
        self.surface: pygame.surface.Surface = surf
        self.rect: pygame.rect.Rect = surf.get_rect()
        self.ore = ore
        self.ore_type = ore_type
        self.highlighter = highlighter

    @abstractmethod
    def mine(self) -> tuple[str, int] | None:  # 0 - block is not broken, 1 - is broken
        raise NotImplementedError

    @abstractmethod
    def highlight(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def unhighlight(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def reset_mining(self) -> None:
        raise NotImplementedError


class EmptyGridPixel(GridPixel):
    def __init__(self, surf: pygame.surface.Surface, *, highlighter: Highlighter):
        super().__init__(surf, False, None, highlighter=highlighter)

    def mine(self) -> None:
        return

    def highlight(self) -> None:
        self.highlighter.show(125)
        print(self.rect.center)
        print(self.rect.x, self.rect.y)
        self.highlighter.move(self.rect.center, center=True)

    def unhighlight(self) -> None:
        self.highlighter.hide()

    def reset_mining(self) -> None:
        print("mining reset")
        return


class OreGridPixel(GridPixel, ABC):
    def __init__(self, surf: pygame.surface.Surface,
                 ore_type: Literal["COAL", "IRON", "GOLD", "DIAMOND"],
                 *, highlighter: Highlighter):
        super().__init__(surf=surf, ore=True, ore_type=ore_type, highlighter=highlighter)
        self.mined_state = 0

    def highlight(self) -> None:
        self.highlighter.show(255)
        #print(self.rect.center)
        #print(self.rect.x, self.rect.y)
        self.highlighter.move(self.rect.center, center=True)
        #print("LET THERE BE LIGHT!")

    def unhighlight(self) -> None:
        self.highlighter.hide()
        self.mined_state = 0

    def reset_mining(self) -> None:
        print("ore mining reset")
        self.mined_state = 0


class OreGridCoal(OreGridPixel):
    def __init__(self, surf: pygame.surface.Surface,
                 *, highlighter: Highlighter):
        super().__init__(surf=surf, ore_type="COAL", highlighter=highlighter)

    def mine(self) -> tuple[Literal["COAL"], int]:
        if self.mined_state == 60:
            self.mined_state = 0
            return "COAL", 1
        self.mined_state += 1
        return "COAL", 0


class OreGridIron(OreGridPixel):
    def __init__(self, surf: pygame.surface.Surface,
                 *, highlighter: Highlighter):
        super().__init__(surf=surf, ore_type="IRON", highlighter=highlighter)

    def mine(self) -> tuple[Literal["IRON"], int]:
        if self.mined_state == 60:
            self.mined_state = 0
            return "IRON", 1
        self.mined_state += 1
        return "IRON", 0



class Grid:
    def __init__(self, w, h, *, highlighter: Highlighter):
        self.width = w
        self.height = h
        self.highlighter = highlighter
        # noinspection PyTypeChecker
        self._grid: List[List[GridPixel]] = [[... for i in range(w)] for j in range(h)]
        _terrain = generate_terrain(w, h, n_clusters=16)
        for i in range(self.height):
            for j in range(self.width):
                if _terrain[i][j] == "I":
                    _surf = pygame.surface.Surface((40,40)).convert()
                    _fill = (255,0,0)
                    pix = OreGridIron(_surf, highlighter=self.highlighter)
                elif _terrain[i][j] == "C":
                    _surf = pygame.surface.Surface((40, 40)).convert()
                    _fill = (0, 255, 0)
                    pix = OreGridCoal(_surf, highlighter=self.highlighter)
                else:
                    _surf = pygame.surface.Surface((40, 40)).convert()
                    _fill = (0, i * j, 255 - i * j)
                    pix = EmptyGridPixel(_surf, highlighter=self.highlighter)
                pix.rect.x = j * 40
                pix.rect.y = i * 40
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

    def mine(self, x_index: int, y_index: int) -> tuple[str, int]:
        return self._grid[y_index][x_index].mine()

    def reset_mining(self, x_index: int, y_index: int):
        self._grid[y_index][x_index].reset_mining()


class PlayerStats:
    def __init__(self):
        self.ore_mined: int = 0
        self.coal: int = 0
        self.iron: int = 0
        self.time_played: int = 0 #IN FRAMES!

    def add_ore(self, ore: str, amount: int):
        if ore.lower() == "coal":
            self.coal += amount
        elif ore.lower() == "iron":
            self.iron += amount


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
        self.stats = PlayerStats()

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
        self.center = self.rect.center

    def abs_rotate(self, amount: float):
        self.rotation = amount
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.
        self.center = (x, y)

    def rotate(self, amount: float):
        self.rotation = (self.rotation + amount) % 360  # Value will reapeat after 359. This prevents angle to overflow.
        self.abs_rotate(self.rotation)


class Pickaxe(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.swing_radius = 5
        # note, radius of the texture is |OB|, where B is the far end of the pickaxe, for a 40*40 player, 20px pickaxe and it sticking out at -13px from the center, radius is 42.0595


highlighter = Highlighter()
util_sprites.add(highlighter)

keys_active = 0
grid = Grid(16, 16, highlighter=highlighter)
lit_block = [0, 0]

player = Player()
all_sprites.add(player)

mouse_hold = False
block_highlighted = False

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
                # print(f"m_dist: {manhattan_distance(player.center, mouse_pos)}")
                # print(f"m_dist_blocks: {manhattan_distance_blocks(player.center, mouse_pos)}")
                # print(f"dist: {math.dist(player.center, mouse_pos)}")
                # print(f"dist_blocks: {math.dist(player.center, mouse_pos) // 40}")
                if math.dist(player.center, mouse_pos) // 40 <= 2:
                    block_highlighted = True
                    #note: there is an issue where because we're doing center math far edges don't count but closer ones do
                    new_lit_block = [mouse_pos[0] // 40, mouse_pos[1] // 40]
                    if lit_block != new_lit_block:
                        grid.light_down(lit_block)
                        lit_block = new_lit_block
                        grid.light_up(mouse_pos[0] // 40, mouse_pos[1] // 40)
                else:
                    block_highlighted = False
                    grid.light_down(lit_block)
                    highlighter.hide()
            case pygame.MOUSEBUTTONDOWN:
                mouse_hold = True
            case pygame.MOUSEBUTTONUP:
                mouse_hold = False
                grid.reset_mining(*lit_block)


    if mouse_hold and block_highlighted:
        mouse_pos = pygame.mouse.get_pos()
        tmp = grid.mine(mouse_pos[0] // 40, mouse_pos[1] // 40)
        if tmp:
            player.stats.add_ore(*tmp)
            print(f"C: {player.stats.coal}, I: {player.stats.iron}")

        # mine block

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

    #GRID UPDATES FIRST!
    grid.update()
    #Then sprites...
    all_sprites.update()
    util_sprites.update()
    #Draw the sprites
    util_sprites.draw(display)
    all_sprites.draw(display)
    pygame.display.flip()

    clock.tick(FPS)
