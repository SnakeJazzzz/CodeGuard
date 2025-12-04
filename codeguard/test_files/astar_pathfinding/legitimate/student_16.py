"""
Recursive A* Implementation
Student 16 - Experimental Approach
"""

import sys
sys.setrecursionlimit(10000)

class RecursiveAStar:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.best_path = None
        self.best_cost = float('inf')

    def h(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def is_valid(self, pos):
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == 0

    def get_next_moves(self, pos):
        r, c = pos
        moves = []
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            new_pos = (r+dr, c+dc)
            if self.is_valid(new_pos):
                moves.append(new_pos)
        return moves

    def recursive_search(self, current, goal, visited, path, g_score):
        """Recursive A* exploration"""
        if current == goal:
            if g_score < self.best_cost:
                self.best_cost = g_score
                self.best_path = path.copy()
            return

        # Pruning: if current path already worse than best, stop
        if g_score >= self.best_cost:
            return

        # Get possible moves
        moves = self.get_next_moves(current)

        # Sort moves by heuristic (greedy selection)
        moves.sort(key=lambda m: self.h(m, goal))

        for next_pos in moves:
            if next_pos not in visited:
                visited.add(next_pos)
                path.append(next_pos)

                # Recursive call
                self.recursive_search(next_pos, goal, visited, path, g_score + 1)

                # Backtrack
                path.pop()
                visited.remove(next_pos)

    def find_path(self, start, goal):
        """Initialize and run recursive search"""
        visited = {start}
        path = [start]

        self.recursive_search(start, goal, visited, path, 0)

        return self.best_path

    def visualize(self, path, start, goal):
        if path:
            path_set = set(path)
        else:
            path_set = set()

        for r in range(self.rows):
            for c in range(self.cols):
                pos = (r, c)
                if pos == start:
                    print('S', end=' ')
                elif pos == goal:
                    print('G', end=' ')
                elif pos in path_set:
                    print('*', end=' ')
                elif self.grid[r][c] == 1:
                    print('#', end=' ')
                else:
                    print('.', end=' ')
            print()

# Test grid - smaller size for recursion
test_grid = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

pathfinder = RecursiveAStar(test_grid)

start = (0, 0)
goal = (6, 6)

print("Recursive A* Pathfinding")
print(f"Start: {start}, Goal: {goal}")
print("-" * 30)

result = pathfinder.find_path(start, goal)

if result:
    print(f"Path found! Length: {len(result)}")
    pathfinder.visualize(result, start, goal)
    print(f"\nPath: {result}")
else:
    print("No path found")
    pathfinder.visualize(None, start, goal)
