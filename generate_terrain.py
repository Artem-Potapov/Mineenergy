import random


def generate_terrain(terrain_h: int = 16, /, terrain_w: int = 16, n_clusters: int = 10) -> list[list[str]]:
    terrain = [["-" for j in range(terrain_w)] for i in range(terrain_h)]
    clusters = []

    for step in range(n_clusters):
        i = random.randint(1, terrain_h - 2 )
        j = random.randint(1, terrain_w - 2)
        terrain[i][j] = "C"
    
    for step in range(n_clusters):
        o = random.randint(1, terrain_h - 2)
        k = random.randint(1, terrain_w - 2)
        terrain[o][k] = "I"

    with open("TERRAIN.txt", "w") as file:
        for i in range(terrain_w):
            for j in range(terrain_h):
                print(terrain[i][j], end="")
                file.write(terrain[i][j])
                file.write("  ")
            file.write("\n")
            print()

    return terrain

generate_terrain()