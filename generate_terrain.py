import random


def generate_terrain(terrain_h: int = 8, /, terrain_w: int = 8, n_clusters: int = 4) -> list[list[str]]:
    terrain = [["#" for j in range(terrain_w)] for i in range(terrain_h)]

    clusters = []

    for step in range(n_clusters):
        i = random.randint(1, terrain_h - 2 )
        j = random.randint(1, terrain_w - 2)
        terrain[i][j] = "C"



    print(*terrain, sep="\n")
    return terrain

generate_terrain()