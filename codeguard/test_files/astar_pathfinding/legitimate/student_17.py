"""
A* with Multiple Heuristics and Performance Metrics
Student 17
"""

import time
from heapq import heappush, heappop

class MultiHeuristicAStar:
    """A* that can use different heuristics"""

    HEURISTICS = {
        'manhattan': lambda p1, p2: abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]),
        'euclidean': lambda p1, p2: ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5,
        'chebyshev': lambda p1, p2: max(abs(p1[0]-p2[0]), abs(p1[1]-p2[1])),
        'octile': lambda p1, p2: max(abs(p1[0]-p2[0]), abs(p1[1]-p2[1])) + (1.414-1)*min(abs(p1[0]-p2[0]), abs(p1[1]-p2[1]))
    }

    def __init__(self, grid, heuristic_name='manhattan'):
        self.grid = grid
        self.h_func = self.HEURISTICS.get(heuristic_name, self.HEURISTICS['manhattan'])
        self.heuristic_name = heuristic_name
        self.stats = {'nodes_explored': 0, 'nodes_generated': 0, 'time': 0}

    def pathfind(self, start, goal):
        start_time = time.time()

        pq = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        visited = set()

        while pq:
            _, current = heappop(pq)

            if current in visited:
                continue

            visited.add(current)
            self.stats['nodes_explored'] += 1

            if current == goal:
                self.stats['time'] = time.time() - start_time
                return self._build_path(came_from, start, goal)

            for neighbor in self._neighbors(current):
                if neighbor in visited:
                    continue

                new_g = g_score[current] + 1

                if neighbor not in g_score or new_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g
                    f = new_g + self.h_func(neighbor, goal)
                    heappush(pq, (f, neighbor))
                    self.stats['nodes_generated'] += 1

        self.stats['time'] = time.time() - start_time
        return None

    def _neighbors(self, pos):
        r, c = pos
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            nr, nc = r+dr, c+dc
            if (0 <= nr < len(self.grid) and
                0 <= nc < len(self.grid[0]) and
                self.grid[nr][nc] == 0):
                yield (nr, nc)

    def _build_path(self, came_from, start, goal):
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        return path[::-1]

    def print_stats(self):
        print(f"\n--- Statistics ({self.heuristic_name}) ---")
        print(f"Nodes explored: {self.stats['nodes_explored']}")
        print(f"Nodes generated: {self.stats['nodes_generated']}")
        print(f"Time: {self.stats['time']:.6f} seconds")

    def draw(self, path, start, goal):
        ps = set(path) if path else set()
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                p = (i, j)
                if p == start: c = 'S'
                elif p == goal: c = 'G'
                elif p in ps: c = '*'
                elif cell == 1: c = '#'
                else: c = '.'
                print(c, end=' ')
            print()

def compare_heuristics():
    """Compare different heuristics"""
    grid = [
        [0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,1,0],
        [0,0,1,1,1,0,0,0,0,0,1,0],
        [0,0,0,0,1,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0],
    ]

    start = (0, 0)
    goal = (7, 11)

    for h_name in ['manhattan', 'euclidean', 'chebyshev', 'octile']:
        print(f"\n{'='*50}")
        print(f"Testing with {h_name.upper()} heuristic")
        print('='*50)

        solver = MultiHeuristicAStar(grid, h_name)
        path = solver.pathfind(start, goal)

        if path:
            print(f"Path found! Length: {len(path)}")
            solver.draw(path, start, goal)
            solver.print_stats()
        else:
            print("No path found")

if __name__ == "__main__":
    compare_heuristics()
