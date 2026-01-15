from typing import Iterable, Sequence


def manhattan_distance(point1: Sequence[int], point2: Sequence[int], /) -> int:
    distance = sum(abs(p1 - p2) for p1, p2 in zip(point1, point2))
    return distance

def manhattan_distance_blocks(point1: Sequence[int], point2: Sequence[int], block_size: int = 40, /) -> int:
    block_point1_x = point1[0] // block_size
    block_point1_y = point1[1] // block_size
    block_point2_x = point2[0] // block_size
    block_point2_y = point2[1] // block_size
    print(f"point1: {block_point1_x}, {block_point1_y}, point2: {block_point2_x}, {block_point2_y}")
    return manhattan_distance((block_point1_x, block_point1_y), (block_point2_x, block_point2_y))
