from enum import Enum

class livers(Enum):
    shrimp = 3
    fish = 2
    rock = 1
    empty = 0

class LifeGame(object):
    """
    Class for Game life
    """
    def __init__(self, ocean):
        self.ocean = ocean
        self.rows = len(ocean)
        self.cols = len(ocean[0]) if self.rows > 0 else 0

    def get_next_generation(self):
        new_ocean = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                neighbors = self._get_neighbors(i, j)
                fish_count = self._count_fish(neighbors)
                shrimp_count = self._count_shrimp(neighbors)
                new_ocean[i][j] = self._update_cell(self.ocean[i][j], fish_count, shrimp_count)
        self.ocean = new_ocean
        return self.ocean

    def _get_neighbors(self, i, j):
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    neighbors.append(self.ocean[ni][nj])
        return neighbors


    def _count_fish(self, neighbors):
        return neighbors.count(livers.fish.value)


    def _count_shrimp(self, neighbors):
        return neighbors.count(livers.shrimp.value)


    def _update_cell(self, cell, fish_count, shrimp_count):
        if cell == livers.rock.value:
            return livers.rock.value
        elif cell == livers.fish.value:
            if fish_count < 2 or fish_count >= 4:
                return livers.empty.value
            else:
                return livers.fish.value
        elif cell == livers.shrimp.value:
            if shrimp_count < 2 or shrimp_count >= 4:
                return livers.empty.value
            else:
                return livers.shrimp.value
        else:
            if fish_count == 3:
                return livers.fish.value
            elif shrimp_count == 3:
                return livers.shrimp.value
            else:
                return livers.empty.value
