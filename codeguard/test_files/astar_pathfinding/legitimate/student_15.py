"""A* with weighted heuristic and path smoothing"""

import math

class WeightedAStar:
    def __init__(self, grid, weight=1.0):
        self.grid = grid
        self.weight = weight  # weight > 1 makes search faster but less optimal
        self.h = len(grid)
        self.w = len(grid[0])

    def dist(self, a, b):
        # Euclidean distance
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def neighbors(self, p):
        r, c = p
        n = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<self.h and 0<=nc<self.w and self.grid[nr][nc]==0:
                n.append((nr,nc))
        return n

    def run(self, start, goal):
        openset = {start}
        closed = set()
        gscore = {start: 0}
        fscore = {start: self.weight * self.dist(start, goal)}
        parent = {}

        while openset:
            curr = min(openset, key=lambda x: fscore.get(x, 1e9))

            if curr == goal:
                # build path
                p = [curr]
                while curr in parent:
                    curr = parent[curr]
                    p.append(curr)
                return p[::-1]

            openset.remove(curr)
            closed.add(curr)

            for nb in self.neighbors(curr):
                if nb in closed:
                    continue

                tent_g = gscore[curr] + 1

                if nb not in openset:
                    openset.add(nb)
                elif tent_g >= gscore.get(nb, 1e9):
                    continue

                parent[nb] = curr
                gscore[nb] = tent_g
                fscore[nb] = tent_g + self.weight * self.dist(nb, goal)

        return None

    def smooth_path(self, path):
        """Remove unnecessary waypoints"""
        if not path or len(path) <= 2:
            return path

        smoothed = [path[0]]
        i = 0

        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1:
                if self.line_of_sight(path[i], path[j]):
                    smoothed.append(path[j])
                    i = j
                    break
                j -= 1
            else:
                i += 1
                if i < len(path):
                    smoothed.append(path[i])

        return smoothed

    def line_of_sight(self, p1, p2):
        """Check if there's a clear line between two points"""
        x0, y0 = p1
        x1, y1 = p2

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            if self.grid[x0][y0] == 1:
                return False

            if x0 == x1 and y0 == y1:
                return True

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def show(self, path, start, goal):
        pset = set(path) if path else set()
        for i in range(self.h):
            for j in range(self.w):
                if (i,j)==start: print('S', end='')
                elif (i,j)==goal: print('G', end='')
                elif (i,j) in pset: print('*', end='')
                elif self.grid[i][j]==1: print('#', end='')
                else: print('.', end='')
            print()

maze = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,1,1,1,0],
    [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

finder = WeightedAStar(maze, weight=1.2)
p = finder.run((0,0), (8,14))

if p:
    print("Original path length:", len(p))
    finder.show(p, (0,0), (8,14))

    smooth = finder.smooth_path(p)
    print("\nSmoothed path length:", len(smooth))
    finder.show(smooth, (0,0), (8,14))
else:
    print("No path")
